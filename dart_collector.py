# import os
# import requests
# from pathlib import Path
# from dotenv import load_dotenv

# # 현재 python 파일과 같은 폴더의 .env 읽기
# load_dotenv(Path(__file__).resolve().parent / ".env")

# api_key = os.getenv("DART_API_KEY")

# if not api_key:
#     raise ValueError("DART_API_KEY가 설정되지 않았습니다.")

# url = "https://opendart.fss.or.kr/api/company.json"

# params = {
#     "crtfc_key": api_key,
#     "corp_code":"00126380"
# }

# response = requests.get(url, params= params, timeout=10)
# response.raise_for_status()

# date = response.json()

# print("응답 상태:", date.get("corp_name"))
# print("응답 메세지:", date.get("message"))

# if date.get("status") =="000":
#     print("기업명:", date.get("corp_name"))
#     print("대표자:", date.get("ceo.nm"))
#     print("업종코드:", date.get("induty_code"))
#     print("설립일:", date.get("est_dt"))
# else:
#     print("API 요청 결과를 확인해야 합니다.")
# # load_dotenv(): .env 파일의 환경변수 읽기
# # os.getenv(): 인증키 가져오기
# # params: API에 전달할 요청 조건
# # corp_code: OpenDART의 기업 고유번호 
# # response.json(): Json응답을 python 데이터로 변환
# # status == "000": OpenDART API 처리 성공

# 실습

import os
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
api_key = os.getenv("DART_API_KEY")

if not api_key:
    raise ValueError("DART_API_KEY가 없습니다.")

companies = {
    "삼성전자": "00126380",
    "SK하이닉스": "00164779",
    "NAVER": "00266961",
    "현대자동차": "00164742",
    "카카오": "00258801"
}

url = "https://opendart.fss.or.kr/api/company.json"
data_list = []

for name, corp_code in companies.items():
    params ={
        "crtfc_key": api_key,
        "corp_code": corp_code
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()


    if data.get("status") =="000":
        data_list.append({
            "corp_code": corp_code,
            "corp_name": data.get("corp_name"),
            "ceo_name": data.get("ceo_nm"),
            "industry_code": data.get("induty_code"),
            "est_date": data.get("est_dt")
        })
        print(name, "수집 성공")
    else:
        print(name, "수집 실패:", data.get("message"))

    time.sleep(0.5)

df = pd.DataFrame(data_list)

print("\n수집 결과:")
print(df)

print("\n수집 기업 수:", len(df))
# companies ={...}: 기업명과 고유번호를 딕셔너리로 관리
# .items(): 딕셔너리의 키와 값을 함께 가져오기
# data_list.append(): 기업정보를 리스트에 누적
# time.sleep(0.5): 서버에 요청을 연속으로 보내지 않도록 대기
# pd.DataFrame(): 수집한 기업정보를 표 형태로 변환

# 9. 실제 기업정보 품질 검증
# 필수 데이터 결측치 검사 
required_columns = ["corp_code", "corp_name", "industry_code"]

print("\n필수 데이터 결측치:")
print(df[required_columns].isnull().sum())

# 기업 고유번호 중복 검사 
duplicate_count = df.duplicated(subset=["corp_code"]).sum()
print("\n기업 고유번호 중복:", duplicate_count)

# 설립일 형식 검증
df["est_date_vaild"] = pd.to_datetime(
    df["est_date"],
    format ="%Y%m%d",
    errors="coerce"
).notna()

print("\n설립일 형식 오류:")
print((~df["est_date_vaild"]).sum())

# 전체 품질검증 결과
print("\n품질검증 완료")
# required_columns: 반드시 확인할 필 수 열 지정
# isnull().sum(): 열별 결측치 개수 계산
# duplicated(subset=["corp_code"]): 기업 고유번호 기준 중복 검사
# pd.to_datetime(): 날짜 형식으로 변환
# errors="corece": 변환할 수 없는 값을 NaT로 처리
# .notna(): 날짜 변환에 성공했는지 확인
# ~: True와 False를 반대로 전환

# 10. SQLite DB저장 및 품질검증 결과 기록
import sqlite3
from datetime import datetime

# DB 연결
db_path = Path(__file__).resolve().parent / "company_data.db"
conn= sqlite3.connect(db_path)

# 기업정보 저장
df.to_sql("companies", conn, if_exists="replace", index=False)

# 품질정보 결과 생성
validation_result = pd.DataFrame([{
    "checked_at": datetime.now().isoformat(timespec="seconds"),
    "total_count": len(df),
    "missing_count": int(df[required_columns].isnull().sum().sum()),
    "duplicate_count": int(df.duplicated(subset=["corp_code"]).sum()),
    "invalid_date_count": int((~df["est_date_vaild"]).sum())
}])

# 검증 결과 저장
validation_result.to_sql(
    "vaildation_logs",
    conn,
    if_exists="append",
    index=False
)

# DB 조회
result = pd.read_sql_query("SELECT corp_code, corp_name, industry_code FROM companies",
                           conn)

print("\nDB 저장 결과:")
print(result)

print("\n품질검증 기록:")
print(pd.read_sql_query("SELECT * FROM vaildation_logs", conn))

conn.close()