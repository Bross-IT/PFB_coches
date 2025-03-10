import pandas as pd
import streamlit as st
import pickle
import numpy as np
import datetime
from tensorflow.keras.models import load_model

import encoding_func
from limpieza import transforma_ML

def show():
    st.markdown("""
        # COTIZA TU COCHE
    """)
    
    option = st.radio("Selecciona una opción:", [
        "Explicación de modelos de predicción de precio", 
        "Usa los modelos de predicción de precio"
    ])
    
    if option == "Explicación de modelos de predicción de precio":
        st.markdown("""
            ## EXPLICACIÓN DE MODELOS DE PREDICCIÓN DE PRECIO
            
            ### FEATURE IMPORTANCE
            Tras seleccionar los campos que más influyen sobre el precio, estos son los pesos que hemos obtenido:
        """)
        
        df_feature_importance = pd.read_pickle("bin/feature_importance.pickle")
        st.dataframe(df_feature_importance)
        
        st.markdown("""
            ### ML (MACHINE LEARNING)
            Hemos realizado pruebas con distintos modelos de ML:
            
            - **Linear Regression** (Regresión lineal)
            - **Decision Tree** (Árbol de decisión)
            - **Random Forest** (Bosque aleatorio)
            - **Gradient Boosted Decision Trees** (Gradient boosting con árboles de decisión)
            - **K Neighbors** (K-Vecinos)
            
            Obteniendo los siguientes resultados:
        """)
        
        df_resultados_ml = pd.read_pickle("bin/resultados_modelos_ml.pickle")
        st.dataframe(df_resultados_ml)
        
        st.markdown("""
            Por tanto, hemos seleccionado **Random Forest**, el cual nos da una precisión de predicción del **90%** tras la búsqueda de los mejores hiperparámetros.
            
            ### DL (DEEP LEARNING)
            Tras probar con distintas variantes de una red neuronal completamente conectada de regresión, con distintos hiperparámetros, distintas variantes de arquitectura y con funciones de pérdida MSE y MAE, hemos determinado que la óptima (es decir, la que da mejor resultado y requiriendo menos tiempo de computación) es la siguiente (numero_entradas = 5):
        """)
        
        st.code("""
            model = Sequential()
            
            model.add(Dense(units = 64, activation='relu', input_dim=numero_entradas))
            
            model.add(Dense(units = 32, activation='relu'))
            
            model.add(Dense(units = 1, activation='linear'))
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        """, language="python")
        
        st.markdown("""
            El cual nos da una precisión de predicción del **85%**.
        """)
    
    elif option == "Usa los modelos de predicción de precio":

        marcas_validas = ['VOLVO', 'MERCEDES-BENZ', 'CITROEN', 'JEEP', 'JAGUAR', 'RENAULT',
            'PEUGEOT', 'LEXUS', 'BMW', 'VOLKSWAGEN', 'TOYOTA', 'FORD',
            'ABARTH', 'FIAT', 'ALFA', 'OPEL', 'MINI', 'INEOS', 'SKODA',
            'MASERATI', 'MORGAN', 'SEAT', 'HYUNDAI', 'KIA', 'SUZUKI', 'DACIA',
            'NISSAN', 'AUDI', 'DS', 'MG', 'TESLA', 'MAZDA', 'LAND-ROVER',
            'CHRYSLER', 'LYNK', 'KGM', 'CUPRA', 'SMART', 'HONDA', 'PORSCHE',
            'CHEVROLET', 'OMODA', 'JAECOO', 'LAMBORGHINI', 'MITSUBISHI',
            'SUBARU', 'INFINITI', 'FERRARI', 'AIWAYS', 'GMC', 'XEV',
            'CADILLAC', 'RAM', 'BENTLEY', 'LEAPMOTOR', 'LIVAN', 'DFSK',
            'ASTON', 'SAAB', 'WIESMANN', 'DODGE', 'SANTANA', 'LANCIA', 'EVO',
            'McLAREN', 'LOTUS', 'LINCOLN', 'YES!', 'DR']

        # Título de la aplicación
        st.title("Predicción del Precio de un Coche")

        # Entrada de datos
        kilometraje = st.number_input("Kilometraje", min_value=0, max_value=375000, value=50000, step=1000)
        cambio_automatico = st.radio("¿Cambio automático?", ["No", "Sí"])
        potencia = st.number_input("Potencia (CV)", min_value=10, max_value=2500, value=150, step=10)
        marca = st.selectbox("Marca", marcas_validas)
        anio_matricula = st.number_input("Año de matriculación", min_value=1900, max_value=datetime.datetime.now().year, value=2015, step=1)
        modelo_prediccion = st.radio("Modelo de predicción", ["Deep forest", "Red neuronal"])

        # Crear DataFrame con los datos
        anio_actual = datetime.datetime.now().year

        df = pd.DataFrame({
            "kilometraje": [kilometraje],
            "cambio_automatico": [1 if cambio_automatico == "Sí" else 0],
            "potencia": [potencia],
            "marca_sola": [marca],
            "anio_matricula": [anio_actual - anio_matricula]
        })

        # Normalización de datos
        df = transforma_ML.normalizar(df, ["kilometraje", "potencia"])

        # Cargar transformadores
        with open("bin/marca_sola_precio_encoder.pickle", "rb") as file:
            marca_sola_precio_encoder = pickle.load(file)
        with open("bin/min_max_scaler.pickle", "rb") as file:
            min_max_scaler = pickle.load(file)

        # Transformar la marca y normalizar el DataFrame
        df["marca_sola"] = marca_sola_precio_encoder.transform(df[["marca_sola"]])
        df = min_max_scaler.transform(df)

        # Cargar modelo y predecir
        if modelo_prediccion == "Deep forest":
            with open("bin/mejor_modelo.pickle", "rb") as file:
                modelo = pickle.load(file)
            prediccion = modelo.predict(df)[0]
        else:
            modelo = load_model("bin/modelo_dl.keras")
            prediccion = modelo.predict(df)[0][0]

        # Convertir de logaritmo a precio real
        precio_estimado = np.exp(prediccion)

        # Mostrar resultado
        st.success(f"El precio estimado de tu coche en el mercado actual es de {precio_estimado:,.0f} €.")