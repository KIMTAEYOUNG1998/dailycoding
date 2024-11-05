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
    search_keyword = keyword_entry.get()
    num_articles = int(num_articles_entry.get())
    
    # 특수 문자 제거하여 파일 이름 생성
    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)
    output_file = os.path.join('C:/git/dailycoding/Crawling project', f'{safe_keyword}.csv')

    # WebDriver 설정 및 크롤링 코드 (여기에 기존 코드 내용 포함)

    messagebox.showinfo("완료", f"뉴스 데이터가 '{output_file}'에 저장되었습니다.")
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
