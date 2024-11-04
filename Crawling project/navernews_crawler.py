import os
import re
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# ChromeDriver 절대 경로 설정
service = Service(r'C:/git/dailycoding/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

url = 'https://www.naver.com/'
driver.get(url)

# 사용자가 검색어 및 크롤링할 기사 개수 입력
search_keyword = input("검색할 키워드를 입력하세요: ")
num_articles = int(input("크롤링할 뉴스 기사 개수를 입력하세요: "))

# 검색어를 파일 이름에 사용하기 위해 특수 문자 제거
safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)  # 파일 이름에 사용할 수 없는 문자 제거
output_file = os.path.join('C:/git/dailycoding/Crawling project', f'{safe_keyword}.csv')

try:
    # 검색창에 검색어 입력
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
    search_box.send_keys(search_keyword)

    # 검색 버튼 클릭
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_search')))
    search_button.click()

    # "뉴스" 탭 클릭
    news_tab = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, '뉴스'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", news_tab)
    driver.execute_script("arguments[0].click();", news_tab)

except Exception as e:
    print(f"오류 발생: {e}")
    driver.quit()

# CSV 파일 생성 및 쓰기 모드 설정
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
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
        article_count = 0  # 크롤링한 기사 개수를 추적

        for news in news_list:
            if article_count >= num_articles:
                break  # 원하는 개수만큼 크롤링하면 종료

            title = news.text
            link = news.get_attribute('href')

            # 각 뉴스 기사 페이지로 이동하여 내용 추출
            driver.execute_script("window.open('');")  # 새 탭 열기
            driver.switch_to.window(driver.window_handles[1])  # 새 탭으로 전환
            driver.get(link)
            
            try:
                # 여러 클래스명 또는 태그를 사용해 기사 본문 내용 찾기
                content = ""
                possible_classes = ['news_end', 'content', 'article_body', 'news_view', 'content_text']
                for cls in possible_classes:
                    try:
                        content = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, cls))
                        ).text
                        if content:
                            break
                    except:
                        pass
                if not content:
                    # 클래스 이름으로 찾지 못했을 경우 div 또는 p 태그로 시도
                    paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                    content = "\n".join([p.text for p in paragraphs if p.text])

                if not content:
                    content = "내용을 불러올 수 없습니다."
            except:
                content = "내용을 불러올 수 없습니다."
            
            # 제목과 내용을 CSV 파일에 저장
            writer.writerow([title, content])
            driver.close()  # 현재 탭 닫기
            driver.switch_to.window(driver.window_handles[0])  # 원래 탭으로 전환
            article_count += 1  # 크롤링한 기사 개수 증가
            time.sleep(1)  # 요청 간격 조정

    except Exception as e:
        print(f"오류 발생: {e}")

print(f"뉴스 데이터가 '{output_file}'에 저장되었습니다.")
driver.quit()