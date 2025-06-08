import numpy as np
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras import losses

model2a = load_model(
    'model2a_gru.h5',
    custom_objects={'mse': losses.MeanSquaredError()}
)
model2b = load_model(
    'model2b_lstm_gru.h5',
    custom_objects={'mse': losses.MeanSquaredError()}
)
scaler_X = joblib.load('scaler_X.gz')
scaler_y = joblib.load('scaler_y.gz')

# === 2. Vhod: zadnje 3 realne cene delnice ===
last_3_prices = np.array([261.12, 261.50, 266.82])

# === 3. Priprava in skaliranje ===
X_input = last_3_prices.reshape(-1, 1)
X_input_scaled = scaler_X.transform(X_input).reshape(1, 3, 1)

# === 4. Napovedi ===
y_pred2a = scaler_y.inverse_transform(model2a.predict(X_input_scaled))[0][0]
y_pred2b = scaler_y.inverse_transform(model2b.predict(X_input_scaled))[0][0]

# === 5. Izpis rezultatov ===
print(f"Napoved (GRU model): {y_pred2a:.2f}")
print(f"Napoved (LSTM -> GRU model): {y_pred2b:.2f}")