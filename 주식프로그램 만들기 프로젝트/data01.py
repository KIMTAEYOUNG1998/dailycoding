import requests
import FinanceDataReader as fdr
import pandas as pd
import tkinter as tk
from tkinter import ttk
import yfinance as yf
from bs4 import BeautifulSoup
import datetime

def get_kospi_kosdaq_stock_list():
    stock_list = []
    sectors = set()

    # 코스피와 코스닥 종목 전체를 가져오기
    kospi = fdr.StockListing('KOSPI')
    kosdaq = fdr.StockListing('KOSDAQ')
    
    # 두 데이터프레임을 합침
    all_stocks = pd.concat([kospi, kosdaq], ignore_index=True)
    
    for _, row in all_stocks.iterrows():
        name = row['Name']
        code = row['Code']
        sector = row['Sector'] if 'Sector' in row and pd.notna(row['Sector']) else 'Unknown'
        stock_list.append((name, code, sector))
        sectors.add(sector)
    
    print("총 종목 수:", len(stock_list))  # 가져온 종목 수 확인
    print("업종 리스트:", sectors)  # 업종 리스트 확인
    
    return stock_list, sorted(sectors)

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
        # KOSPI와 KOSDAQ 구분하여 티커 접미사 추가
        ticker_symbol = f"{symbol}.KS" if symbol.startswith("0") else f"{symbol}.KQ"
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        return data.iloc[-1]
    except Exception:
        return None

# 조건에 맞는 주식 검색 함수
def search_stocks():
    result_text.delete(1.0, tk.END)

    min_price_value = float(min_price.get() or 0)
    max_price_value = float(max_price.get() or float("inf"))
    min_volume_value = float(min_volume.get() or 0)
    max_volume_value = float(max_volume.get() or float("inf"))
    min_per_value = float(min_per.get() or 0)
    max_per_value = float(max_per.get() or float("inf"))
    min_pbr_value = float(min_pbr.get() or 0)
    max_pbr_value = float(max_pbr.get() or float("inf"))
    selected_sector = sector_combobox.get()
    stock_name_filter = stock_name_entry.get().strip()

    stock_list, _ = get_kospi_kosdaq_stock_list()
    matched_stocks = []

    for name, symbol, sector in stock_list:
        if selected_sector and selected_sector != sector:
            continue
        if stock_name_filter and stock_name_filter.lower() not in name.lower():
            continue

        try:
            per, pbr = get_stock_per_pbr(symbol)
            print(f"{name} ({symbol}) - PER: {per}, PBR: {pbr}")
            if per is None or pbr is None:
                continue
            if not (min_per_value <= per <= max_per_value) or not (min_pbr_value <= pbr <= max_pbr_value):
                continue

            stock_data = get_stock_data(symbol)
            if stock_data is None:
                print(f"{name} ({symbol}) - 주식 데이터 없음")
                continue

            price = stock_data['Close']
            volume = stock_data['Volume']
            print(f"{name} ({symbol}) - 주가: {price}, 거래량: {volume}")

            if (min_price_value <= price <= max_price_value) and (min_volume_value <= volume <= max_volume_value):
                # 여기서 리스트에 추가되는지 확인
                matched_stock_info = f"{name} ({symbol}): 업종={sector}, 주가={price}, 거래량={volume}, PER={per}, PBR={pbr}"
                matched_stocks.append(matched_stock_info)
                print(f"매칭된 종목 추가됨: {matched_stock_info}")  # 디버깅용 출력
        except Exception as e:
            print(f"오류 발생: {e}")
            continue

    # 파일에 결과 저장
    if matched_stocks:
        filename = f"stock_search_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write("조건에 맞는 종목:\n" + "\n".join(matched_stocks) + "\n")
        result_text.insert(tk.END, f"{len(matched_stocks)}개의 종목이 파일 '{filename}'에 저장되었습니다.\n")
    else:
        result_text.insert(tk.END, "조건에 맞는 종목이 없습니다. 파일이 생성되지 않았습니다.\n")
        
# Tkinter GUI 설정
root = tk.Tk()
root.title("주식 조건 검색 프로그램")
root.geometry("600x800")

name_label = ttk.Label(root, text="종목명")
name_label.pack()
stock_name_entry = tk.Entry(root, width=20)
stock_name_entry.pack()

price_label = ttk.Label(root, text="주가 범위")
price_label.pack()
min_price = tk.Entry(root, width=10)
min_price.pack()
max_price = tk.Entry(root, width=10)
max_price.pack()

volume_label = ttk.Label(root, text="거래량 범위")
volume_label.pack()
min_volume = tk.Entry(root, width=10)
min_volume.pack()
max_volume = tk.Entry(root, width=10)
max_volume.pack()

per_label = ttk.Label(root, text="PER 범위")
per_label.pack()
min_per = tk.Entry(root, width=10)
min_per.pack()
max_per = tk.Entry(root, width=10)
max_per.pack()

pbr_label = ttk.Label(root, text="PBR 범위")
pbr_label.pack()
min_pbr = tk.Entry(root, width=10)
min_pbr.pack()
max_pbr = tk.Entry(root, width=10)
max_pbr.pack()

sector_label = ttk.Label(root, text="업종 선택")
sector_label.pack()
stock_list, sectors = get_kospi_kosdaq_stock_list()
sector_combobox = ttk.Combobox(root, values=[""] + sectors)
sector_combobox.pack()

result_text = tk.Text(root, height=5, width=80)
result_text.pack(pady=10)

search_button = ttk.Button(root, text="검색", command=search_stocks)
search_button.pack(pady=10)

root.mainloop()
