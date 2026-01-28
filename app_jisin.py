import requests
import json
from datetime import datetime
import time as tm
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def earthquake_search():
    result.delete("1.0", tk.END)
    period_s = f"{combo_s_y.get()}/{combo_s_m.get()}/{combo_s_d.get()}"
    period_e = f"{combo_e_y.get()}/{combo_e_m.get()}/{combo_e_d.get()}"

    print(f"検索を開始します:{period_s}～{period_e}")
    try:
        start_dt = datetime.strptime(period_s, "%Y/%m/%d")
        end_dt = datetime.strptime(period_e, "%Y/%m/%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        print("日付が正しくありません。")
        return

    finished = False
    for offset_num in range(0, 1000, 100):
        if finished: break
        url = f"https://api.p2pquake.net/v2/history?codes=551&limit=100&offset={offset_num}"
        response = requests.get(url)
        kekka = json.loads(response.text)

        for data in kekka:
            try:
                # 過去データの終了判定
                time_val = data['time']
                time_short = time_val[:19] # APIから届く時間に「ミリ秒」がある時とない時があるため、秒まで（19文字）を切り出す
                eq_dt = datetime.strptime(time_short, "%Y/%m/%d %H:%M:%S")
                if eq_dt < start_dt:
                    message = f"{start_dt}より古いデータは取得できないため検索を終了します"
                    result.insert(tk.END,message)
                    root.update()
                    finished = True
                    break

                # 出力データの取得
                place = data['earthquake']['hypocenter']['name']
                max = data['earthquake']['maxScale']/10
                mag = data['earthquake']['hypocenter']['magnitude']

                # 取得データ不明時の対応
                if mag == -1:
                    mag = "不明"
                if place == '':
                    place = "調査中"

                # 期間の判定、地震規模の絞り込み
                if (isinstance(max, (int, float)) and max >= 3) or \
                       (isinstance(mag, (int, float)) and mag >= 5):
                        res = f'{time_val}{place}マグニチュード{mag}、最大震度{max}\n'
                        result.insert(tk.END, res)
                        root.update()
            except KeyError:
                pass
        tm.sleep(1.0)

    if not result.get("1.0", tk.END).strip():
        result.insert(tk.END, "指定された条件で地震は見つかりませんでした。")
    
    messagebox.showinfo("検索終了", "検索が完了しました！")

def my_reset():
    combo_s_y.set(years[0])
    combo_s_m.set(months[0])
    combo_s_d.set(days[0])
    combo_e_y.set(years[0])
    combo_e_m.set(months[0])
    combo_e_d.set(days[0])
    result.delete("1.0",tk.END)


root = tk.Tk()
root.title("地震検索システム")
root.minsize(530,600)

this_year = datetime.now().year
years = [str(this_year - i) for i in range(10)]
months = [f'{i:02}' for i in range(1,13)]
days = [f'{i:02}' for i in range(1,32)]

bi=("MSゴシック", "13", "")
sm=("MSゴシック", "10", "")

title = tk.Label(text="マグニチュード３、最大震度５以上を検索します", font=bi)
title_s = tk.Label(text="【検索開始日】", font=sm)

combo_s_y = ttk.Combobox(values=years)
combo_s_y.set(str(this_year))
combo_s_m = ttk.Combobox(values=months)
combo_s_m.set("01")
combo_s_d = ttk.Combobox(values=days)
combo_s_d.set("01")

text = tk.Label(text="～", font=bi)

title_e = tk.Label(text="【検索終了日】", font=sm)
combo_e_y = ttk.Combobox(values=years)
combo_e_y.set(str(this_year))
combo_e_m = ttk.Combobox(values=months)
combo_e_m.set("01")
combo_e_d = ttk.Combobox(values=days)
combo_e_d.set("01")

btn = tk.Button(text="検索", command=earthquake_search)

result = tk.Text(width=70, height=25)
r_scroll = tk.Scrollbar(orient="vertical",command=result.yview)
result["yscrollcommand"] = r_scroll.set

btn2 = tk.Button(text='リセット', command=my_reset)

title.place(x=80,y=10)
title_s.place(x=80,y=50)
combo_s_y.place(x=80,y=80)
combo_s_m.place(x=80,y=100)
combo_s_d.place(x=80,y=120)

text.place(x=250,y=100)

title_e.place(x=300,y=50)
combo_e_y.place(x=300,y=80)
combo_e_m.place(x=300,y=100)
combo_e_d.place(x=300,y=120)

btn.place(x=250,y=160)

result.place(x=18,y=200)
r_scroll.place(x=505, y=200, height=335)

btn2.place(x=250,y=550)


root.mainloop()