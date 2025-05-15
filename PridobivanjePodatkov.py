import requests
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient  
from lstm_predictor import predict_lstm

# ------------------- Povezava z MongoDB -------------------
mongo_url = "mongodb+srv://haracicervin:password@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_url)
db = client["delnice_db"]
collection = db["podatki_o_delnicah"]

API_KEY = "UO0OIPK3VT2AUW8W"
BASE_URL = "https://www.alphavantage.co/query"

# ------------------- Funkcija za prikaz grafa -------------------
def plot_graph(close_prices, lstm_price, dates, parent): 
    fig, ax = plt.subplots(figsize=(6, 3))
    x_past = dates  

    ax.plot(x_past, close_prices, "bo-", label="Zgodovinske cene")
    ax.plot(dates[-1], lstm_price, "ro", label=f"LSTM napoved: {lstm_price:.2f} USD")
    ax.plot(
        [dates[-1], "LSTM"], 
        [close_prices[-1], lstm_price],
        "r--", linewidth=2
    )

    xticks_to_show = [i for i in range(len(dates)) if i % 7 == 0]
    xtick_labels = [dates[i] if i in xticks_to_show else "" for i in range(len(dates))]

    ax.set_xticks(np.arange(len(dates)))
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right", fontsize=8)



    ax.set_xlabel("Datum")
    ax.set_ylabel("Cena (USD)")
    ax.set_title("Zgodovinske cene in LSTM napoved")
    for i, tick in enumerate(ax.xaxis.get_major_ticks()):
        if i % 7 == 0:
            tick.tick1line.set_markersize(10)  
            tick.tick2line.set_markersize(10)  
            tick.tick1line.set_linewidth(1.5)
            tick.tick2line.set_linewidth(1.5)

    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    fig.tight_layout()
    canvas.draw()
    canvas.get_tk_widget().pack()

# ------------------- Funkcija za pridobitev podatkov -------------------
def get_stock_data():
    stock_symbol = entry.get().upper()
    if not stock_symbol:
        messagebox.showwarning("Napaka", "Prosim, vnesite simbol delnice!")
        return

    documents = list(collection.find({"symbol": stock_symbol}))
    if not documents:
        messagebox.showerror("Napaka", f"Ni podatkov za simbol {stock_symbol}.")
        return

    close_prices = []
    dates = []
    for doc in documents: 
        if "close" in doc and "date" in doc:
            close_prices.append(doc["close"])
            dates.append(doc["date"])

    sorted_data = sorted(zip(dates, close_prices), key=lambda x: x[0])
    dates, close_prices = zip(*sorted_data)

    if not close_prices:
        messagebox.showerror("Napaka", "Ni dovolj zgodovinskih podatkov.")
        return

    avg_close_price = sum(close_prices) / len(close_prices)

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": stock_symbol,
        "interval": "5min",
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        time_series = data.get("Time Series (5min)", {})

        if time_series:
            timestamps = list(time_series.keys())[:5]
            prices = [float(time_series[t]["4. close"]) for t in timestamps]

            latest_timestamp = timestamps[0]
            latest_data = time_series[latest_timestamp]
            latest_price = prices[0]
            trend = "Trenutna cena je pod povprečjem" if latest_price < avg_close_price else "Trenutna cena je nad povprečjem"

            dokument = {
                "symbol": stock_symbol,
                "cas": latest_timestamp,
                "date": latest_timestamp.split(" ")[0],  
                "open": float(latest_data["1. open"]),
                "high": float(latest_data["2. high"]),
                "low": float(latest_data["3. low"]),
                "close": float(latest_data["4. close"]),
                "volume": int(latest_data["5. volume"]),
            }
            collection.insert_one(dokument)

            lstm_price = predict_lstm(stock_symbol, mongo_url)

            for widget in root.winfo_children():
                if hasattr(widget, "is_dynamic") and widget.is_dynamic:
                    widget.destroy()

            # --- Prikaz rezultatov ---
            result_frame = ttk.Frame(root, padding=10, style="Card.TFrame")
            result_frame.place(relx=0.5, rely=0.25, anchor="n")
            result_frame.is_dynamic = True

            result_label = ttk.Label(result_frame, text="", justify="center", wraplength=550, background="#ffffff", padding=10, relief="ridge")
            result_label.pack()

            result_text = (
                f"Podatki za {stock_symbol} ob {latest_timestamp}\n"
                f"Cena na začetku dneva: {latest_data['1. open']} USD\n"
                f"Najvišja cena na današnji dan: {latest_data['2. high']} USD\n"
                f"Najnižja cena na današnji dan: {latest_data['3. low']} USD\n"
                f"Število trgovnaih delnic (volumen): {latest_data['5. volume']}\n"
                f"Zadnja cena: {latest_price} USD\n"
                f"Povprečna close cena : {avg_close_price:.2f} USD\n"
                f"{trend}\n"
                f"Napoved: {lstm_price:.2f} USD" if lstm_price else "\nNapoved: premalo podatkov"
            )
            result_label.config(text=result_text)

            # --- Prikaz grafa ---
            graph_frame = ttk.Frame(root)
            graph_frame.place(relx=0.5, rely=0.6, anchor="n")
            graph_frame.is_dynamic = True

            plot_graph(close_prices, lstm_price or latest_price, dates, graph_frame)  
        else:
            messagebox.showerror("Napaka", "Ni podatkov za izbrano delnico.")
    else:
        messagebox.showerror("Napaka", f"API napaka: {response.status_code}")

# ------------------- GUI -------------------
root = tk.Tk()
root.title("Delniški podatki")
root.geometry("600x800")
root.configure(bg="#e6f2ff")

style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#e6f2ff")
style.configure("TLabel", background="#e6f2ff", font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), background="#e6f2ff", foreground="#003366")
style.configure("Card.TFrame", background="#ffffff", borderwidth=1, relief="solid")
style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#cce6ff", foreground="black")
style.map("TButton", background=[("active", "#99ccff")])

# ------------------- Vnos -------------------
main_frame = ttk.Frame(root)
main_frame.place(relx=0.5, rely=0.05, anchor="n")

input_frame = ttk.Frame(main_frame, padding=20)
input_frame.pack()

ttk.Label(input_frame, text="Vnesi simbol delnice:", style="Header.TLabel").pack(pady=(0, 10))

entry = ttk.Entry(input_frame, width=30, font=("Segoe UI", 11))
entry.pack(pady=5)

ttk.Button(input_frame, text="Pridobi podatke", command=get_stock_data).pack(pady=10)

root.mainloop()