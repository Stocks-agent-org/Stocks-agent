import os
import random
import numpy as np
import pandas as pd

from pymongo import MongoClient

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam


# ──────────────── 1. Fiksiraj naključna semena ─────────────────
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)
os.environ['TF_DETERMINISTIC_OPS'] = '1'
os.environ['TF_CUDNN_DETERMINISM'] = '1'
# ─────────────────────────────────────────────────────────────────


def fetch_close_series(symbol: str, mongo_url: str) -> pd.DataFrame:
    client = MongoClient(mongo_url)
    db = client["delnice_db"]
    collection = db[symbol]
    cursor = collection.find({"symbol": symbol}).sort("date", 1)  # sortiraj po 'date'
    data = list(cursor)
    client.close()

    if len(data) == 0:
        return pd.DataFrame(columns=['date', 'close'])

    df = pd.DataFrame(data)

    # Prepričaj se, da imamo stolpec 'date'
    if 'date' not in df.columns:
        raise KeyError(f"Ne najdem stolpca 'date' za simbol {symbol}")

    # Pretvori 'date' v datetime in nastavi kot index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Uporabi samo 'close' stolpec kot float
    df = df[['close']].astype(float)

    return df

def make_windowed_series(prices: np.ndarray, n_timesteps: int) -> (np.ndarray, np.ndarray):
    """
    Iz enodimenzionalnega niza cen (np.ndarray) naredi 'slide window' dolžine n_timesteps.
    Vrne:
      X  → oblika (samples, n_timesteps, 1)
      y  → oblika (samples,)
    """
    X_list, y_list = [], []
    for i in range(n_timesteps, len(prices)):
        window = prices[i - n_timesteps : i + 1]   # dolžina = n_timesteps + 1
        X_list.append(window[:-1].reshape(n_timesteps, 1))
        y_list.append(window[-1])
    X = np.stack(X_list, axis=0)  # (samples, n_timesteps, 1)
    y = np.array(y_list)          # (samples,)
    return X, y


def predict_lstm_hybrid(symbol: str, mongo_url: str) -> dict:
    """
    - Pridobi serijo 'close' iz MongoDB.
    - Ustvari windows dolžine n_timesteps = 5.
    - Razdeli na X_train/X_val/X_test in y_train/… brez shuffle.
    - Normalizira z MinMaxScalerjem.
    - Definira in nauči dva modela:
        1) Čisti GRU (64 → Dense(32, relu) → Dense(1))
        2) Hibrid LSTM(64, return_sequences=True) → GRU(64) → Dense(32, relu) → Dense(1)
      oba z compile(loss='mse', Adam(lr=0.001), metrics=['mae']).
    - Fit 100 epoh, batch_size=32 (privzeto), verbose=2.
    - Napove zadnji dan + 1 v izvorni skali s čisto GRU.
    - Z LSTM→GRU modelom oceni, ali bo cena rasla (True) ali padala (False).
    - Vrne dict z:
        {
          'next_price_gru': float,
          'direction_lstm_gru': bool
        }
    """
    # 1) Pridobi podatke
    df = fetch_close_series(symbol, mongo_url)
    if df.shape[0] < 6:
        return None  # premalo podatkov: n_timesteps=5 zahteva vsaj 6 točk

    # 2) Enodimenzionalen array cen
    prices = df['close'].values  # oblika (N,)

    # 3) Windowed serija (n_timesteps = 5)
    n_timesteps = 5
    X_all, y_all = make_windowed_series(prices, n_timesteps)
    # X_all.shape = (N-5, 5, 1),  y_all.shape = (N-5,)

    # 4) Razdelitev na train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X_all, y_all, test_size=0.2, shuffle=False
    )
    val_rel = 0.1 / (1 - 0.2)  # val_size=0.1
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_rel, shuffle=False
    )

    # 5) Normalizacija (MinMaxScaler)
    X_train_flat = X_train.reshape(-1, 1)
    X_val_flat   = X_val.reshape(-1, 1)
    X_test_flat  = X_test.reshape(-1, 1)

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    scaler_X.fit(X_train_flat)
    scaler_y.fit(y_train.reshape(-1, 1))

    X_train_scaled = scaler_X.transform(X_train_flat).reshape(X_train.shape)
    X_val_scaled   = scaler_X.transform(X_val_flat).reshape(X_val.shape)
    X_test_scaled  = scaler_X.transform(X_test_flat).reshape(X_test.shape)

    y_train_scaled = scaler_y.transform(y_train.reshape(-1, 1)).flatten()
    y_val_scaled   = scaler_y.transform(y_val.reshape(-1, 1)).flatten()
    # y_test_scaled, če bi merili metrike, pa ni nujno

    # 6a) Definicija čistega GRU
    model_gru = Sequential([
        layers.Input(shape=(X_train.shape[1], X_train.shape[2])),  # (5,1)
        layers.GRU(64),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ])
    model_gru.compile(
        loss='mse',
        optimizer=Adam(learning_rate=0.001),
        metrics=['mean_absolute_error']
    )

    # 6b) Definicija hibridnega LSTM→GRU
    model_lstm_gru = Sequential([
        layers.Input(shape=(X_train.shape[1], X_train.shape[2])),
        layers.LSTM(64, return_sequences=True),
        layers.GRU(64),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ])
    model_lstm_gru.compile(
        loss='mse',
        optimizer=Adam(learning_rate=0.001),
        metrics=['mean_absolute_error']
    )

    # 7a) Treniranje čistega GRU
    model_gru.fit(
        X_train_scaled, y_train_scaled,
        validation_data=(X_val_scaled, y_val_scaled),
        epochs=100,
        verbose=2  # batch_size=32 privzeto, shuffle=True privzeto
    )

    # 7b) Treniranje hibridnega LSTM→GRU
    model_lstm_gru.fit(
        X_train_scaled, y_train_scaled,
        validation_data=(X_val_scaled, y_val_scaled),
        epochs=100,
        verbose=2
    )

    # 8a) Napoved naslednjega dne s čistim GRU
    last_window = prices[-n_timesteps:]                   # zadnjih 5 cen
    last_window = last_window.reshape(n_timesteps, 1)      # (5,1)
    last_flat   = last_window.reshape(-1, 1)               # (5,1)
    last_scaled = scaler_X.transform(last_flat).reshape(1, n_timesteps, 1)

    next_scaled_gru  = model_gru.predict(last_scaled, verbose=0).flatten()[0]
    next_price_gru   = scaler_y.inverse_transform([[next_scaled_gru]])[0][0]

    # 8b) Napoved naslednjega dne s hibridom LSTM→GRU
    next_scaled_lstm_gru = model_lstm_gru.predict(last_scaled, verbose=0).flatten()[0]
    next_price_lstm_gru  = scaler_y.inverse_transform([[next_scaled_lstm_gru]])[0][0]

    # 9) Oceni smer napovedi hibridnega modela (True = narašča, False = pada)
    last_actual_price = prices[-1]
    direction_lstm_gru = next_price_lstm_gru > last_actual_price

    return {
        'next_price_gru': float(next_price_gru),
        'direction_lstm_gru': bool(direction_lstm_gru)
    }