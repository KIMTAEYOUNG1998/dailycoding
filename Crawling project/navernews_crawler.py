from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# ChromeDriver 절대 경로 설정
service = Service('C:/git/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# 네이버 뉴스 메인 페이지 열기
url = 'https://news.naver.com/'
driver.get(url)

# 검색어 입력 및 검색 버튼 클릭
search_keyword = "검색할 키워드"  # 원하는 키워드로 변경

try:
    # 검색창에 검색어 입력
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
    driver.execute_script("arguments[0].scrollIntoView();", search_box)
    search_box.send_keys(search_keyword)

    # 검색 버튼 클릭
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_search')))
    driver.execute_script("arguments[0].click();", search_button)
except Exception as e:
    print(f"오류 발생: {e}")
    driver.quit()


# CSV 파일 생성 및 쓰기 모드 설정
with open('naver_news_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Content'])

    # 뉴스 기사 리스트에서 제목과 내용 추출
    try:
        # 검색 결과 페이지에서 기사 리스트 요소 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'news_tit'))
        )
        
        # 뉴스 기사 요소 찾기
        news_list = driver.find_elements(By.CLASS_NAME, 'news_tit')
        for news in news_list:
            title = news.text
            link = news.get_attribute('href')

            # 각 뉴스 기사 페이지로 이동하여 내용 추출
            driver.execute_script("window.open('');")  # 새 탭 열기
            driver.switch_to.window(driver.window_handles[1])  # 새 탭으로 전환
            driver.get(link)
            
            try:
                content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'news_end'))
                ).text
            except:
                content = "내용을 불러올 수 없습니다."
            
            # 제목과 내용을 CSV 파일에 저장
            writer.writerow([title, content])
            driver.close()  # 현재 탭 닫기
            driver.switch_to.window(driver.window_handles[0])  # 원래 탭으로 전환

    except Exception as e:
        print(f"오류 발생: {e}")

print("뉴스 데이터가 'naver_news_results.csv'에 저장되었습니다.")
driver.quit()
