import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from price_predictor import predict_price
from grow_predictor import predict_lstm_hybrid
from datetime import datetime, timedelta
from datetime import datetime, timedelta

# ------------------- MongoDB povezava -------------------
mongo_url = "mongodb+srv://haracicervin:PASSWORD@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_url)
db = client["delnice_db"]
latest_price = 0
opomba_smer = "" 

clear_button = None  
API_KEY = "PASSWORD"
BASE_URL = "https://www.alphavantage.co/query"
current_symbol = None
refresh_button = None
loading_label = None 
loading_label_main = None
discord_button = None
hour_spin = None
top_frame  = None

root = tk.Tk()
hour_var = tk.StringVar(value="15")
minute_var = tk.StringVar(value="54")

TitleDiscord = None
TitleDelnice = None

minute_spin = None
# ------------------- Prikaz grafa -------------------
def plot_graph(close_prices, future_price, dates, parent):

    fig, ax = plt.subplots(figsize=(6, 4.5))
    
    ax.plot(dates, close_prices, "bo-", label="Zgodovinske cene")

    # Dodamo eno točko za napovedano ceno malo desno od zadnje točke
    x_vals = list(range(len(dates)))
    future_x = x_vals[-1] + 1
    ax.plot(future_x, future_price, "ro", label=f"Napoved: {future_price:.2f} USD")

    # Risanje povezovalne črte med zadnjo ceno in napovedjo
    ax.plot([x_vals[-1], future_x], [close_prices[-1], future_price], "r--", linewidth=2)

    # Oznake na osi x
    xticks = x_vals + [future_x]
    xtick_labels = dates + ["Napoved"]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Datum")
    ax.set_ylabel("Cena (USD)")
    ax.set_title("Zgodovinske cene in napovedana cena")
    ax.legend(loc="lower left", fontsize=9)

    # Poudari vsako 7. kljukico
    for i, tick in enumerate(ax.xaxis.get_major_ticks()):
        if i % 7 == 0:
            tick.tick1line.set_markersize(10)
            tick.tick2line.set_markersize(10)
            tick.tick1line.set_linewidth(1.5)
            tick.tick2line.set_linewidth(1.5)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    fig.tight_layout()
    canvas.draw()
    canvas.get_tk_widget().pack()

# ------------------- Pridobitev podatkov -------------------
def prikazi_info_okvir(stock_symbol, info_frame):
    collection = db[stock_symbol]
    latest_doc = collection.find_one({"symbol": stock_symbol}, sort=[("date", -1)])
    if not latest_doc:
        messagebox.showerror("Napaka", f"Ni podatkov v bazi za simbol {stock_symbol}.")
        return

    all_docs = list(collection.find({"symbol": stock_symbol}))
    close_prices = [doc["close"] for doc in all_docs if "close" in doc]
    avg_close_price = sum(close_prices) / len(close_prices)
    latest_price = latest_doc["close"]

    info_text = (
        f"📈 Podatki iz baze za {stock_symbol} (datum: {latest_doc['date']})\n\n"
        f"🔹 Cena na začetku dneva: {latest_doc['open']} USD\n"
        f"🔹 Najvišja današnja cena: {latest_doc['high']} USD\n"
        f"🔹 Najnižja današnja cena: {latest_doc['low']} USD\n"
        f"🔹 Zadnja cena: {latest_price} USD\n"
        f"🔹 Povprečna zgodovinska cena: {avg_close_price:.2f} USD\n"
    )

    info_label = ttk.Label(
        info_frame,
        text=info_text,
        justify="left",
        wraplength=550,
        background="#ffffff",
        padding=10,
        relief="ridge"
    )
    info_label.is_dynamic = True
    info_label.pack()

# ------------------- Zagon test.py in prikaz rezultatov -------------------
def run_test_script(stock_symbol):
    global current_symbol
    global loading_label_main
    global refresh_button
    global clear_button
    current_symbol = stock_symbol
    global discord_button
    global minute_spin
    global hour_spin
    global top_frame
    global TitleDiscord
    global TitleDelnice

    button_frame.pack_forget() 
    TitleDelnice.pack_forget() 

    TitleDiscord = tk.Label(root, text="Nastavi čas prejemanja podatkov", bg="#e6f2ff", font=("Arial", 16))
    TitleDiscord.pack(side="top", pady=10)

    top_frame = tk.Frame(root)
    top_frame.configure(bg="#e6f2ff")
    top_frame.pack(side="top", pady=15)

# Ure

    hour_spin = tk.Spinbox(top_frame, from_=0, to=23, wrap=True, textvariable=hour_var, width=5, format="%02.0f")
    hour_spin.pack(side="left", padx=5)

    # Minute
    minute_spin = tk.Spinbox(top_frame, from_=0, to=59, wrap=True, textvariable=minute_var, width=5, format="%02.0f")
    minute_spin.pack(side="left", padx=5)

    # Discord gumb
    discord_button = ttk.Button(top_frame, text="Start", command=start_schedule)
    discord_button.pack(side="left", padx=10)

    root.update()
    clear_button = ttk.Button(
        root,
        text="⬅️ NAZAJ",
        command=lambda: destroy_dynamic_widgets(root),
    )

    # Stilizacija zelenega gumba
    style = ttk.Style()
    style.configure('Green.TButton', background='#4CAF50', foreground='white')
    clear_button.config(style='Green.TButton')

    # Postavitev gumba levo zgoraj (x=10, y=10, lahko prilagodiš)
    clear_button.place(x=10, y=10)

    # Glavni okvir
    main_display_frame = ttk.Frame(root, padding=10)
    main_display_frame.place(relx=0.5, rely=0.15, anchor="n")
    main_display_frame.is_dynamic = True

    # OKVIR: INFO O DELNICI – TAKOJŠNJI PRIKAZ
    info_frame = ttk.Frame(main_display_frame, style="Card.TFrame", padding=10)
    info_frame.pack(fill="x", pady=(0, 10))
    prikazi_info_okvir(stock_symbol, info_frame)
    main_display_frame.info_frame = info_frame
    root.update_idletasks()

    # Indikator nalaganja
    if loading_label_main:
        loading_label_main.destroy()

    loading_label_main = ttk.Label(
        root,
        text="⏳ Računanje podatkov...",
        font=("Segoe UI", 16, "bold"),
        background="#e6f2ff",
        foreground="#003366"
    )
    loading_label_main.place(relx=0.5, rely=0.5, anchor="center")
    root.update_idletasks()

    # Gumb za osvežitev
    if refresh_button:
        refresh_button.destroy()

    refresh_button = ttk.Button(
        bottom_button_frame,
        text="🔄 Osveži podatke",
        command=prompt_refresh
    )
    refresh_button.pack(pady=10)

    # Poženi test.py
    stock_dir = os.path.join("delnice", stock_symbol)
    script_path = os.path.join(stock_dir, "test.py")

    if not os.path.exists(script_path):
        messagebox.showerror("Napaka", f"Datoteka test.py ni najdena za {stock_symbol}")
        return

    try:
        result = subprocess.run(
            ["python", "test.py"],
            cwd=stock_dir,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )

        output_lines = result.stdout.strip().splitlines()
        filtered_lines = [line for line in output_lines if "Napoved" in line]

        napovedi = []
        for line in filtered_lines:
            match = re.search(r"[-+]?\d*\.\d+|\d+", line)
            if match:
                napovedi.append(float(match.group()))

        output = "\n".join(filtered_lines)

        if napovedi[1] > latest_price:
            primerjava = "Model meni, da bo cena delnice narasla"
            primerjavaOpomba = "višja"
        elif napovedi[1] < latest_price:
            primerjava = "Model meni, da bo cena delnice padla."
            primerjavaOpomba = "nižja"
        else:
            primerjava = "Model meni, da se cena delnice ne bo spremenila"
            primerjavaOpomba = "enaka"

        text = (
            f"🔹Napovedana cena z GRU modelom: {napovedi[1]}\n"
            f"🔹{primerjava}\n"
        )

    except subprocess.CalledProcessError as e:
        output = f"Napaka pri izvajanju skripte:\n{e.stderr or e.stdout}"
        text = output
        primerjavaOpomba = "neznana"
        napovedi = []

    # Glavni vsebinski del
    bottom_frame = ttk.Frame(main_display_frame)
    bottom_frame.pack(fill="both", expand=True)

    # Leva stran – LSTM + grafi
    left_frame = ttk.Frame(bottom_frame, style="Card.TFrame", padding=10)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    main_display_frame.left_frame = left_frame
    left_frame.is_dynamic = True

    left_title = ttk.Label(
        left_frame,
        text="📊 Napoved nad trenutnimi podatki",
        style="Header.TLabel"
    )
    left_title.pack(pady=(0, 10), anchor="center")
    left_title.is_dynamic = True
    # Desna stran – test.py rezultati
    right_frame = ttk.Frame(bottom_frame, style="Card.TFrame", padding=10)
    right_frame.pack(side="right", fill="both", expand=True)
    main_display_frame.right_frame = right_frame
    right_frame.is_dynamic = True

    right_top_frame = ttk.Frame(right_frame, style="Card.TFrame", padding=10)
    right_top_frame.pack(fill="both", expand=True, pady=(0, 5))
    right_top_frame.is_dynamic = True

    right_bottom_frame = ttk.Frame(right_frame, style="Card.TFrame", padding=10)
    right_bottom_frame.pack(fill="both", expand=True)
    right_bottom_frame.is_dynamic = True
    # Dodatno besedilo
    
    right_title = ttk.Label(
        right_top_frame,
        text="🧪 Napoved nad zgodovisnkimi podatki",
        style="Header.TLabel"
    )
    right_title.pack(pady=(0, 10), anchor="center")
    right_title.is_dynamic = True
    # Izpis rezultata iz test.py
    test_label = ttk.Label(
        right_top_frame,
        text=text,
        justify="left",
        wraplength=600,
        background="#ffffff",
        padding=10,
        relief="ridge"
    )
    test_label.pack()
    test_label.is_dynamic = True

    # Skrij indikator nalaganja
    if loading_label_main:
        loading_label_main.destroy()
        loading_label_main = None

    # Naloži dokumente in prikaži okvire modelov
    all_docs = list(db[stock_symbol].find({"symbol": stock_symbol}))

    future_price = predict_price(stock_symbol, mongo_url)
    grow = predict_lstm_hybrid(stock_symbol, mongo_url)

    if grow is None:
        smer_besedilo = "Premalo podatkov za oceno smeri trenda."
        opomba_smer = ""
    else:
        smer = "narastla" if grow['direction_lstm_gru'] else "padla"
        smer_besedilo = f"Model meni, da bo cena delnice {smer}."
        opomba_smer = "narašča" if grow['direction_lstm_gru'] else "pada"

    lstm_text = (
        f"🔹Napovedana cena z GRU modelom : {future_price:.2f} USD\n"
        f"🔹{smer_besedilo}"
    )

    lstm_label = ttk.Label(
        left_frame,
        text=lstm_text,
        justify="left",
        background="#ffffff",
        padding=10,
        relief="ridge"
    )
    lstm_label.is_dynamic = True
    lstm_label.pack(pady=(0, 10))

    N = 25
    dates = [doc["date"] for doc in all_docs if "close" in doc][-N:]
    close_prices = [doc["close"] for doc in all_docs if "close" in doc][-N:]
    plot_graph(close_prices, future_price, dates, left_frame)

    dodatno_besedilo = f"📌 Trenutni trend kaže, da cena {opomba_smer}, vendar model, ki obdeluje vse zgodovinske cene sporoča, da je cena v zgodovini že bila {primerjavaOpomba}."
    dodatni_label = ttk.Label(
        right_bottom_frame,
        text=dodatno_besedilo,
        justify="left",
        wraplength=600,
        background="#ffffff",
        padding=10,
        relief="ridge"
    )
    dodatni_label.pack()
    dodatni_label.is_dynamic = True

    return (dodatno_besedilo,text,lstm_text)

def osvezi_podatke(stock_symbol):
    destroy_dynamic_widgets(root)
    print("osvezujem")
    collection = db[stock_symbol]
    today = datetime.today().date()
    days_back = 75  # dodaten buffer v primeru vikendov/brez trgovalnih dni
    start_date = today - timedelta(days=days_back)

    # 1. Pridobi obstoječe datume v bazi
    existing_docs = list(collection.find({"symbol": stock_symbol}))
    existing_dates = {doc["date"] for doc in existing_docs}

    # 2. Kliči Alpha Vantage API za zadnjih 75 dni
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_symbol,
        "outputsize": "compact",
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)


    if response.status_code != 200:
        messagebox.showerror("Napaka", "Napaka pri klicu API-ja.")
        return

    data = response.json().get("Time Series (Daily)", {})
    if not data:
        messagebox.showerror("Napaka", "API ni vrnil podatkov.")
        return

    new_data = []
    for date_str, daily_data in data.items():
        if date_str not in existing_dates and datetime.strptime(date_str, "%Y-%m-%d").date() >= start_date:
            new_data.append({
                "symbol": stock_symbol,
                "date": date_str,
                "open": float(daily_data["1. open"]),
                "high": float(daily_data["2. high"]),
                "low": float(daily_data["3. low"]),
                "close": float(daily_data["4. close"]),
                "volume": int(daily_data["5. volume"]),
            })

    if new_data:
        new_data.sort(key=lambda x: x["date"])  # 🔽 Uredi po datumu naraščajoče
        collection.insert_many(new_data)

    # 3. Po osvežitvi – izbriši vse starejše od 50 zadnjih dni
    all_docs = list(collection.find({"symbol": stock_symbol}))
    sorted_docs = sorted(all_docs, key=lambda x: x["date"], reverse=True)
    keep_latest = sorted_docs[:50]
    keep_ids = {doc["_id"] for doc in keep_latest}
    to_delete = [doc["_id"] for doc in sorted_docs if doc["_id"] not in keep_ids]

    if to_delete:
        collection.delete_many({"_id": {"$in": to_delete}})

# ------------------- GUI -------------------


root.attributes('-fullscreen', True)
root.title("Delniški podatki")
root.geometry("600x900")
root.configure(bg="#e6f2ff")

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#e6f2ff")
style.configure("TLabel", background="#e6f2ff", font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), background="#e6f2ff", foreground="#003366")
style.configure("Card.TFrame", background="#ffffff", borderwidth=1, relief="solid")
style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#cce6ff", foreground="black")
style.map("TButton", background=[("active", "#99ccff")])

# ------------------- Gumbi za izbiro delnice -------------------


main_frame = ttk.Frame(root)
# Okvir na dnu za gumb "Osveži podatke"
bottom_button_frame = ttk.Frame(root)
bottom_button_frame.place(relx=0.5, rely=0.98, anchor="s")
# Okvir za gumb za zapiranje, ki ga poravnamo desno zgoraj
top_right_frame = ttk.Frame(root)
top_right_frame.place(relx=1.0, rely=0.0, anchor="ne")
TitleDelnice = tk.Label(root, text="Izberi delnico", bg="#e6f2ff",font=("Arial", 16))
TitleDelnice.pack(side="top", pady=20)
# Definicija stila za rdeč gumb
style.configure("Close.TButton", font=("Segoe UI", 10, "bold"), background="#ff4d4d", foreground="white")
style.map("Close.TButton", background=[("active", "#ff1a1a")])

# Gumb za zapiranje
close_button = ttk.Button(
    top_right_frame,
    text="❌ Zapri",
    style="Close.TButton",
    command=root.destroy
)
close_button.pack(padx=10, pady=10)

main_frame.place(relx=0.5, rely=0.01, anchor="n")


input_frame = ttk.Frame(main_frame, padding=20)
input_frame.pack()


stock_dir = "delnice"
if not os.path.exists(stock_dir):
    os.makedirs(stock_dir)

stock_names = [name for name in os.listdir(stock_dir) if os.path.isdir(os.path.join(stock_dir, name))]

button_frame = ttk.Frame(input_frame)
button_frame.pack(pady=50)

max_columns = 12
for idx, name in enumerate(stock_names):
    row = idx // max_columns
    col = idx % max_columns
    ttk.Button(
        button_frame,
        text=name,
        command=lambda n=name: run_test_script(n)
    ).grid(row=row, column=col, padx=5, pady=5, sticky="ew")

def prompt_refresh():
    global refresh_button

    if current_symbol:
        if refresh_button:
            refresh_button.destroy()
            refresh_button = None


        # 1. Osveži podatke iz API-ja
        osvezi_podatke(current_symbol)

        # 2. Po osvežitvi ponovno prikaži podatke
        run_test_script(current_symbol)

        # 3. Odstrani label "Nalaganje podatkov"
        loading_label.destroy()

    else:
        messagebox.showwarning("Pozor", "Najprej izberi delnico.")


def destroy_dynamic_widgets(parent):
    global clear_button
    global refresh_button
    global discord_frame
    global top_frame 
    global TitleDelnice
    global TitleDiscord
    button_frame.pack(pady=50)
    TitleDelnice.pack(pady=20)

    if clear_button is not None:
        clear_button.place_forget()

    if refresh_button is not None:
       refresh_button.pack_forget()

    if discord_button is not None:
        discord_button.pack_forget()
        hour_spin.pack_forget()
        minute_spin.pack_forget()
        top_frame.pack_forget()
        TitleDiscord.pack_forget()

    for widget in parent.winfo_children():
        destroy_dynamic_widgets(widget)
        if hasattr(widget, "is_dynamic") and widget.is_dynamic:
            print(f"Destroying widget: {widget}")  # Dodaj izpis za debug
            widget.destroy()
    
import tkinter as tk
from tkinter import ttk
import requests
import schedule

webhook_url = "https://discord.com/api/webhooks/1380964304148234240/KgMXIUhJutR5IoffmOmXSD84tZApyrx6FArM-HU1XoBh-L63yPQivjEzuG3b1xDyNctb"

def send_discord_message(message):
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Sporočilo poslano uspešno!")
    else:
        print(f"Napaka pri pošiljanju: {response.status_code}, {response.text}")

def job():
    osvezi_podatke(current_symbol)


    collection = db[current_symbol ]
    latest_doc = collection.find_one({"symbol": current_symbol }, sort=[("date", -1)])
    if not latest_doc:
        messagebox.showerror("Napaka", f"Ni podatkov v bazi za simbol {current_symbol }.")
        return

    all_docs = list(collection.find({"symbol": current_symbol}))
    close_prices = [doc["close"] for doc in all_docs if "close" in doc]
    avg_close_price = sum(close_prices) / len(close_prices)
    latest_price = latest_doc["close"]
    opomba, zgodovinskaNapoved, trenutniTrend = run_test_script(current_symbol)

    info_text = (
        f"📈 Podatki iz baze za {current_symbol } (datum: {latest_doc['date']})\n\n"
        f"🔹 Cena na začetku dneva: {latest_doc['open']} USD\n"
        f"🔹 Najvišja današnja cena: {latest_doc['high']} USD\n"
        f"🔹 Najnižja današnja cena: {latest_doc['low']} USD\n"
        f"🔹 Zadnja cena: {latest_price} USD\n"
        f"🔹 Povprečna zgodovinska cena: {avg_close_price:.2f} USD\n\n"
        f"📈 Napoved nad zgodovinskimi podatki\n"
        f"{zgodovinskaNapoved}\n\n"
        f"📈 Napoved nad trenutnimi podatki\n"
        f"{trenutniTrend}\n\n"
        f"{opomba}\n\n"

    )


    send_discord_message(info_text)



def check_schedule():
    print("Checking schedule...")
    schedule.run_pending()
    root.after(1000, check_schedule)

def start_schedule():
    global hour_var, minute_var  # <-- zelo pomembno!
    try:
        hour = int(hour_var.get())
        minute = int(minute_var.get())
    except ValueError:
        print("Napaka pri pretvorbi ure/minut.")
        return

    selected_time = f"{hour:02}:{minute:02}"
    print(f"Scheduler nastavljen za čas: {selected_time}")
    schedule.every().day.at(selected_time).do(job)
    check_schedule()
    print("Discord scheduler zaženjen!")


root.mainloop()
