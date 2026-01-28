import requests
import json
from datetime import datetime, timedelta
import time as tm
import tkinter as tk
from tkinter import messagebox

def earthquake_search():
    result.delete("1.0", tk.END)
    
    # 自動的に「現在」から「14日前」の範囲を設定
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=14)
    
    date_str = start_dt.strftime('%Y/%m/%d')
    print(f"検索を開始します: {date_str} ～ 現在")
    root.update()

    finished = False
    for offset_num in range(0, 1000, 100):
        if finished: break
        
        url = f"https://api.p2pquake.net/v2/history?codes=551&limit=100&offset={offset_num}"
        try:
            response = requests.get(url)
            kekka = json.loads(response.text)
        except:
            break

        for data in kekka:
            try:
                time_val = data['time']
                eq_dt = datetime.strptime(time_val[:19], "%Y/%m/%d %H:%M:%S")
                
                # 指定した14日前より古くなったら検索終了
                if eq_dt < start_dt:
                    finished = True
                    break

                place = data['earthquake']['hypocenter']['name']
                max_v = data['earthquake']['maxScale'] / 10
                mag = data['earthquake']['hypocenter']['magnitude']

                if mag == -1: mag = "不明"
                if place == '': place = "調査中"

                # 【条件】マグニチュード5以上、最大震度3以上
                if (isinstance(max_v, (int, float)) and max_v >= 3) and \
                   (isinstance(mag, (int, float)) and mag >= 5):
                    res = f'【{time_val}】\n {place} (M{mag} / 震度{max_v})\n'
                    res += "-" * 30 + "\n"
                    result.insert(tk.END, res)
                    root.update()
            except KeyError:
                pass
        tm.sleep(0.1)

    if not result.get("1.0", tk.END).strip():
        result.insert(tk.END, "指定された条件で地震は見つかりませんでした。")
    
    messagebox.showinfo("検索終了", "検索が完了しました！")

def my_reset():
    result.delete("1.0", tk.END)

root = tk.Tk()
root.title("地震履歴分析ツール")
root.minsize(530, 600)

#日付の計算
today = datetime.now()
start_date = today - timedelta(days=14)

start_str = start_date.strftime("%Y/%m/%d")
today_str = today.strftime("%Y/%m/%d")

bi = ("MSゴシック", "15", "")
sm = ("MSゴシック", "10", "")

# GUIをスッキリ整理
title = tk.Label(text="最新2週間の地震データ (M5.0以上 / 震度3以上)", font=bi)
title.place(x=50, y=20)

period_label = tk.Label(
    text=f"取得対象期間： {start_str} ～ {today_str} (直近14日間)", 
    font=sm, 
    fg="black"
)
period_label.place(x=80, y=55)


desc = tk.Label(text="※APIのデータ保持期間に基づき、履歴をチェックしています", fg="#666", font=sm)
desc.place(x=30, y=450)

btn = tk.Button(text="検索開始", command=earthquake_search, font=sm)
btn.place(x=150, y=130, width=200, height=30)

result = tk.Text(width=65, height=20, font=("MSゴシック", 10))
r_scroll = tk.Scrollbar(orient="vertical", command=result.yview)
result["yscrollcommand"] = r_scroll.set

result.place(x=30, y=180)
r_scroll.place(x=490, y=180, height=325)

btn2 = tk.Button(text='クリア', command=my_reset)
btn2.place(x=240, y=530)

root.mainloop()