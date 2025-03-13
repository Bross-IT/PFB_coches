import pandas as pd
import numpy as np
import pickle

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
# from tensorflow.keras.regularizers import l2
# from tensorflow.keras.optimizers import Adam
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import os
import sys

notebook_path = os.path.abspath(".")
sys.path.append(os.path.abspath(os.path.join(notebook_path, '..', 'src')))

import encoding_func

df_modelo = pd.read_pickle('bin/dataframe_ml.pickle')

with open(f"bin/marca_sola_precio_encoder.pickle", "rb") as file:
    marca_sola_precio_encoder = pickle.load(file)

with open(f"bin/min_max_scaler.pickle", "rb") as file:
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
    model.add(Dense(units=64, activation='relu', input_dim=numero_entradas))
    model.add(Dense(units=32, activation='relu'))
    # model.add(Dropout(0.2))
    model.add(Dense(units=1, activation='linear'))

    # learning_rate = 0.01  # Ajusta este valor
    # optimizer = Adam(learning_rate=learning_rate)

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.summary()

    return model

def entrenar_modelo(model, X_train, y_train, epochs=100, batch_size=32):
    """Entrena el modelo de red neuronal y guarda el historial de entrenamiento."""
    early_stopping = EarlyStopping(monitor="val_loss",
                                   patience=15,
                                   restore_best_weights=True)
    history = model.fit(X_train,
                        y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_split=0.2,
                        callbacks=[early_stopping])
     
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
    """Grafica el historial de entrenamiento (loss y MAE) y guarda la imagen."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Loss vs. Epochs", "MAE vs. Epochs"))

    # Gráfica de Loss
    fig.add_trace(go.Scatter(
        x=list(range(len(history['loss']))),
        y=history['loss'],
        mode='lines',
        name='Training Loss'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=list(range(len(history['val_loss']))),
        y=history['val_loss'],
        mode='lines',
        name='Validation Loss'
    ), row=1, col=1)

    # Gráfica de MAE
    fig.add_trace(go.Scatter(
        x=list(range(len(history['mae']))),
        y=history['mae'],
        mode='lines',
        name='Training MAE'
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=list(range(len(history['val_mae']))),
        y=history['val_mae'],
        mode='lines',
        name='Validation MAE'
    ), row=1, col=2)

    fig.update_layout(
        title_text='Training History',
        xaxis_title='Epochs',
        yaxis_title='Loss',
        yaxis2=dict(
            title='MAE',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=10),
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        )
    )

    # fig.write_image('../img/graficas_dl.png')
    # fig.show()

    return fig

def generar_y_entrenar_modelo_dl(X_train, X_test, y_train, y_test):
    """Función principal que ejecuta todo el proceso de modelado."""
    model = crear_modelo(X_train.shape[1])
    model, history = entrenar_modelo(model, X_train, y_train)

    model.save('bin/modelo_dl.keras')
    with open('bin/modelo_dl_architecture.json', 'w') as json_file:
        json_file.write(model.to_json())

    with open('bin/history_dl.pickle', 'wb') as file:
        pickle.dump(history, file)

    y_pred = obtener_predicciones(model, X_test)
    mse, mae, r2 = evaluar_modelo(y_test, y_pred)

    print(f"MSE: {mse:.4f}, MAE: {mae:.4f}, R^2: {r2:.4f}")

    df_metrics = pd.DataFrame({
        'MSE': [mse],
        'MAE': [mae],
        'R2': [r2]
    })
    with open('bin/metrics_dl.pickle', 'wb') as file:
        pickle.dump(df_metrics, file)

    return

    # graficar_historial(history)

# generar_y_entrenar_modelo_dl(X_train, X_test, y_train, y_test)