import pandas as pd
import numpy as np
import re
import json

# ===== [1] 엑셀 불러오기 =====
df = pd.read_excel("모든_기업_정리2.xlsx")

# ===== [2] 칼럼 이름 정리 =====
def clean_column(col):
    return re.split(r'\(', col)[0].strip()

df.columns = [clean_column(col) for col in df.columns]

# ===== [3] 사용할 지표 설정 =====
target_metrics = ['PER', 'PBR', 'ROE', 'DPS']
years = ['2022', '2023', '2024']

# ===== [4] 업종별 평균 계산 =====
industry_group = df.groupby("업종명")
industry_summary = {}

for industry, group in industry_group:
    metric_data = {}

    for metric in target_metrics:
        values = []

        for year in years:
            col_name = f"{year}/12_{metric}"
            if col_name in group.columns:
                # 이상치 제거 + 평균
                col_data = pd.to_numeric(group[col_name], errors='coerce')
                col_data = col_data.replace([np.inf, -np.inf], np.nan).dropna()

                # IQR 기반 이상치 제거
                if len(col_data) > 3:
                    q1 = col_data.quantile(0.25)
                    q3 = col_data.quantile(0.75)
                    iqr = q3 - q1
                    col_data = col_data[(col_data >= q1 - 1.5 * iqr) & (col_data <= q3 + 1.5 * iqr)]

                if len(col_data) > 0:
                    values.append(round(col_data.mean(), 2))
                else:
                    values.append(None)
            else:
                values.append(None)

        metric_data[metric] = {
            "2022": values[0],
            "2023": values[1],
            "2024": values[2]
        }

    industry_summary[industry] = metric_data

# ===== [5] JSON 저장 =====
with open("업종별_지표요약.json", "w", encoding="utf-8") as f:
    json.dump(industry_summary, f, ensure_ascii=False, indent=2)

print("✅ 업종별 평균 지표가 '업종별_지표_요약.json'으로 저장되었습니다!")
