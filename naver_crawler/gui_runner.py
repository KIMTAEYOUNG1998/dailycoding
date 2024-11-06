import os
import re
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

def run_crawling():
    search_keyword = keyword_entry.get()
    num_articles = int(num_articles_entry.get())
    source = source_var.get()
    
    safe_keyword = re.sub(r'[\\/*?:"<>|]', "", search_keyword)
    output_file = os.path.join('C:/git/dailycoding/Crawling project', f'{safe_keyword}_{source}.csv')
    
    # Scrapy 프로젝트 루트 경로
    project_dir = 'C:/git/dailycoding/naver_crawler'

    # Scrapy 스파이더 실행 명령어
    command = [
        'scrapy', 'crawl', 'naver', 
        '-a', f'keyword={search_keyword}', 
        '-a', f'source={source}', 
        '-a', f'num_articles={num_articles}', 
        '-o', output_file
    ]
    
    try:
        subprocess.run(command, check=True, cwd=project_dir)  # cwd 인자로 프로젝트 경로 지정
        messagebox.showinfo("완료", f"{source} 데이터가 '{output_file}'에 저장되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류 발생", f"크롤링 중 문제가 발생했습니다: {str(e)}")

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

