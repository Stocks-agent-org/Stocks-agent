import os
import yfinance as yf
import pandas as pd
import requests

# Funkcija za pridobivanje seznamov kriptovalut iz CoinGecko
def get_crypto_tickers():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',  # Pridobi podatke v USD
        'order': 'market_cap_desc',  # Razvrsti po tržni kapitalizaciji
        'per_page': 10,  # Prvih 10 kriptovalut (lahko prilagodiš)
        'page': 1  # Stran 1
    }
    response = requests.get(url, params=params)
    cryptos = response.json()

    # Pridobi kriptovalute (simboli)
    tickers = [crypto['id'] for crypto in cryptos]
    return tickers

# Funkcija za pridobivanje in shranjevanje mesečnih podatkov za vsako kriptovaluto
def get_and_save_data(tickers, start_date, end_date, output_dir):
    for ticker in tickers:
        try:
            # Pridobi podatke za posamezno kriptovaluto (uporaba yfinance z "symbol-USD")
            data = yf.download(f'{ticker}-USD', start=start_date, end=end_date)
            print(f"Podatki za {ticker} pridobljeni.")

            # Nastavi Date kot indeks
            data['Date'] = data.index

            # Izberi samo stolpce Date in Close
            data = data[['Date', 'Close']]

            # Poskrbi, da bo podatek le za vsak mesec
            data = data.resample('M').last()

            # Shrani v CSV z imenom tickerja v mapi 'crypto'
            data.to_csv(os.path.join(output_dir, f'{ticker}_monthly.csv'), index=False)
            print(f"Podatki za {ticker} shranjeni v {output_dir}/{ticker}_monthly.csv.")
        except Exception as e:
            print(f"Napaka pri pridobivanju podatkov za {ticker}: {e}")

# Glavni del
if __name__ == "__main__":
    # Izhodna mapa
    output_dir = 'crypto'

    # Preveri, ali mapa za kriptovalute obstaja, sicer jo ustvari
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Pridobi seznam kriptovalut
    crypto_tickers = get_crypto_tickers()

    # Zaenkrat samo prvih 10
    first_10 = crypto_tickers[:10]

    # Obdobje
    start_date = "2020-01-01"
    end_date = "2023-01-01"

    # Pridobi in shrani podatke za vsako kriptovaluto
    get_and_save_data(first_10, start_date, end_date, output_dir)
