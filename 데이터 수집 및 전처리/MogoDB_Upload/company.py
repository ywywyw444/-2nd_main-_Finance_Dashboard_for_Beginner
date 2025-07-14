import pandas as pd
import json
import re

# 파일 불러오기
df = pd.read_excel('모든_기업_정리2.xlsx')

# 괄호 제거 등 컬럼 정제
def clean_column(col):
    return re.split(r'\(', col)[0].strip()

df.columns = [clean_column(c) for c in df.columns]

# 대상 지표
metrics = ['PER', 'PBR', 'ROE', 'DPS']

# 결과 저장용 dict
result = {}

for _, row in df.iterrows():
    company = row['기업명']
    if company not in result:
        result[company] = {}

    for metric in metrics:
        result[company][metric] = {}
        for year in ['2022', '2023', '2024']:
            col_name = f"{year}/12_{metric}"
            if col_name in df.columns:
                val = row[col_name]
                try:
                    result[company][metric][year] = round(float(val), 2)
                except:
                    result[company][metric][year] = None

# JSON 저장
with open("기업별재무지표.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("🎉 JSON 저장 완료: 기업별_재무지표.json")
