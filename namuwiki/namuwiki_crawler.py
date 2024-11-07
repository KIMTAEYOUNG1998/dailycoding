import csv
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import messagebox
import logging

logging.basicConfig(filename='crawler_error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 크롤러 함수 정의
def start_crawler():
    search_keyword = entry_keyword.get()
    if not search_keyword:
        messagebox.showerror("오류", "검색어를 입력하세요.")
        return

    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)
    output_file = os.path.join('C:/git/dailycoding/namuwiki/output/', f'{safe_keyword}.csv')

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(r'C:/git/dailycoding/Crawling project/chromedriver-win64/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://namu.wiki/w/{search_keyword}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "UCfKg97Y"))
        )
        
        content = driver.find_element(By.CLASS_NAME, "UCfKg97Y").text
        content = content.replace("\n\n", "\n")

        # UTF-8로 파일 생성
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['제목', '내용'])
            writer.writerow([search_keyword, content])

        # UTF-8-BOM으로 재저장
        with open(output_file, 'r', encoding='utf-8') as f:
            data = f.read()
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(data)

        messagebox.showinfo("완료", f"데이터가 '{output_file}'에 UTF-8 BOM 형식으로 저장되었습니다.")
    
    except Exception as e:
        logging.error("문서 내용을 찾는 중 오류 발생", exc_info=True)
        messagebox.showerror("오류", f"오류 발생: {e}")

    driver.quit()

# Tkinter GUI 설정
root = tk.Tk()
root.title("Namuwiki Crawler")

tk.Label(root, text="검색할 키워드:").pack(pady=5)
entry_keyword = tk.Entry(root, width=30)
entry_keyword.pack(pady=5)
start_button = tk.Button(root, text="크롤링 시작", command=start_crawler)
start_button.pack(pady=20)
root.mainloop()

