import pandas as pd
import numpy as np
from pymongo import MongoClient

# 엑셀 로드
df = pd.read_excel("전처리_기업_데이터.xlsx")

# 컬럼 정리
df.columns = df.columns.str.strip()

# 지표 컬럼만 숫자 처리
meta_cols = ["종목코드", "업종명", "기업명"]
indicator_cols = [col for col in df.columns if col not in meta_cols]

# 숫자로 변환, 에러 시 NaN → 0
df[indicator_cols] = df[indicator_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

# MongoDB 연결
client = MongoClient("")
collection = client["testDB"]["users"]

# 전체 업로드
docs = []
for _, row in df.iterrows():
    doc = {
        "종목코드": int(row["종목코드"]),
        "업종명": row["업종명"],
        "기업명": row["기업명"],
        "지표": {k: float(row[k]) for k in indicator_cols}
    }
    docs.append(doc)

collection.insert_many(docs)
