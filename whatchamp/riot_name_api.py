import time
from dotenv import load_dotenv
import requests
import os
import json
import sys
import re
import io
# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 불러오기
API_KEY = os.getenv("RIOT_API_KEY")

# stdin의 인코딩을 UTF-8로 재설정
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')


# 소환사 정보를 가져오는 함수
def get_summoner_info(summoner_name: str, tag: str):
    # 엔드포인트 URL 설정 (소환사 이름으로 검색)
    # region = tag.lower()  # 태그에 해당하는 지역을 소문자로 변환
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"

    # 헤더에 API 키 추가
    headers = {
        "X-Riot-Token": API_KEY
    }

    # API 요청
    response = requests.get(url, headers=headers)

    # 요청이 성공했을 경우
    if response.status_code == 200:
        summoner_data = response.json()
        return summoner_data
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # 'Retry-After' 헤더 값(초) 가져오기
        print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)  # 지정된 시간만큼 대기
    else:
        # 요청 실패시 에러 메시지 출력
        print(f"Error: {response.status_code}")
        return None

# 매치 리스트를 가져오는 함수
def get_match_history(puuid: str, region: str, count=100):
    match_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime=1715731200&start=0&count={count}"
    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(match_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # 'Retry-After' 헤더 값(초) 가져오기
        print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)  # 지정된 시간만큼 대기
    else:
        print(f"Error fetching match history: {response.status_code}")
        return None

# 매치 세부 정보를 가져오는 함수
def get_match_details(match_id: str, region: str):
    match_detail_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(match_detail_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # 'Retry-After' 헤더 값(초) 가져오기
        print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)  # 지정된 시간만큼 대기
    else:
        print(f"Error fetching match details: {response.status_code}")
        return None

def main():
    try:
        # JSON 데이터 직접 로드
        json_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)


    # 소환사 닉네임과 태그 입력 받기
    summoner_name = json_data["username"]
    tag = json_data["tag"]

    # 소환사 정보 가져오기
    summoner_info = get_summoner_info(summoner_name, tag)
    region = 'asia'

    # 결과 출력
    if summoner_info:
        # print(f"소환사 이름: {summoner_info['puuid']}")
        # print(f"소환사 레벨: {summoner_info['gameName']}")
        # print(f"소환사 아이디: {summoner_info['tagLine']}")

        # print(summoner_info)
        puuid = summoner_info['puuid']
        
        # 모든 게임 기록 가져오기 (최대 20개의 기록을 가져옴)
        match_history = get_match_history(puuid, region, count=100)

        print(json.dumps(len(match_history), ensure_ascii=False))
        
        # if match_history:
        #     filtered_matches = []
            
        #     for match_id in match_history:
        #         match_details = get_match_details(match_id, region)
        #         if match_details:
        #             queue_id = match_details['info']['queueId']
                    
        #             # 큐 ID가 450이 아닌 게임만 필터링 (칼바람 나락 제외)
        #             if (queue_id == 420 or queue_id == 430 or queue_id == 440):
        #                 filtered_matches.append(match_details)
            
        #     # 필터링된 게임 기록 출력
        #     if filtered_matches:
        #         print(f"칼바람 나락 제외된 최근 {len(filtered_matches)}개의 게임 기록:")
            
        #         for match in filtered_matches:
        #             for participant in match['info']['participants']:
        #                 if participant['puuid'] == puuid:
        #                     print(f"{participant['summonerName']} used {participant['championName']}")
        #                     # break
        #             # print(f"매치 ID: {match['metadata']['matchId']}, 큐 ID: {match['info']['queueId']}")
        #     else:
        #         print("칼바람 나락을 제외한 게임 기록이 없습니다.")

            
            # if(len(filtered_matches) >= 10):
            #     # 콜라보레이트 필터링 수행


if __name__ == "__main__":
    main()
