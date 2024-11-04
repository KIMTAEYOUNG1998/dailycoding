from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ChromeDriver 절대 경로 지정
service = Service('C:/git/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# 웹페이지 열기
url = 'https://weather.naver.com/'
driver.get(url)

# 페이지 로딩 대기 (최대 20초 대기)
try:
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'is_weather')))
    print("웹페이지가 로드되었습니다.")
except:
    print("웹페이지 로딩에 실패했습니다.")
    driver.quit()
    exit()

# 데이터 추출
title = driver.title
try:
    weather_summary = driver.find_element(By.CLASS_NAME, 'is_weather').text
except:
    weather_summary = "날씨 요약 정보를 찾을 수 없습니다."

# 데이터 저장
with open('weather_data_selenium.txt', 'w', encoding='utf-8') as file:
    file.write("웹페이지 제목: " + title + "\n")
    file.write("날씨 요약 정보:\n" + weather_summary)

print("크롤링한 데이터가 'weather_data_selenium.txt' 파일에 저장되었습니다.")
driver.quit()
