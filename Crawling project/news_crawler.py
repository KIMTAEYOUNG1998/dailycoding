import os
import re
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import tkinter as tk
from tkinter import messagebox

def run_crawling():
    # GUI에서 검색어와 기사 개수를 입력받음
    search_keyword = keyword_entry.get()
    num_articles = int(num_articles_entry.get())
    
    # 특수 문자 제거하여 파일 이름 생성
    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)
    output_file = os.path.join('C:/git/dailycoding/Crawling project', f'{safe_keyword}.csv')

    # ChromeDriver 설정
    service = Service(r'C:/git/dailycoding/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # Naver 홈페이지 접속
    url = 'https://www.naver.com/'
    driver.get(url)

    try:
        # 검색어 입력 및 검색 실행
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
        search_box.send_keys(search_keyword)
        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_search')))
        search_button.click()

        # "뉴스" 탭 클릭
        news_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '뉴스')))
        driver.execute_script("arguments[0].scrollIntoView();", news_tab)
        driver.execute_script("arguments[0].click();", news_tab)

        # CSV 파일 생성 및 쓰기 모드 설정
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Content'])

            # 뉴스 기사 리스트에서 제목과 내용 추출
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'news_tit')))
            news_list = driver.find_elements(By.CLASS_NAME, 'news_tit')
            article_count = 0

            for news in news_list:
                if article_count >= num_articles:
                    break

                title = news.text
                link = news.get_attribute('href')

                # 각 뉴스 기사 페이지로 이동하여 내용 추출
                driver.execute_script("window.open('');")  # 새 탭 열기
                driver.switch_to.window(driver.window_handles[1])  # 새 탭으로 전환
                driver.get(link)

                try:
                    content = ""
                    possible_classes = ['news_end', 'content', 'article_body', 'news_view', 'content_text']
                    for cls in possible_classes:
                        try:
                            content = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, cls))).text
                            if content:
                                break
                        except:
                            pass
                    if not content:
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
                article_count += 1
                time.sleep(1)  # 요청 간격 조정

        messagebox.showinfo("완료", f"뉴스 데이터가 '{output_file}'에 저장되었습니다.")
        
    except Exception as e:
        messagebox.showerror("오류 발생", str(e))
    finally:
        driver.quit()

# GUI 설정
root = tk.Tk()
root.title("뉴스 크롤링 프로그램")

tk.Label(root, text="검색할 키워드:").grid(row=0)
keyword_entry = tk.Entry(root)
keyword_entry.grid(row=0, column=1)

tk.Label(root, text="크롤링할 뉴스 기사 개수:").grid(row=1)
num_articles_entry = tk.Entry(root)
num_articles_entry.grid(row=1, column=1)

tk.Button(root, text="실행", command=run_crawling).grid(row=2, columnspan=2)

root.mainloop()