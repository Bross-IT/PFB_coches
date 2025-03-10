import pandas as pd
import numpy as np
import pickle

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
# from tensorflow.keras.regularizers import l2
# from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

import os
import sys

notebook_path = os.path.abspath(".")
sys.path.append(os.path.abspath(os.path.join(notebook_path, '..', 'src')))

import encoding_func

df_modelo = pd.read_pickle('../bin/dataframe_ml.pickle')

with open(f"../bin/marca_sola_precio_encoder.pickle", "rb") as file:
    marca_sola_precio_encoder = pickle.load(file)

with open(f"../bin/min_max_scaler.pickle", "rb") as file:
    min_max_scaler = pickle.load(file)

TARGET = "precio"

X_train, X_test, y_train, y_test = encoding_func.dividir_dataframe(df_modelo, TARGET, test_size=0.2, random_state=42)

X_train["marca_sola"] = marca_sola_precio_encoder.transform(X_train["marca_sola"])
X_test["marca_sola"] = marca_sola_precio_encoder.transform(X_test["marca_sola"])

X_train = min_max_scaler.transform(X_train)
X_test = min_max_scaler.transform(X_test)

def crear_modelo(numero_entradas):
    """Crea un modelo de red neuronal secuencial para regresión."""

    model = Sequential()
    
    # Capa de entrada
    model.add(Dense(units = 64, activation='relu', input_dim=numero_entradas))

    model.add(Dense(units = 32, activation='relu'))
    # model.add(Dropout(0.2))

    model.add(Dense(units = 1, activation='linear'))

    # learning_rate = 0.001  # Ajusta este valor
    # optimizer = Adam(learning_rate=learning_rate)

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    model.summary()

    return model

def entrenar_modelo(model, X_train, y_train, epochs=100, batch_size=32):
    """Entrena el modelo de red neuronal y guarda el historial de entrenamiento."""
    history = model.fit(X_train,
                        y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_split=0.2)
    
    model.save('../bin/modelo_dl') 

    return model, history

def obtener_predicciones(model, X_test):
    """Obtiene las predicciones del modelo."""
    return model.predict(X_test).flatten()

def evaluar_modelo(y_test, y_pred):
    """Evalúa el rendimiento del modelo de regresión."""
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return mse, mae, r2

def graficar_historial(history):
    """Grafica el historial de entrenamiento (loss y MAE)."""
    plt.figure(figsize=(12, 5))

    # Gráfica de Loss
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Loss vs. Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    # Gráfica de MAE
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Training MAE')
    plt.plot(history.history['val_mae'], label='Validation MAE')
    plt.title('MAE vs. Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('MAE')
    plt.legend()

    plt.show()

def main(X_train, X_test, y_train, y_test):
    """Función principal que ejecuta todo el proceso de modelado."""
    model = crear_modelo(X_train.shape[1])
    model, history = entrenar_modelo(model, X_train, y_train)

    y_pred = obtener_predicciones(model, X_test)
    mse, mae, r2 = evaluar_modelo(y_test, y_pred)

    print(f"MSE: {mse:.4f}, MAE: {mae:.4f}, R^2: {r2:.4f}")

    graficar_historial(history)

main(X_train, X_test, y_train, y_test)