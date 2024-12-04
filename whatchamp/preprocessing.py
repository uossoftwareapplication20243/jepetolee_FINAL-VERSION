import pandas as pd
from sklearn.preprocessing import StandardScaler
import os

print("ready")

current_dir = os.path.dirname(os.path.abspath(__file__))

# 로컬 파일 경로를 사용하여 데이터 로드
raw_data = pd.read_excel(os.path.join(current_dir, 'feature.xlsx', header=1))
# print(raw_data)  # 데이터 확인

# 데이터 전처리 과정
columns_to_standardize = ['WinRate', 'Atks', 'Deff', 'Diff', 'PickRate', 'SkillCount', 'Mvs', 'Sps', 'CCs']
columns_to_remove = ['ByTop', 'ByJun', 'ByMid', 'ByADC', 'BySup', 'DetailRole', 'MainRole', 'SubRole']
roles = ['전사', '마법사', '암살자', '원거리딜러', '탱커', '서포터']

# 새로운 컬럼 생성
for role in roles:
    raw_data[role] = raw_data.apply(lambda row: 3.4 if role in [row['MainRole'], row['SubRole']] else 0, axis=1)

# 정규화
scaler = StandardScaler()
raw_data[columns_to_standardize] = scaler.fit_transform(raw_data[columns_to_standardize])

# 필요없는 컬럼 제거
standized_data = raw_data.drop(columns=columns_to_remove)

# 컬럼 재정렬
new_column_order = ['챔피언명', '한글명', '라인', '전사', '마법사', '암살자', '원거리딜러', '탱커', '서포터',
                    'WinRate', 'Atks', 'Deff', 'Diff', 'PickRate', 'SkillCount', 'Mvs', 'Sps', 'CCs', '전성기']
standized_data = standized_data[new_column_order]

# 전처리된 데이터를 새로운 Excel 파일로 저장 (로컬 경로 사용)
standized_data.to_excel(os.path.join(current_dir, 'StandardizedData.xlsx', index=False))

a = input("end")
