import os
import yfinance as yf
import pandas as pd

# Funkcija za pridobivanje vseh ETF-ov iz Wikipedije
def get_etf_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_exchange-traded_funds'
    table = pd.read_html(url)
    tickers = table[0]['Ticker symbol'].tolist()
    # Odstrani prazen vnos, če obstaja
    tickers = [ticker for ticker in tickers if ticker]
    return tickers

# Funkcija za pridobivanje in shranjevanje mesečnih podatkov za vsak ETF
def get_and_save_data(tickers, start_date, end_date, output_dir):
    for ticker in tickers:
        try:
            # Pridobi podatke za posamezen ETF
            data = yf.download(ticker, start=start_date, end=end_date)
            print(f"Podatki za {ticker} pridobljeni.")

            # Nastavi Date kot indeks
            data['Date'] = data.index

            # Izberi samo stolpce Date in Close
            data = data[['Date', 'Close']]

            # Poskrbi, da bo podatek le za vsak mesec
            data = data.resample('M').last()

            # Shrani v CSV z imenom tickerja v mapi 'etf'
            data.to_csv(os.path.join(output_dir, f'{ticker}_monthly.csv'), index=False)
            print(f"Podatki za {ticker} shranjeni v {output_dir}/{ticker}_monthly.csv.")
        except Exception as e:
            print(f"Napaka pri pridobivanju podatkov za {ticker}: {e}")

# Glavni del
if __name__ == "__main__":
    # Izhodna mapa
    output_dir = 'etf'

    # Preveri, ali mapa za ETF-je obstaja, sicer jo ustvari
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Pridobi vse ETF-je
    etf_tickers = get_etf_tickers()

    # Zaenkrat samo prvih 10
    first_10 = etf_tickers[:10]

    # Obdobje
    start_date = "2020-01-01"
    end_date = "2023-01-01"

    # Pridobi in shrani podatke za vsak ETF
    get_and_save_data(first_10, start_date, end_date, output_dir)
