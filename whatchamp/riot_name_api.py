import time
from dotenv import load_dotenv
import requests
import os
import json
import sys
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
def get_match_history(puuid: str,  count=100):
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

def validate_environment():
    if not API_KEY:
        handle_error("Missing Riot API Key in environment variables", code=500)

def validate_input(json_data):
    if not json_data.get("username") or not json_data.get("tag"):
        handle_error("Invalid input: 'username' and 'tag' are required", code=400)

def handle_error(message, code=None):
    response = {"error": message}
    if code:
        response["code"] = code
    print(json.dumps(response), file=sys.stderr)
    sys.exit(1)

def log_debug(message):
    with open("riot_name_api_debug.log", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


def checking_response(summoner_name, tag):
    try:

        validate_environment()

        summoner_info = get_summoner_info(summoner_name, tag)
        if not summoner_info:
            handle_error("Summoner info not found or API request failed" + str(summoner_name) + str(tag), code=404)

        puuid = summoner_info.get("puuid")
        if not puuid:
            handle_error("Summoner PUUID not found in response", code=404)

        match_history = get_match_history(puuid, count=100)
        if match_history is None:
            handle_error("Failed to fetch match history", code=500)

        response = {"match_count": len(match_history), "success": True}
        log_debug(f"Output JSON: {response}")
        return response
    except json.JSONDecodeError as e:
        handle_error(f"JSON decode error: {str(e)}", code=400)
        return {"match_count": 0, "success": False}
    except Exception as e:
        handle_error(f"Unexpected error: {str(e)}", code=500)
        return {"match_count": 0, "success": False}