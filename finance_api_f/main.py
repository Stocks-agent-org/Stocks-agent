import yfinance as yf

# Funkcija za pridobivanje podatkov o delnici
def get_stock_data(tickers, start_date, end_date):
    if not tickers:
        print("Prosim, vnesite vsaj en ticker!")
        return

    # Preverimo vsak ticker posebej
    for ticker_symbol in tickers:
        ticker_symbol = ticker_symbol.strip().upper()  # Preverimo in očistimo simbol
        try:
            # Uporabimo yfinance.download za pridobivanje mesečnih podatkov v določenem obdobju
            data = yf.download(ticker_symbol, start=start_date, end=end_date, interval='1mo')  # Mesečni interval

            if data.empty:
                print(f"Ni podatkov za ticker: {ticker_symbol}")
            else:
                print(f"\nPodatki za {ticker_symbol} od {start_date} do {end_date}:")
                for date, row in data.iterrows():  # Iteriramo po mesecih
                    print(f"\nDatum: {date.strftime('%Y-%m-%d')}")
                    print(f"Zadnja cena: {row['Close']} USD")
                    print(f"Najvišja cena: {row['High']} USD")
                    print(f"Najnižja cena: {row['Low']} USD")
                    print(f"Volumen: {row['Volume']}")
                    print("-" * 50)

        except Exception as e:
            print(f"Napaka pri pridobivanju podatkov za {ticker_symbol}: {str(e)}")

# Seznam tickerjev, ki jih želimo preveriti
tickers = ["AAPL", "GOOG", "MSFT"]  # Primer tickerjev

# Nastavimo obdobje (datum začetka in konca)
start_date = "2020-01-01"
end_date = "2023-01-01"

# Klic funkcije za pridobivanje podatkov
get_stock_data(tickers, start_date, end_date)
