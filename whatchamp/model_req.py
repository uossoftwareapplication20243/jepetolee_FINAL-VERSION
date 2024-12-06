import pandas as pd
import sys
import io
import os
import time
import requests
from urllib import parse
from dotenv import load_dotenv
import torch
import torch.nn as nn
import numpy as np
from torchdiffeq import odeint
import scipy.sparse as sp

index_to_champion_name = {136: 'Aatrox', 86: 'Ahri', 74: 'Akali', 119: 'Akshan', 11: 'Alistar', 157: 'Ambessa', 31: 'Amumu', 33: 'Anivia',
                          0: 'Annie', 152: 'Aphelios', 21: 'Ashe', 107: 'Aurelion Sol', 162: 'Aurora', 138: 'Azir', 146: 'Bard', 120: "Bel'Veth",
                          48: 'Blitzcrank', 58: 'Brand', 121: 'Braum', 127: 'Briar', 47: 'Caitlyn', 118: 'Camille', 62: 'Cassiopeia', 30: "Cho'Gath",
                          41: 'Corki', 101: 'Darius', 104: 'Diana', 98: 'Draven', 35: 'Dr. Mundo', 133: 'Ekko', 55: 'Elise', 27: 'Evelynn', 71: 'Ezreal',
                          8: 'Fiddlesticks', 95: 'Fiora', 88: 'Fizz', 2: 'Galio', 40: 'Gangplank', 76: 'Garen', 113: 'Gnar', 69: 'Gragas', 87: 'Graves',
                          160: 'Gwen', 99: 'Hecarim', 64: 'Heimerdinger', 167: 'Hwei', 142: 'Illaoi', 38: 'Irelia', 144: 'Ivern', 39: 'Janna', 54: 'Jarvan IV',
                          23: 'Jax', 102: 'Jayce', 122: 'Jhin', 125: 'Jinx', 111: "Kai'Sa", 145: 'Kalista', 42: 'Karma', 29: 'Karthus', 37: 'Kassadin', 50: 'Katarina',
                          9: 'Kayle', 108: 'Kayn', 75: 'Kennen', 100: "Kha'Zix", 123: 'Kindred', 132: 'Kled', 81: "Kog'Maw", 164: "K'Sante", 6: 'LeBlanc', 59: 'Lee Sin',
                          77: 'Leona', 159: 'Lillia', 103: 'Lissandra', 130: 'Lucian', 97: 'Lulu', 83: 'Lux', 49: 'Malphite', 78: 'Malzahar', 52: 'Maokai', 10: 'Master Yi',
                          166: 'Milio', 20: 'Miss Fortune', 57: 'Wukong', 72: 'Mordekaiser', 24: 'Morgana', 168: 'Naafiri', 137: 'Nami', 65: 'Nasus', 92: 'Nautilus',
                          151: 'Neeko', 66: 'Nidalee', 163: 'Nilah', 51: 'Nocturne', 19: 'Nunu & Willump', 1: 'Olaf', 56: 'Orianna', 149: 'Ornn', 70: 'Pantheon',
                          68: 'Poppy', 154: 'Pyke', 134: 'Qiyana', 105: 'Quinn', 147: 'Rakan', 32: 'Rammus', 143: "Rek'Sai", 153: 'Rell', 161: 'Renata Glasc', 53: 'Renekton',
                          90: 'Rengar', 80: 'Riven', 61: 'Rumble', 12: 'Ryze', 140: 'Samira', 94: 'Sejuani', 129: 'Senna', 112: 'Seraphine', 158: 'Sett', 34: 'Shaco',
                          82: 'Shen', 85: 'Shyvana', 26: 'Singed', 13: 'Sion', 14: 'Sivir', 63: 'Skarner', 165: 'Smolder', 36: 'Sona', 15: 'Soraka', 46: 'Swain',
                          150: 'Sylas', 106: 'Syndra', 126: 'Tahm Kench', 117: 'Taliyah', 79: 'Talon', 43: 'Taric', 16: 'Teemo', 141: 'Thresh', 17: 'Tristana',
                          45: 'Trundle', 22: 'Tryndamere', 3: 'Twisted Fate', 28: 'Twitch', 67: 'Udyr', 5: 'Urgot', 91: 'Varus', 60: 'Vayne', 44: 'Veigar', 116: "Vel'Koz",
                          155: 'Vex', 135: 'Vi', 128: 'Viego', 93: 'Viktor', 7: 'Vladimir', 89: 'Volibear', 18: 'Warwick', 148: 'Xayah', 84: 'Xerath', 4: 'Xin Zhao',
                          115: 'Yasuo', 156: 'Yone', 73: 'Yorick', 139: 'Yuumi', 114: 'Zac', 131: 'Zed', 124: 'Zeri', 96: 'Ziggs', 25: 'Zilean', 109: 'Zoe', 110: 'Zyra'}

champion_translation = {
    'Aatrox': '아트록스', 'Ahri': '아리', 'Akali': '아칼리', 'Akshan': '아크샨', 'Alistar': '알리스타',
    'Ambessa': '암베사', 'Amumu': '아무무', 'Anivia': '애니비아', 'Annie': '애니', 'Aphelios': '아펠리오스',
    'Ashe': '애쉬', 'Aurelion Sol': '아우렐리온 솔', 'Aurora': '오로라', 'Azir': '아지르', 'Bard': '바드',
    "Bel'Veth": '벨베스', 'Blitzcrank': '블리츠크랭크', 'Brand': '브랜드', 'Braum': '브라움', 'Briar': '브라이어',
    'Caitlyn': '케이틀린', 'Camille': '카밀', 'Cassiopeia': '카시오페아', "Cho'Gath": '초가스', 'Corki': '코르키',
    'Darius': '다리우스', 'Diana': '다이애나', 'Draven': '드레이븐', 'Dr. Mundo': '문도 박사', 'Ekko': '에코',
    'Elise': '엘리스', 'Evelynn': '이블린', 'Ezreal': '이즈리얼', 'Fiddlesticks': '피들스틱', 'Fiora': '피오라',
    'Fizz': '피즈', 'Galio': '갈리오', 'Gangplank': '갱플랭크', 'Garen': '가렌', 'Gnar': '나르',
    'Gragas': '그라가스', 'Graves': '그레이브즈', 'Gwen': '그웬', 'Hecarim': '헤카림', 'Heimerdinger': '하이머딩거',
    'Hwei': '흐웨이', 'Illaoi': '일라오이', 'Irelia': '이렐리아', 'Ivern': '아이번', 'Janna': '잔나',
    'Jarvan IV': '자르반 4세', 'Jax': '잭스', 'Jayce': '제이스', 'Jhin': '진', 'Jinx': '징크스',
    "Kai'Sa": '카이사', 'Kalista': '칼리스타', 'Karma': '카르마', 'Karthus': '카서스', 'Kassadin': '카사딘',
    'Katarina': '카타리나', 'Kayle': '케일', 'Kayn': '케인', 'Kennen': '케넨', "Kha'Zix": '카직스',
    'Kindred': '킨드레드', 'Kled': '클레드', "Kog'Maw": '코그모', "K'Sante": '크샨테', 'LeBlanc': '르블랑',
    'Lee Sin': '리 신', 'Leona': '레오나', 'Lillia': '릴리아', 'Lissandra': '리산드라', 'Lucian': '루시안',
    'Lulu': '룰루', 'Lux': '럭스', 'Malphite': '말파이트', 'Malzahar': '말자하', 'Maokai': '마오카이',
    'Master Yi': '마스터 이', 'Milio': '밀리오', 'Miss Fortune': '미스 포츈', 'Wukong': '오공', 'Mordekaiser': '모데카이저',
    'Morgana': '모르가나', 'Naafiri': '나피리', 'Nami': '나미', 'Nasus': '나서스', 'Nautilus': '노틸러스',
    'Neeko': '니코', 'Nidalee': '니달리', 'Nilah': '닐라', 'Nocturne': '녹턴', 'Nunu & Willump': '누누와 윌럼프',
    'Olaf': '올라프', 'Orianna': '오리아나', 'Ornn': '오른', 'Pantheon': '판테온', 'Poppy': '뽀삐',
    'Pyke': '파이크', 'Qiyana': '키아나', 'Quinn': '퀸', 'Rakan': '라칸', 'Rammus': '람머스',
    "Rek'Sai": '렉사이', 'Rell': '렐', 'Renata Glasc': '레나타 글라스크', 'Renekton': '레넥톤', 'Rengar': '렝가',
    'Riven': '리븐', 'Rumble': '럼블', 'Ryze': '라이즈', 'Samira': '사미라', 'Sejuani': '세주아니',
    'Senna': '세나', 'Seraphine': '세라핀', 'Sett': '세트', 'Shaco': '샤코', 'Shen': '쉔',
    'Shyvana': '쉬바나', 'Singed': '신지드', 'Sion': '사이온', 'Sivir': '시비르', 'Skarner': '스카너',
    'Smolder': '스몰더', 'Sona': '소나', 'Soraka': '소라카', 'Swain': '스웨인', 'Sylas': '사일러스',
    'Syndra': '신드라', 'Tahm Kench': '탐 켄치', 'Taliyah': '탈리야', 'Talon': '탈론', 'Taric': '타릭',
    'Teemo': '티모', 'Thresh': '쓰레쉬', 'Tristana': '트리스타나', 'Trundle': '트런들', 'Tryndamere': '트린다미어',
    'Twisted Fate': '트위스티드 페이트', 'Twitch': '트위치', 'Udyr': '우디르', 'Urgot': '우르곳', 'Varus': '바루스',
    'Vayne': '베인', 'Veigar': '베이가', "Vel'Koz": '벨코즈', 'Vex': '벡스', 'Vi': '바이',
    'Viego': '비에고', 'Viktor': '빅토르', 'Vladimir': '블라디미르', 'Volibear': '볼리베어', 'Warwick': '워윅',
    'Xayah': '자야', 'Xerath': '제라스', 'Xin Zhao': '신 짜오', 'Yasuo': '야스오', 'Yone': '요네',
    'Yorick': '요릭', 'Yuumi': '유미', 'Zac': '자크', 'Zed': '제드', 'Zeri': '제리',
    'Ziggs': '직스', 'Zilean': '질리언', 'Zoe': '조이', 'Zyra': '자이라'
}

print(len(champion_translation))
champion_name_to_index = {name: index for index, name in index_to_champion_name.items()}

def convert_champions_to_indices(champions_list, mapping):
    return [mapping.get(champion, -1) for champion in champions_list]

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

    english_name = index_to_champion_name.get(index, None)
    if not english_name:
        return "해당 챔피언을 찾을 수 없습니다."

    # 영어 이름을 한국어 이름으로 변환
    korean_name = champion_translation.get(english_name, "해당 챔피언의 한글 이름이 없습니다.")
    return korean_name



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
def get_match_ids(puuid, count=2):
    match_ids = []
    headers = {
        'X-Riot-Token': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for idx in range(count):
        time.sleep(0.2)
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
    time.sleep(0.2)
    response = requests.get(match_detail_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match details for {match_id}: {response.status_code}")
        return None

def create_binary_array(champion_indices, total_champions=169):
    binary_array = np.zeros((1, total_champions), dtype=int)
    for index in champion_indices:
        binary_array[0, index] = 1
    return binary_array

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

    total_games_played = sum(stats['games_played'] for stats in champion_stats.values())

    champion_list = []
    for champion, stats in champion_stats.items():
        games_played = stats['games_played']
        wins = stats['wins']
        win_rate = (wins / games_played) * 100 if games_played > 0 else 0
        pick_rate = (games_played / total_games_played) * 100 if total_games_played > 0 else 0
        champion_list.append({
            'Champion': champion,
            'GamesPlayed': games_played,
            'Wins': wins,
            'WinRate': win_rate,
            'PickRate': pick_rate
        })

    champion_list = pd.DataFrame(champion_list)
    filtered_stats = champion_list[champion_list['GamesPlayed'] >= 10]

    user_champion_stats_winrate = filtered_stats[filtered_stats['WinRate'] > 50]
    user_champion_stats_winrate = user_champion_stats_winrate.sort_values(by=['WinRate'], ascending=[False])
    user_champion_grouped_winrate = user_champion_stats_winrate['Champion'].apply(list).reset_index()
    user_champion_grouped_winrate.rename(columns={'Champion': 'WinRate_Sorted_Champions'}, inplace=True)

    user_champion_stats_pickrate = filtered_stats[filtered_stats['PickRate'] > 7.5]
    user_champion_stats_pickrate = user_champion_stats_pickrate.sort_values(by=['PickRate'], ascending=[False])
    user_champion_grouped_pickrate = user_champion_stats_pickrate['Champion'].apply(list).reset_index()
    user_champion_grouped_pickrate.rename(columns={'Champion': 'PickRate_Sorted_Champions'}, inplace=True)

    user_champion_grouped = pd.merge(user_champion_grouped_winrate, user_champion_grouped_pickrate)

    user_champion_grouped['WinRate_Sorted_Champions'] = user_champion_grouped['WinRate_Sorted_Champions'].apply(
        lambda champions: [champion_name_to_index.get(champion, -1) for champion in champions]
        )

    user_champion_grouped['PickRate_Sorted_Champions'] = user_champion_grouped['PickRate_Sorted_Champions'].apply(
                lambda champions: [champion_name_to_index.get(champion, -1) for champion in champions]
                )

    user_champion_indices_win = [
                index for indices in user_champion_grouped['WinRate_Sorted_Champions'] for index in indices if index >= 0
                ]
    winrate_array = create_binary_array(user_champion_indices_win, total_champions=169)

    user_champion_indices_pick = [
                index for indices in user_champion_grouped['PickRate_Sorted_Champions'] for index in indices if index >= 0
                ]
    pickrate_array = create_binary_array(user_champion_indices_pick, total_champions=169)

    return winrate_array,pickrate_array

# 유저 ID 입력 및 처리



class BSPM(object):
    def __init__(self, adj_mat):
        self.adj_mat = adj_mat

        self.idl_solver = 'euler'
        self.blur_solver = 'euler'
        self.sharpen_solver = 'rk4'

        self.idl_beta = 0.2
        self.factor_dim = 448

        idl_T = 1
        idl_K = 1

        blur_T = 1
        blur_K = 1

        sharpen_T = 4
        sharpen_K = 1

        self.device = 'cuda'
        self.idl_times = torch.linspace(0, idl_T, idl_K + 1).float().to(self.device)
        self.blurring_times = torch.linspace(0, blur_T, blur_K + 1).float().to(self.device)
        self.sharpening_times = torch.linspace(0, sharpen_T, sharpen_K + 1).float().to(self.device)

        self.final_sharpening = True

    def train(self):
        adj_mat = self.adj_mat
        rowsum = np.array(adj_mat.sum(axis=1))
        d_inv = np.power(rowsum, -0.5, where=rowsum != 0).flatten()
        d_inv[np.isinf(d_inv)] = 0.
        d_mat = sp.diags(d_inv)
        norm_adj = d_mat.dot(adj_mat)

        colsum = np.array(adj_mat.sum(axis=0))
        d_inv = np.power(colsum, -0.5, where=colsum != 0).flatten()
        d_inv[np.isinf(d_inv)] = 0.
        d_mat = sp.diags(d_inv)

        self.d_mat_i = d_mat

        self.d_mat_i_inv = sp.diags(1 / d_inv, 0)
        norm_adj = norm_adj.dot(d_mat)
        self.norm_adj = norm_adj.tocsc()
        del norm_adj, d_mat

        linear_Filter = self.norm_adj.T @ self.norm_adj
        self.linear_Filter = self.convert_sp_mat_to_sp_tensor(linear_Filter).to_dense().to(self.device)



    def sharpenFunction(self, t, r):
        out = r @ self.linear_Filter
        return -out


    def getUsersRating(self, batch_users):
        batch_test = batch_users.to_sparse()

        with torch.no_grad():

            blurred_out = torch.mm(batch_test.to_dense(), self.linear_Filter)
            if self.final_sharpening == True:  # EM
                sharpened_out = odeint(func=self.sharpenFunction, y0=blurred_out, t=self.sharpening_times, method=self.sharpen_solver)

        U_2 = sharpened_out[-1]
        ret = U_2
        return ret

    def convert_sp_mat_to_sp_tensor(self, X):
        # X가 이미 PyTorch Tensor라면 변환 작업 필요 없음
        if isinstance(X, torch.Tensor):
            if X.is_sparse:
                return X  # 이미 희소 텐서라면 반환
            else:
                raise ValueError("Input is a dense tensor, expected a sparse matrix.")

        # X가 SciPy 희소 행렬인지 확인
        if sp.issparse(X):
            coo = X.tocoo().astype(np.float32)
            row = torch.Tensor(coo.row).long()
            col = torch.Tensor(coo.col).long()
            index = torch.stack([row, col])
            data = torch.FloatTensor(coo.data)
            return torch.sparse_coo_tensor(index, data, torch.Size(coo.shape))

        raise TypeError("Input must be a PyTorch sparse tensor or a SciPy sparse matrix.")

    
def get_champions_name(summoner_name, tag):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"

    print(API_KEY)
    headers = {
        "X-Riot-Token": API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        summoner_id = response.json()['puuid']
        new_win_array,new_pick_array = calculate_champion_stats(summoner_id)
        train_mat_win = np.load('./train_mat_win.npy', allow_pickle=True)
        train_mat_pick = np.load('./train_mat_pick.npy', allow_pickle=True)

        train_mat_win = sp.dok_matrix(np.vstack((train_mat_win, new_win_array)))  # 5013x169
        train_mat_pick = sp.dok_matrix(np.vstack((train_mat_pick, new_pick_array)))  # 5013x169

        model_win = BSPM(train_mat_win)
        model_win.train()
        model_pick = BSPM(train_mat_pick)
        model_pick.train()


        adj_mat_win = model_win.convert_sp_mat_to_sp_tensor(train_mat_win)
        adj_mat_win = adj_mat_win.to_dense()
        batch_ratings = adj_mat_win[5012, :].to('cuda').reshape(-1,169)
        indices_to_mask = np.where(new_win_array[0] == 1)[0]  # 값이 1인 인덱스 추출
        indices_to_mask_tensor = torch.tensor(indices_to_mask, dtype=torch.long)  # torch.Tensor로 변환


        rating_win = model_win.getUsersRating(batch_ratings)
        # 해당 인덱스를 마스킹 (0으로 설정)
        rating_win[0, indices_to_mask_tensor] = 0

        _, top_k_win = torch.topk(rating_win, 30)

        adj_mat_pick = model_pick.convert_sp_mat_to_sp_tensor(train_mat_pick)
        adj_mat_pick = adj_mat_pick.to_dense()
        batch_ratings = adj_mat_pick[5012, :].to('cuda').reshape(-1,169)
        indices_to_mask = np.where(new_pick_array[0] == 1)[0]  # 값이 1인 인덱스 추출
        indices_to_mask_tensor = torch.tensor(indices_to_mask, dtype=torch.long)  # torch.Tensor로 변환

        rating_pick = model_win.getUsersRating(batch_ratings)
        # 해당 인덱스를 마스킹 (0으로 설정)
        rating_pick[0, indices_to_mask_tensor] = 0

        _, top_k_pick = torch.topk(rating_pick, 30)

        top_k_pick_indices = top_k_pick[0].tolist()
        top_k_win_indices = top_k_win[0].tolist()
        common_indices = list(set(top_k_pick_indices) & set(top_k_win_indices))

        ranked_indices = sorted(
            common_indices,
            key=lambda idx: (top_k_pick_indices.index(idx) + top_k_win_indices.index(idx))
        )

        top_k = ranked_indices[:5]

        return {
            "message": "Data received successfully",
            "champions": list(map(lambda idx: get_champion_name_by_index(idx), top_k))
        }
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)
        return {"error": "Rate limit exceeded. Please try again later."}, 429
    else:
        return {"error": f"Failed to fetch data from Riot API. Status code: {response.status_code}"}, response.status_code



'''
import time

# 시작 시간
start_time = time.time()
print(get_champions_name('괴물쥐', 'KR3'))
end_time = time.time()

# 경과 시간 계산
elapsed_time = end_time - start_time
print(f"경과 시간: {elapsed_time:.2f}초")
'''

