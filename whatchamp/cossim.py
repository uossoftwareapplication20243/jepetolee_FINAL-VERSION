import numpy as np
import pandas as pd
import json
import sys
import re
import io
import os

# stdin의 인코딩을 UTF-8로 재설정
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))

# StandardizedData.xlsx 파일 로드
standardized_data = pd.read_excel(os.path.join(current_dir, 'StandardizedData.xlsx'))

# 질문 응답 매핑 함수들 (q1_mapper, q2_mapper, ..., q7_mapper)
def q1_mapper(q1):
    result = [0, 0, 0, 0, 0, 0]
    job_dict = {
        '전사': 0,
        '마법사': 1,
        '암살자': 2,
        '원거리딜러': 3,
        '탱커': 4,
        '서포터': 5,
    }
    for job in q1:
        # 모든 공백 문자 및 특수 문자 제거
        job_cleaned = re.sub(r'\s+', '', job)
        if job_cleaned in job_dict:
            result[job_dict[job_cleaned]] = 4
        else:
            print(f"Warning: '{job}' after cleaning is not a recognized job type", file=sys.stderr)
    return result

def q2_mapper(q2):
    result = [0]
    if q2 == "이길 수 있는\n챔피언":
        result[0] = 2
    return result

def q3_mapper(q3, atk_max, def_max):
    if q3 == "공격적인\n챔피언":
        return [atk_max*2, 0]
    else:
        return [0, def_max*2]

def q4_mapper(q4, diff_max, diff_min):
    if q4 == "어렵지만 화려한\n챔피언":
        return [diff_max]
    else:
        return [diff_min]

def q5_mapper(q5):
    if q5 == "유니크한\n챔피언":
        return [-2]
    else:
        return [2]

def q6_mapper(q6, skill_max, skill_min):
    if q6 == "아뇨. 저한테만\n집중하고 싶어요":
        return [skill_max]
    else:
        return [skill_min]

def q7_mapper(q7, mvs_max, sps_max, ccs_max):
    if q7 == "일단 내가 잘해야 한다":
        return [mvs_max, 0, 0]
    else:
        return [0, sps_max, ccs_max]

# 사용자 프로파일 생성 함수
def list_user_profile(json_data, df):
    user_profile = []
    user_profile.extend(q1_mapper(json_data['q1']))
    user_profile.extend(q2_mapper(json_data['q2']))
    user_profile.extend(q3_mapper(json_data['q3'], df['Atks'].max(), df['Deff'].max()))
    user_profile.extend(q4_mapper(json_data['q4'], df['Diff'].max(), df['Diff'].min()))
    user_profile.extend(q5_mapper(json_data['q5']))
    user_profile.extend(q6_mapper(json_data['q6'], df['SkillCount'].max(), df['SkillCount'].min()))
    user_profile.extend(q7_mapper(json_data['q7'], df['Mvs'].max(), df['Sps'].max(), df['CCs'].max()))
    return user_profile

# 코사인 유사도 계산 함수
def cos_sim(item_profile, user_profile):
    magnitude_user = np.linalg.norm(user_profile)
    dot_product = np.dot(item_profile, user_profile)
    magnitude_items = np.linalg.norm(item_profile, axis=1)
    cosine_similarity = dot_product / (magnitude_items * magnitude_user + 1e-10)  # 0으로 나누는 것을 방지
    return cosine_similarity

def main():
    try:
        # JSON 데이터 직접 로드
        json_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        sys.exit(1)

    columns_to_drop = ['챔피언명', '한글명', '라인', '전성기']
    
    filtered_df = standardized_data
    # 서폿 챔피언만 필터링 (원본 인덱스 유지)
    if json_data['line'] != '상관없음':
        filtered_df = standardized_data[standardized_data['라인'] == json_data['line']].copy()
    
    # 필요한 열만 선택하고 NumPy 배열로 변환
    item_profile = filtered_df.drop(columns=columns_to_drop).to_numpy()
    
    # 사용자 프로파일 생성 (전체 데이터프레임 사용)
    user_profile = np.array(list_user_profile(json_data, standardized_data))
    
    # 코사인 유사도 계산
    similarity_scores = cos_sim(item_profile, user_profile)
    
    # 상위 3개의 챔피언 인덱스 추출 (필터링된 DataFrame의 인덱스를 기준으로 함)
    top_indices_relative = np.argsort(similarity_scores)[-5:][::-1]
    
    # 필터링된 DataFrame의 원본 인덱스를 가져옴
    top_indices_original = filtered_df.index[top_indices_relative].tolist()
    
    # 상위 3개의 챔피언명 추출
    top_champions = filtered_df.iloc[top_indices_relative][['한글명']].reset_index(drop=True)
    
    # 챔피언 정보를 JSON으로 출력
    response_data = {
        "message": "Data received successfully",
        "champions": top_champions['한글명'].tolist(),
	"championsNum": [int(idx) for idx in top_indices_original[:5]]
    }
        #"champ1_num": int(top_indices_original[0]),
        #"champ1_name": top_champions.loc[0, '챔피언명'],
        #"champ2_num": int(top_indices_original[1]),
        #"champ2_name": top_champions.loc[1, '챔피언명'],
        #"champ3_num": int(top_indices_original[2]),
        #"champ3_name": top_champions.loc[2, '챔피언명'],
    
    # ensure_ascii=False를 사용하여 한글이 제대로 출력되도록 함
    print(json.dumps(response_data, ensure_ascii=False))

if __name__ == "__main__":
    main()
