import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
import yfinance as yf

def get_kospi_stock_list():
    url = "https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page="
    stock_list = []
    sectors = set()  # 업종 목록을 담기 위한 set 생성

    for page in range(1, 5):  # 필요한 페이지 수만큼 반복
        response = requests.get(url + str(page))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table.type_2 tbody tr")
        for row in rows:
            if len(row.select("td")) > 1:
                name = row.select_one("a.tltle").text
                code = row.select_one("a.tltle")["href"].split("=")[-1]
                sector = row.select("td")[5].text.strip()  # 업종 정보를 추가
                stock_list.append((name, code, sector))
                sectors.add(sector)  # 업종 정보를 set에 추가

    return stock_list, sorted(sectors)  # stock_list와 정렬된 업종 리스트 반환

# Naver 금융에서 PER, PBR 값을 가져오는 함수
def get_stock_per_pbr(symbol):
    url = f"https://finance.naver.com/item/main.nhn?code={symbol}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    per_tag = soup.select_one("em#_per")
    pbr_tag = soup.select_one("em#_pbr")

    per = float(per_tag.text.replace(",", "")) if per_tag and per_tag.text else None
    pbr = float(pbr_tag.text.replace(",", "")) if pbr_tag and pbr_tag.text else None
    return per, pbr

# 주식 데이터를 가져오는 함수
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(f"{symbol}.KS")
        data = stock.history(period="1d")
        if data.empty:
            return None  # 데이터가 없으면 None 반환
        return data.iloc[-1]
    except Exception as e:
        # 예외가 발생하면 None 반환
        return None

# 조건에 맞는 주식 검색 함수
def search_stocks():
    result_text.delete(1.0, tk.END)  # 이전 결과 삭제

    # 사용자 입력 조건
    min_price_value = float(min_price.get() or 0)
    max_price_value = float(max_price.get() or float("inf"))
    min_volume_value = float(min_volume.get() or 0)
    max_volume_value = float(max_volume.get() or float("inf"))
    min_per_value = float(min_per.get() or 0)
    max_per_value = float(max_per.get() or float("inf"))
    min_pbr_value = float(min_pbr.get() or 0)
    max_pbr_value = float(max_pbr.get() or float("inf"))
    selected_sector = sector_combobox.get()  # 선택한 업종 정보

    stock_list, _ = get_kospi_stock_list()
    matched_stocks = []

    for name, symbol, sector in stock_list:
        if selected_sector and selected_sector != sector:
            continue  # 선택한 업종과 일치하지 않으면 건너뜁니다.

        try:
            per, pbr = get_stock_per_pbr(symbol)
            if per is None or pbr is None:
                continue
            if not (min_per_value <= per <= max_per_value) or not (min_pbr_value <= pbr <= max_pbr_value):
                continue

            stock_data = get_stock_data(symbol)
            if stock_data is None:
                continue

            price = stock_data['Close']
            volume = stock_data['Volume']

            if (min_price_value <= price <= max_price_value) and (min_volume_value <= volume <= max_volume_value):
                matched_stocks.append(f"{name} ({symbol}): 업종={sector}, 주가={price}, 거래량={volume}, PER={per}, PBR={pbr}")
        except Exception as e:
            continue

    # 결과 출력
    if matched_stocks:
        result_text.insert(tk.END, "조건에 맞는 종목:\n" + "\n".join(matched_stocks) + "\n")
    else:
        result_text.insert(tk.END, "조건에 맞는 종목이 없습니다.\n")

# Tkinter GUI 설정
root = tk.Tk()
root.title("주식 조건 검색 프로그램")
root.geometry("600x700")

# 주가 범위
price_label = ttk.Label(root, text="주가 범위")
price_label.pack()
min_price = tk.Entry(root, width=10)
min_price.pack()
max_price = tk.Entry(root, width=10)
max_price.pack()

# 거래량 범위
volume_label = ttk.Label(root, text="거래량 범위")
volume_label.pack()
min_volume = tk.Entry(root, width=10)
min_volume.pack()
max_volume = tk.Entry(root, width=10)
max_volume.pack()

# PER 범위
per_label = ttk.Label(root, text="PER 범위")
per_label.pack()
min_per = tk.Entry(root, width=10)
min_per.pack()
max_per = tk.Entry(root, width=10)
max_per.pack()

# PBR 범위
pbr_label = ttk.Label(root, text="PBR 범위")
pbr_label.pack()
min_pbr = tk.Entry(root, width=10)
min_pbr.pack()
max_pbr = tk.Entry(root, width=10)
max_pbr.pack()

# 업종 선택 (ComboBox 추가)
sector_label = ttk.Label(root, text="업종 선택")
sector_label.pack()
stock_list, sectors = get_kospi_stock_list()  # 모든 업종 리스트 받아오기
sector_combobox = ttk.Combobox(root, values=[""] + sectors)  # 빈 값과 함께 모든 업종 추가
sector_combobox.pack()

# 결과 출력창
result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=10)

# 검색 버튼
search_button = ttk.Button(root, text="검색", command=search_stocks)
search_button.pack(pady=10)

root.mainloop()
