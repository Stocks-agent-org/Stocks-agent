import requests
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient  # <-- Dodano

# MongoDB povezava
client = MongoClient("mongodb+srv://haracicervin:<PASSWORD>@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Uporabi svojo povezavo če uporabljaš MongoDB Atlas
db = client["delnice_db"]
collection = db["podatki_o_delnicah"]

API_KEY = "API_KEY"
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_data():
    stock_symbol = entry.get().upper()
    if not stock_symbol:
        messagebox.showwarning("Napaka", "Prosim, vnesite simbol delnice!")
        return

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
            avg_price = sum(prices) / len(prices)
            trend = "Trenutna cena je pod povprecjem" if latest_price < avg_price else "Trenutna cena je nad povprecjem"
            future_prices = predict_future(prices)

            # ---  MongoDb ---
            dokument = {
                "symbol": stock_symbol,
                "cas": latest_timestamp,
                "open": float(latest_data["1. open"]),
                "high": float(latest_data["2. high"]),
                "low": float(latest_data["3. low"]),
                "close": float(latest_data["4. close"]),
                "volume": int(latest_data["5. volume"]),
                "avg_price_5": avg_price,
                "trend": trend
            }
            print("POŠILJAM V MONGO:", dokument) 
            collection.insert_one(dokument)
            # ----------------------------------

            result_label.config(
                text=f"Podatki za {stock_symbol} ob {latest_timestamp}\n"
                     f"Najvišja cena: {latest_data['2. high']} USD\n"
                     f"Najnižja cena: {latest_data['3. low']} USD\n"
                     f"Volumen: {latest_data['5. volume']}\n"
                     f"Zadnja cena: {latest_price} USD\n"
                     f"Povprečna cena (5x): {avg_price:.2f} USD\n"
                     f"Napoved: {trend}"
            )
            plot_graph(prices, future_prices)
        else:
            messagebox.showerror("Napaka", "Ni podatkov za izbrano delnico.")
    else:
        messagebox.showerror("Napaka", f"API napaka: {response.status_code}")

def predict_future(prices):
    x = np.arange(len(prices))
    y = np.array(prices)
    coeffs = np.polyfit(x, y, 1)
    trend_line = np.poly1d(coeffs)
    future_x = np.arange(len(prices), len(prices) + 3)
    future_prices = trend_line(future_x)
    return future_prices

def plot_graph(prices, future_prices):
    plt.clf()
    x_past = np.arange(len(prices))
    x_future = np.arange(len(prices), len(prices) + len(future_prices))
    plt.plot(x_past, prices, "bo-", label="Zgodovinske cene")
    plt.plot(x_future, future_prices, "ro--", label="Napovedane cene")
    plt.xlabel("Časovni intervali")
    plt.ylabel("Cena (USD)")
    plt.title("Napoved gibanja cen delnice")
    plt.legend()
    canvas.draw()

# ---Uporabniški vmesnik -----
root = tk.Tk()
root.title("Delniški podatki")
root.geometry("500x600")

tk.Label(root, text="Vnesi simbol delnice:").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="Pridobi podatke", command=get_stock_data).pack(pady=10)
result_label = tk.Label(root, text="", justify="left")
result_label.pack(pady=10)

fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
