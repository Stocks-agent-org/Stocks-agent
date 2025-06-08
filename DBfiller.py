import requests
import pymongo
from pymongo import MongoClient
import datetime

client = MongoClient("mongodb+srv://haracicervin:HdUwE4OAlBxJV1Qi@cluster0.bun7is9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["delnice_db"]
#collection = db["podatki_o_delnicah"]

API_KEY = "YOUR_API_KEY"  
BASE_URL = "https://www.alphavantage.co/query"

def get_historical_data(stock_symbol):
    """
    Funkcija za pridobivanje zgodovinskih podatkov za določeno delnico
    :param stock_symbol: simbol delnice (npr. "AAPL", "GOOGL")
    :return: seznam zadnjih 50 dni podatkov
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_symbol,
        "apikey": API_KEY,
        "outputsize": "compact"  
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        time_series = data.get("Time Series (Daily)", {})
        
        if time_series:
            historical_data = []
            for date, values in sorted(time_series.items())[-50:]:
                data_point = {
                    "symbol": stock_symbol,
                    "date": date,
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"]),
                }
                historical_data.append(data_point)
            return historical_data
        else:
            print("Ni podatkov za izbrano delnico.")
            return []
    else:
        print(f"Napaka pri pridobivanju podatkov: {response.status_code}")
        return []

def insert_data_into_mongo(historical_data, stock_symbol):
    """
    Funkcija za shranjevanje podatkov v MongoDB v zbirko po imenu delnice
    :param historical_data: seznam podatkov za shranjevanje
    :param stock_symbol: simbol delnice (npr. "AAPL")
    """
    collection = db[stock_symbol]  # Ustvari zbirko z imenom delnice

    if historical_data:
        for data in historical_data:
            existing_record = collection.find_one({
                "symbol": data["symbol"],
                "date": data["date"]
            })

            if existing_record is None:
                collection.insert_one(data)
                print(f"Podatek za {data['symbol']} za {data['date']} je bil uspešno shranjen.")
            else:
                print(f"Podatek za {data['symbol']} za {data['date']} že obstaja.")
    else:
        print("Ni podatkov za shranjevanje.")


def populate_database(stock_symbol):
    """
    Funkcija za nalaganje zgodovinskih podatkov in shranjevanje v MongoDB bazo
    :param stock_symbol: simbol delnice
    """
    print(f"Začenjam nalaganje podatkov za {stock_symbol}...")
    
    historical_data = get_historical_data(stock_symbol)
    insert_data_into_mongo(historical_data, stock_symbol)


stock_symbol = "DIS" 
populate_database(stock_symbol)
