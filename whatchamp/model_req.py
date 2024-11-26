import pandas as pd
import sys
import io
import os
import time
import requests
from urllib import parse
from transformers import DistilBertTokenizer, DistilBertModel
from dotenv import load_dotenv
import torch
import torch.nn as nn


load_dotenv()
# stdin의 인코딩을 UTF-8로 재설정
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
# 로컬 파일 경로를 사용하여 데이터 로드
feature = pd.read_excel(os.path.join(current_dir, 'feature.xlsx'), header=1)

API_KEY = os.getenv("RIOT_API_KEY")  # Riot API 키
REGION = 'kr'  # 한국 서버

def get_champion_name_by_index(index):
    """
    주어진 행 번호로 엑셀에서 해당하는 챔피언의 한글명을 가져옵니다.
    """
    if 0 <= int(index) < len(feature):
        return feature.iloc[index][1]
    else:
        return "해당 챔피언을 찾을 수 없습니다."

# 아이템 정보 가져오기
def get_item_names():
    item_url = 'https://ddragon.leagueoflegends.com/cdn/14.18.1/data/ko_KR/item.json'
    response = requests.get(item_url)
    if response.status_code == 200:
        items_data = response.json()
        return items_data
    else:
        print("아이템 정보를 가져오는 데 실패했습니다.")
        return {}

# PUUID 가져오기
def get_puuid(summoner_name):
    summoner_name = parse.quote(summoner_name)
    summoner_url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summoner_name}'
    
    headers = {
        'X-Riot-Token': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(summoner_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('puuid')
    else:
        print(f"Error fetching summoner data for {summoner_name}: {response.status_code}")
        return None

# 최근 게임 리스트 가져오기
def get_match_ids(puuid, count=5):
    match_ids = []
    headers = {
        'X-Riot-Token': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for idx in range(count):
        time.sleep(1)
        match_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={idx * 20}&count=20'
        response = requests.get(match_url, headers=headers)
        while response.status_code != 200:
            print(f"Error {response.status_code}, retrying in 80 seconds...")
            time.sleep(80)
            response = requests.get(match_url, headers=headers)
        match_ids.extend(response.json())
    return match_ids

# 게임 상세 정보 가져오기
def get_match_details(match_id):
    headers = {
        'X-Riot-Token': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    match_detail_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}'
    time.sleep(1.22)
    response = requests.get(match_detail_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match details for {match_id}: {response.status_code}")
        return None

# 유저의 챔피언 픽률과 승률 계산
def calculate_champion_stats(summoner_id):
    puuid = get_puuid(summoner_id)
    if not puuid:
        return []

    match_ids = get_match_ids(puuid)
    champion_stats = {}

    for match_id in match_ids:
        match_detail = get_match_details(match_id)
        if match_detail:
            participants = match_detail['info']['participants']
            for participant in participants:
                if participant['puuid'] == puuid:
                    champion_name = participant['championName']
                    win = participant['win']
                    if champion_name not in champion_stats:
                        champion_stats[champion_name] = {'games_played': 0, 'wins': 0}
                    champion_stats[champion_name]['games_played'] += 1
                    if win:
                        champion_stats[champion_name]['wins'] += 1
                    break

    champion_list = []
    for champion, stats in champion_stats.items():
        games_played = stats['games_played']
        wins = stats['wins']
        win_rate = (wins / games_played) * 100 if games_played > 0 else 0
        champion_list.append({
            'Champion': champion,
            'GamesPlayed': games_played,
            'Wins': wins,
            'WinRate': win_rate
        })

    return champion_list

# 결과 출력 및 CSV 파일로 저장
def print_champion_stats(summoner_name):
    champion_list = calculate_champion_stats(summoner_name)
    if champion_list:
        result_text = "\n".join([
            f"Champion: {champion['Champion']}, Games Played: {champion['GamesPlayed']}, Wins: {champion['Wins']}, Win Rate: {champion['WinRate']:.2f}%"
            for champion in champion_list
        ])
        return result_text
    else:
        print("데이터가 없습니다.")

# 유저 ID 입력 및 처리




class UltraGCNWithDistilBERT(nn.Module):
    def __init__(self,):
        super(UltraGCNWithDistilBERT, self).__init__()
        self.item_num = 169
        self.embedding_dim = 768
        self.w1 = 1e-8
        self.w2 = 1
        self.w3 = 1
        self.w4 = 1e-8

        self.negative_weight = 500
        self.gamma = 1e-4
        self.lambda_ = 2.75

        # DistilBERT 모델과 토크나이저 초기화
        self.bert_model = DistilBertModel.from_pretrained('distilbert-base-uncased')
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

        self.item_embeds = nn.Embedding(self.item_num, self.embedding_dim)


        self.initial_weight = 1e-4
        self.initial_weights()

    def initial_weights(self):
        nn.init.normal_(self.item_embeds.weight, std=self.initial_weight)
    
    def get_user_embeddings(self, user_texts):
        tokens = self.tokenizer(user_texts, padding=True, truncation=True, return_tensors="pt")
        user_embeddings = self.bert_model(**tokens).last_hidden_state[:, 0, :]
        return user_embeddings
    
    def test_foward(self, user_texts):
        items = torch.arange(self.item_num)
        user_embeds = self.get_user_embeddings(user_texts)
        item_embeds = self.item_embeds(items)

        return user_embeds.mm(item_embeds.t())

    
def get_champions_name(summoner_name, tag):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"

    # 헤더에 API 키 추가
    headers = {
        "X-Riot-Token": API_KEY
    }

    # API 요청
    response = requests.get(url, headers=headers)

    # 요청이 성공했을 경우
    if response.status_code == 200:
        user_id = response.json()['puuid']
        # return summoner_data
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # 'Retry-After' 헤더 값(초) 가져오기
        print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)  # 지정된 시간만큼 대기
  
    model = UltraGCNWithDistilBERT()
    out = model.test_foward(print_champion_stats(user_id))
    _,top_k  =  torch.topk(out,3)
    return  {
        "message": "Data received successfully",
        "champions":  list(map(lambda idx: get_champion_name_by_index(idx), top_k[0].tolist()))
        }




