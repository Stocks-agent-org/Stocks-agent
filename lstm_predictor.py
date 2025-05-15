import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def predict_lstm(symbol, mongo_url):
    client = MongoClient(mongo_url)
    db = client["delnice_db"]
    collection = db["podatki_o_delnicah"]

    data = list(collection.find({"symbol": symbol}).sort("cas", 1))

    if len(data) < 5:
        return None  # premalo podatkov

    df = pd.DataFrame(data)
    prices = df["close"].values.reshape(-1, 1)

    scaler = MinMaxScaler() 
    scaled_prices = scaler.fit_transform(prices)

    x = np.arange(len(scaled_prices)).reshape(-1, 1)
    y = scaled_prices

    model = LinearRegression()
    model.fit(x, y)

    future_index = np.array([[len(scaled_prices)]])
    future_scaled = model.predict(future_index)
    future_price = scaler.inverse_transform(future_scaled)

    return float(future_price[0][0])
