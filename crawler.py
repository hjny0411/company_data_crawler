# # 1.웹사이트에 데이터 요청하기
# import requests
# url = "https://quotes.toscrape.com/"

# response = requests.get(url, timeout=10)

# print("상태 코드:", response.status_code)
# print("HTML 내용:", response.text[:500])
# # import requests: HTTP 요청 라이브러리 불러오기 
# # url: 수집 대상 웹사이트 지정
# # requests.get(): 웹사이트에 GET 요청 보내기
# # timeout=10: 최대 10초 동안 응답 기다리기
# # response.status_code: 서버의 응답 상태 확인(200:요청성공, 403:접근금지. 404:요청한 페이지를 찾을 수 없음, 500: 서버 내부 오류)
# # response.text: 응답받은 HTML 문자열
# # [:500]: 문자열의 앞 500글자 추출

# # Beautifulsoup이란 requests가 웹페이지의 HTML을 가져오는 도구라면, BeautifulSoup은 HTML을 분석해서 원하는 요소를 찾아주는 도구다.

# # 2. Beautifulsoup으로 원하는 데이터 추출하기.
# import requests
# from bs4 import BeautifulSoup

# url = "https://quotes.toscrape.com/"
# response = requests.get(url, timeout =10)
# response.raise_for_status()

# soup = BeautifulSoup(response.text, "html.parser")

# quotes = soup.select(".quote")

# print("수집된 문장 수:", len(quotes))

# for quote in quotes:
#     text = quote.select_one(".text").get_text(strip=True)
#     author = quote.select_one(".author").get_text(strip=True)
    
#     print("문장:", text)
#     print("작성자:", author)
#     print()
# # BeautifulSoup(): HTML을 분석 가능한 객체로 변환
# # html.parser: python 기본 HTML 분석기
# # soup.select(".quote"): quote 클래스를 가진 요소 모두 선택
# # .quote의 점(.)은 HTML의 class속성을 선택한다는 의미.
# # len(quotes): 추출된 요소 개수 확인
# # for quote in quotes: 추출한 요소를 하나씩 처리 
# # select_one(".text"): 해당 요소 안에서 text 클래스 요소 하나 선택
# # get_text(strip=True): HTML 태그를 제외한 텍스트 추출, 앞뒤 공백 제거
# # raise_for_status(): HTTP 오류 응답이면 예외 발생 

# 3.pandas로 수집 데이터 구조화하기. 
import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"
response = requests.get(url, timeout=10)
response.raise_for_status

soup = BeautifulSoup(response.text, "html.parser")
quotes = soup.select(".quote")

data = []

for quote in quotes:
    text = quote.select_one(".text").get_text(strip=True)
    author = quote.select_one(".author").get_text(strip=True)
    
    data.append({
        "text": text,
        "author": author
    })
    
df = pd.DataFrame(data)

print(df)
print("데이터 크기:", df.shape)
# import pandas as pd: pandas 라이브러리 불러오기
# data=[]: 수집 데이터를 저장할 빈 리스트 생성
# data.append(): 리스트에 데이터 추가
# {"text": text, "author": author}: 딕셔너리 형태로 데이터 구성
# pd. DataFrame(data): 리스트를 표 형태의 데이터로 변환
# df.shape: 데이터의 행과 열 개수 확인 

# 4. 데이터 품질검증 
print("전체 데이터 수:", len(df))

print("결측치 개수:")
print(df.isnull().sum())

print("중복 데이터 수:", df.duplicated().sum())

# 5. 오류 데이터 생성 및 품질검증
# 원본 데이터 보존
df_test = df.copy()

# 결측치 생성
df_test.loc[0, "author"] = None

# 중복 데이터 생성
df_test = pd.concat([df_test, df_test.iloc[[1]]], ignore_index=True)

print("오류 데이터 생성 후:")
print(df_test)

print("결측치 검사:")
print(df_test.isnull().sum())

print("중복 데이터 검사:")
print(df_test.duplicated().sum())

# 6. 오류 데이터 정제하기
df_clean = df_test.dropna(subset=["text", "author"])
df_clean = df_clean.drop_duplicates()

print("정제 전 데이터:", len(df_test))
print("정제 후 데이터:", len(df_clean))

print("정제 후 결측치:")
print(df_clean.isnull().sum())

print("정제 후 중복 데이터:", df_clean.duplicated().sum())
# dropan():결측치가 있는 행을 제거
# subset=["text", "author"]: 두 열을 결측치 검사 대상으로 지정
# drop_duplicates(): 중복 행 제거
# len(df_clean): 정제 후 남은 행 개수

# 7. SQLite 데이터베이스에 저장하기.
import sqlite3
# 데이터베이스에 연결
conn = sqlite3.connect("crawler.db")
# 정제된 데이터 저장
df_clean.to_sql(
    "quotes",
    conn,
    if_exists="replace",
    index=False
)
# 저장된 데이터 조회
query = "SELECT * FROM quotes"
df_sql = pd.read_sql_query(query, conn)

print("DB 저장 결과:")
print(df_sql)

print("저장된 데이터의 수:", len(df_sql))

conn.close()

# sqlite3.connect: SQLite DB 연결 또는 생성
# to_sql: DataFrame을 SQL 테이블에 저장
# if exists ="replace": 기존 테이블이 있으면 교체
# index = False: pandas 인덱스를 별도 열로 저장하지 않음
# pd.read_sql_query(): SQL 조회 결과를 DataFrame으로 변환
# conn.close(): DB 연결 종료 