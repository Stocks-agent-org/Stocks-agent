import requests
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient  
from lstm_predictor import predict_lstm

client = MongoClient("mongodb+srv://haracicervin:PASSWORD@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  
db = client["delnice_db"]
collection = db["podatki_o_delnicah"]

API_KEY = "API_KEY"
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_data():
    stock_symbol = entry.get().upper()
    if not stock_symbol:
        messagebox.showwarning("Napaka", "Prosim, vnesite simbol delnice!")
        return

    documents = collection.find({"symbol": stock_symbol})
    
    if not documents:
        messagebox.showerror("Napaka", f"Ni podatkov za simbol {stock_symbol}.")
        return

    # Pridobim vse "close" cene za ta simbol 
    close_prices = [doc["close"] for doc in documents]
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
            trend = "Trenutna cena je pod povprecjem" if latest_price < avg_close_price else "Trenutna cena je nad povprecjem"        

            dokument = {
                "symbol": stock_symbol,
                "cas": latest_timestamp,
                "open": float(latest_data["1. open"]),
                "high": float(latest_data["2. high"]),
                "low": float(latest_data["3. low"]),
                "close": float(latest_data["4. close"]),
                "volume": int(latest_data["5. volume"]),
            }
            print("POŠILJAM V MONGO:", dokument) 
            collection.insert_one(dokument)


            lstm_price = predict_lstm(stock_symbol, "mongodb+srv://haracicervin:PASSWORD@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # vstavi svoj mongo url
            if lstm_price:
                result_label.config(text=result_label.cget("text") + f"\nLSTM napoved: {lstm_price:.2f} USD")
            else:
                result_label.config(text=result_label.cget("text") + "\nLSTM napoved: premalo podatkov")

            result_label.config(
                text=f"Podatki za {stock_symbol} ob {latest_timestamp}\n"
                     f"Cena na začetku dneva: {latest_data['1. open']} USD\n"
                     f"Najvišja cena na današnji dan: {latest_data['2. high']} USD\n"
                     f"Najnižja cena na današnji dan: {latest_data['3. low']} USD\n"
                     f"Število trgovnaih delnic (volumen): {latest_data['5. volume']}\n"
                     f"Zadnja cena: {latest_price} USD\n"
                     f"Povprečna close cena : {avg_close_price:.2f} USD\n"
                     f"Napoved glede na povprecje: {trend}\n"
                     f"LSTM napoved: {lstm_price}"
            )
            plot_graph(close_prices, lstm_price)
        else:
            messagebox.showerror("Napaka", "Ni podatkov za izbrano delnico.")
    else:
        messagebox.showerror("Napaka", f"API napaka: {response.status_code}")


def plot_graph(close_prices, lstm_price):
    plt.clf()  

    ax = plt.gca()  

    x_past = np.arange(len(close_prices))
    ax.plot(x_past, close_prices, "bo-", label="Zgodovinske cene")

    # Določim zadnjo ceno kot LSTM napoved 
    ax.plot(len(close_prices), lstm_price, "ro", label=f"LSTM napoved: {lstm_price:.2f} USD")

    ax.set_xlabel("Časovni intervali")
    ax.set_ylabel("Cena (USD)")
    ax.set_title("Zgodovinske cene in LSTM napoved")
    ax.legend()

    canvas.draw()


# ---Uporabniški vmesnik -----
root = tk.Tk()
root.title("Delniški podatki")
root.geometry("500x800")

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
