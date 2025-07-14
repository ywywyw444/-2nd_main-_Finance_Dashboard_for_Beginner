import pandas as pd
import json
import os

# 데이터 불러오기
file_path = '코스피_주주구분현황_전체.csv'
df = pd.read_csv(file_path)

# 숫자형 변환
df['대표 주주수'] = pd.to_numeric(df['대표 주주수'], errors='coerce')
df['지분율'] = pd.to_numeric(df['지분율'], errors='coerce')
df_clean = df.dropna(subset=['대표 주주수', '지분율'])

# JSON 저장용 딕셔너리 생성
result = {}

for code in df_clean['종목코드'].unique():
    df_target = df_clean[df_clean['종목코드'] == code]
    if df_target.empty:
        continue

    result[str(code)] = [
        {
            "주주구분": row["주주구분"],
            "지분율": round(row["지분율"], 2),
            "대표주주수": int(row["대표 주주수"])
        }
        for _, row in df_target.iterrows()
    ]

# 저장 경로
output_path = '지분현황.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ JSON 저장 완료: {output_path}")
