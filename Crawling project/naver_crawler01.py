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
from tkinter import messagebox, ttk
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def run_crawling():
    search_keyword = keyword_entry.get()
    num_articles = int(num_articles_entry.get())
    source = source_var.get()
    
    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)
    output_file = os.path.join('C:/git/dailycoding/Crawling project', f'{safe_keyword}_{source}.csv')

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")  # 디버깅 포트 추가
    chrome_options.add_argument("--headless")  # 헤드리스 모드로 설정 (필요시 주석 처리)
    # ChromeDriver 설정
    service = Service(r'C:/git/dailycoding/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    try:
        if source == "뉴스":
            crawl_news(driver, search_keyword, num_articles, output_file)
        elif source == "블로그":
            crawl_blog(driver, search_keyword, num_articles, output_file)
        elif source == "지식인":
            crawl_knowledgein(driver, search_keyword, num_articles, output_file)
        
        messagebox.showinfo("완료", f"{source} 데이터가 '{output_file}'에 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류 발생", f"크롤링 중 문제가 발생했습니다: {str(e)}")
    finally:
        driver.quit()

def crawl_news(driver, search_keyword, num_articles, output_file):
    driver.get('https://www.naver.com/')
    try:
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
        search_box.send_keys(search_keyword)

        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_search')))
        search_button.click()

        news_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '뉴스')))
        driver.execute_script("arguments[0].scrollIntoView();", news_tab)
        driver.execute_script("arguments[0].click();", news_tab)

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Content'])

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'news_tit'))
            )

            news_list = driver.find_elements(By.CLASS_NAME, 'news_tit')
            article_count = 0

            for news in news_list:
                if article_count >= num_articles:
                    break

                title = news.text
                link = news.get_attribute('href')

                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                
                try:
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
                        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                        content = "\n".join([p.text for p in paragraphs if p.text])

                    if not content:
                        content = "내용을 불러올 수 없습니다."
                except:
                    content = "내용을 불러올 수 없습니다."

                writer.writerow([title, content])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                article_count += 1
                time.sleep(1)

    except Exception as e:
        print(f"오류 발생: {e}")

def crawl_blog(driver, search_keyword, num_articles, output_file):
    driver.get('https://www.naver.com/')
    
    try:
        # 검색어 입력 및 검색 버튼 클릭
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'query')))
        search_box.send_keys(search_keyword)

        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_search')))
        search_button.click()

        # 블로그 탭 클릭
        blog_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, '블로그')))
        driver.execute_script("arguments[0].scrollIntoView();", blog_tab)
        driver.execute_script("arguments[0].click();", blog_tab)

        # CSV 파일 생성
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Content'])

            # 블로그 목록이 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'api_txt_lines.total_tit'))
            )

            blogs = driver.find_elements(By.CLASS_NAME, 'api_txt_lines.total_tit')
            article_count = 0

            for blog in blogs:
                if article_count >= num_articles:
                    break

                # 제목과 링크 추출
                title = blog.text
                link = blog.get_attribute('href')
                print(f"블로그 제목: {title} | 링크: {link}")

                # 링크 클릭 시도
                clicked = False
                retry_count = 0
                while not clicked and retry_count < 3:
                    try:
                        driver.execute_script("window.open(arguments[0]);", link)
                        driver.switch_to.window(driver.window_handles[1])
                        clicked = True  # 클릭 성공 시 탈출
                    except Exception as e:
                        print(f"블로그 링크 클릭 실패, 재시도 중... ({retry_count + 1}/3)")
                        retry_count += 1
                        time.sleep(2)  # 재시도 전에 잠시 대기

                if not clicked:
                    print("블로그 링크 클릭에 실패하여 해당 항목을 건너뜁니다.")
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                try:
                    # 네이버 블로그의 경우, iframe이 존재하므로 iframe으로 전환
                    WebDriverWait(driver, 10).until(
                        EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))
                    )

                    # 본문 내용 로드 확인
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )

                    # 블로그 본문 내용 추출
                    content = ""
                    possible_classes = ['se-main-container', 'post_ct', 'post-view']
                    for cls in possible_classes:
                        try:
                            content = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, cls))
                            ).text
                            if content:
                                break
                        except:
                            pass

                    # 만약 본문 내용이 없을 경우, <p> 태그로부터 텍스트를 추출
                    if not content:
                        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                        content = "\n".join([p.text for p in paragraphs if p.text])

                    if not content:
                        content = "내용을 불러올 수 없습니다."

                    # iframe에서 메인 콘텐츠로 복귀
                    driver.switch_to.default_content()
                except Exception as e:
                    print(f"블로그 본문을 가져오는 중 오류 발생: {str(e)}")
                    content = "내용을 불러올 수 없습니다."

                # 본문이 로드된 후에만 결과를 CSV 파일에 저장
                writer.writerow([title, content])
                
                # 현재 탭 닫기 및 원래 탭으로 전환
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                article_count += 1
                time.sleep(1)

    except Exception as e:
        print(f"오류 발생: {str(e)}")



def crawl_knowledgein(driver, search_keyword, num_articles, output_file):
    url = 'https://kin.naver.com/search/list.naver?query=' + search_keyword
    driver.get(url)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Question', 'Answer'])

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.basic1 > li > a'))
        )

        questions = driver.find_elements(By.CSS_SELECTOR, '.basic1 > li > a')
        article_count = 0

        for question in questions:
            if article_count >= num_articles:
                break

            title = question.text
            link = question.get_attribute('href')

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)

            try:
                question_content = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'c-heading__content'))
                ).text

                answer_elements = driver.find_elements(By.CLASS_NAME, 'se-main-container')
                answer_content = "\n\n".join([answer.text for answer in answer_elements])

                if not answer_content:
                    paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                    answer_content = "\n\n".join([p.text for p in paragraphs if p.text])

                if not answer_content:
                    answer_content = "답변을 불러올 수 없습니다."
            except:
                question_content = "질문을 불러올 수 없습니다."
                answer_content = "답변을 불러올 수 없습니다."

            writer.writerow([title, question_content, answer_content])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            article_count += 1
            time.sleep(1)

# GUI 설정
root = tk.Tk()
root.title("네이버 크롤링 프로그램")

tk.Label(root, text="검색할 키워드:").grid(row=0)
keyword_entry = tk.Entry(root)
keyword_entry.grid(row=0, column=1)

tk.Label(root, text="크롤링할 개수:").grid(row=1)
num_articles_entry = tk.Entry(root)
num_articles_entry.grid(row=1, column=1)

tk.Label(root, text="크롤링 소스 선택:").grid(row=2)
source_var = tk.StringVar(value="뉴스")
source_menu = ttk.Combobox(root, textvariable=source_var)
source_menu['values'] = ("뉴스", "블로그", "지식인")
source_menu.grid(row=2, column=1)

tk.Button(root, text="실행", command=run_crawling).grid(row=3, columnspan=2)

root.mainloop()