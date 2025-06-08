import os
import yfinance as yf
import pandas as pd

# Funkcija za pridobivanje podatkov za MSFT
def get_and_save_data(ticker, start_date, end_date, output_dir):
    try:
        # Pridobi podatke za MSFT
        data = yf.download(ticker, start=start_date, end=end_date)
        print(f"Podatki za {ticker} pridobljeni.")

        # Nastavi Date kot indeks
        data['Date'] = data.index

        # Izberi samo stolpce Date in Close
        data = data[['Date', 'Close']]



        # Odstrani drugo vrstico (index 1)
        data = data.drop(data.index[1])

        # Shrani v CSV z imenom MSFT_data.csv
        output_file = os.path.join(output_dir, 'MSFT4_data.csv')
        data.to_csv(output_file, index=False)
        print(f"Podatki za {ticker} shranjeni v {output_file}.")
    except Exception as e:
        print(f"Napaka pri pridobivanju podatkov za {ticker}: {e}")

# Glavni del
if __name__ == "__main__":
    # Izhodna mapa
    output_dir = '.'

    # Preveri, ali mapa obstaja, sicer jo ustvari
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ticker za MSFT
    ticker = "MSFT"

    # Obdobje
    start_date = "1986-03-13"
    end_date = "2025-01-01"

    # Pridobi in shrani podatke za MSFT
    get_and_save_data(ticker, start_date, end_date, output_dir)
