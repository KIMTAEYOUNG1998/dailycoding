import requests
from bs4 import BeautifulSoup

# 1. 웹페이지 가져오기
url = 'https://weather.naver.com/'  # 크롤링할 URL을 지정합니다.
response = requests.get(url)  # 웹페이지 요청

# 요청이 성공했는지 확인
if response.status_code == 200:
    print("웹페이지를 성공적으로 가져왔습니다.")
else:
    print("웹페이지를 가져오는데 실패했습니다.")

# 2. HTML 파싱
html = response.text  # HTML 텍스트 가져오기
soup = BeautifulSoup(html, 'html.parser')  # BeautifulSoup으로 파싱

# 3. 원하는 데이터 추출
title = soup.title.text  # 웹페이지 제목 추출
weather_summary = soup.find('div', {'class': 'weather_summary'})  # 날씨 요약 부분

# 4. 데이터 저장
with open('weather_data.txt', 'w', encoding='utf-8') as file:  # utf-8 인코딩으로 파일을 열어 작성
    file.write("웹페이지 제목: " + title + "\n")  # 제목 저장
    if weather_summary:
        file.write("날씨 요약 정보:\n" + weather_summary.text.strip())  # 날씨 정보가 있으면 저장
    else:
        file.write("날씨 요약 정보를 찾을 수 없습니다.")  # 날씨 정보가 없으면 메시지 출력

print("크롤링한 데이터가 'weather_data.txt' 파일에 저장되었습니다.")