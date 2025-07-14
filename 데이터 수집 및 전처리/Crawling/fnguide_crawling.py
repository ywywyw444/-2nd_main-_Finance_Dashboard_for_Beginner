from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
from collections import Counter

df = pd.read_excel(r'D:\bit_esg\python\project 2\DART_재무_코스피전체_2024기준 (1).xlsx')
df['종목코드'] = df['종목코드'].apply(lambda x: f"A{x:06d}")
kospi_df = df[['종목명', '종목코드']].reset_index(drop=True)

# Selenium 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

output_file = "financial_highlight_all_by_sheet.xlsx"
failed_list = []
sheet_data = {}  # {기업명: DataFrame}

for idx in range(len(kospi_df)):  # ✅ 전체 기업 반복
    name = kospi_df.loc[idx, '종목명']
    code = kospi_df.loc[idx, '종목코드']
    print(f"▶ [{idx+1}/{len(kospi_df)}] {name} 처리 중...")

    try:
        url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"
        driver.get(url)
        time.sleep(1.5)

        # 연간 탭 클릭
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, '.gbtn_c.r3.ac')
            for b in buttons:
                if '연간' in b.text.strip():
                    b.click()
                    time.sleep(1.2)
                    break
        except Exception as e:
            print(f"❌ 연간 탭 클릭 실패: {e}")
            failed_list.append(name)
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Financial Highlight 테이블 찾기
        target_table = None
        tables = soup.find_all('table', class_='us_table_ty1 h_fix zigbg_no')
        for table in tables:
            caption = table.find('caption')
            if caption and 'Financial Highlight' in caption.text:
                target_table = table
                break

        if not target_table:
            print("❌ 테이블 찾기 실패")
            failed_list.append(name)
            continue

        # 헤더 추출
        header_rows = target_table.find_all('thead')[0].find_all('tr')
        if len(header_rows) < 2:
            print("❌ 헤더 2줄 이상이 아님")
            failed_list.append(name)
            continue

        col_years = [th.get_text(strip=True) for th in header_rows[1].find_all('th')]
        columns = ['항목'] + col_years

        # 본문 추출
        row_data = []
        for tr in target_table.tbody.find_all('tr'):
            cols = tr.find_all(['th', 'td'])
            row = [col.get_text(strip=True).replace(',', '') for col in cols]
            if len(row) == len(columns):
                row_data.append(row)

        if not row_data:
            print("⚠️ 데이터 없음")
            failed_list.append(name)
            continue

        df_table = pd.DataFrame(row_data, columns=columns)

        # 숫자 변환
        for col in df_table.columns[1:]:
            try:
                df_table[col] = pd.to_numeric(df_table[col].astype(str).str.replace(',', ''), errors='coerce')
            except Exception:
                continue

        # 저장할 시트로 등록
        if not df_table.empty:
            sheet_data[name[:30]] = df_table
            print(f"✅ {name} 저장 준비 완료")
        else:
            failed_list.append(name)

    except Exception as e:
        print(f"❌ {name} 실패: {e}")
        failed_list.append(name)

driver.quit()

# 실제 저장
if sheet_data:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df_sheet in sheet_data.items():
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"\n✅ 전체 저장 완료: {output_file}")
else:
    print("❌ 저장할 시트가 없어 파일 생성 안 함")

# 실패 종목 출력
if failed_list:
    print("\n⚠️ 실패한 종목 목록:")
    for name in failed_list:
        print(f" - {name}")
