import pandas as pd
import streamlit as st
import pickle
import numpy as np
import re
import datetime
import plotly.express as px
from tensorflow.keras.models import load_model, model_from_json
from limpieza import transforma_ML
from machinelearning.graficar_dl import graficar_historial

def show():
    st.markdown("""
        # COTIZA TU COCHE
    """)
    st.markdown("""
        Esta es la sección de los dos modelos de predicción ML y DL para averiguar el precio de un coche, según los datos obtenidos de autocasion.es.
    """)
    
    option = st.radio("Selecciona una opción:", [
        "Explicación de modelos de predicción", 
        "Usar los modelos de predicción"
    ])
    
    if option == "Explicación de modelos de predicción":
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

        fig = px.bar(df_resultados_ml, x='Modelo', y=['MSE', 'MAE', 'RMSE', 'R2'], barmode='group',
                title='Resultados de los Modelos de Machine Learning',
                labels={'value': 'Métrica', 'variable': 'Tipo de Métrica'})
        st.plotly_chart(fig)
        
        with open("bin/best_score_ml.pickle", "rb") as file:
            best_score_rf = pickle.load(file)
        
        porcentaje_rf = round(best_score_rf * 100)
        
        st.markdown(f"""
            Por tanto, hemos seleccionado **Random Forest**, el cual nos da una precisión de predicción del **{porcentaje_rf}%** tras la búsqueda de los mejores hiperparámetros.
            ### DL (DEEP LEARNING)
            Tras probar con distintas variantes de una red neuronal completamente conectada de regresión, con distintos hiperparámetros, distintas variantes de arquitectura y con funciones de pérdida MSE y MAE, hemos determinado que la óptima es la siguiente:
        """)

        # Cargar la arquitectura del modelo desde el archivo JSON
        with open("bin/modelo_dl_architecture.json", "r") as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json)

        # Mostrar el summary del modelo
        summary_str = []
        model.summary(print_fn=lambda x: summary_str.append(x))
        summary_str = "\n".join(summary_str)  # Convertir la lista a un solo string
        summary_str_html = summary_str.replace("\n", "<br>")  # Reemplazar saltos de línea por <br>

        st.markdown(f"""
        <style>
        .custom-font {{
            font-family: 'Courier New', monospace;
            font-size: 20px;
        }}
        </style>

        <p class="custom-font">{summary_str_html}</p>
        """, unsafe_allow_html=True)

        st.markdown("""
            El número de entradas es 5 (el de las features seleccionadas) y el número de épocas es 100 con EarlyStoppoing. Por tanto, en el eje X de las gráficas posteriores saldrá un número menor o igual a 100.
        """)

        st.markdown("""
            ### MÉTRICAS
            Las métricas obtenidas tras el último entrenamiento de la red neuronal son las siguientes:
        """)

        # Mostrar las métricas almacenadas en el df
        with open("bin/metrics_dl.pickle", "rb") as file:
            df_metrics = pickle.load(file)
        st.dataframe(df_metrics)

        # Indicar la precisión de predicción
        r2 = df_metrics['R2'][0]
        porcentaje = round(r2 * 100)
        st.markdown(f"Actualmente tiene una precisión de predicción del **{porcentaje}%**, tal y como se puede ver en el campo R².")

        # Imprimir el título para las gráficas
        st.markdown("### Gráficas del resultado del último entrenamiento de la red neuronal")

        # Cargar el historial de entrenamiento
        with open("bin/history_dl_2.pickle", "rb") as file:
            history = pickle.load(file)

        # Graficar el historial de entrenamiento
        fig = graficar_historial(history)
        st.plotly_chart(fig)

        # Agregar la explicación en texto
        st.markdown("""
        #### Conceptos básicos:
        - **Epoch**: Una época representa una pasada completa de todo el conjunto de datos de entrenamiento a través de la red neuronal.
        - **Loss (Pérdida)**: La función de pérdida mide qué tan bien (o mal) está realizando predicciones el modelo. Un valor bajo de pérdida indica que está haciendo buenas predicciones.
        - **MAE (Error Absoluto Medio)**: El MAE mide la magnitud promedio de los errores en las predicciones del modelo. Si es bajo, significa que las predicciones están cerca de los valores reales.
        - **val_loss y val_mae**: Estos representan la pérdida y el MAE calculados en el conjunto de datos de validación (unos separados y no vistos durante el entrenamiento).

        #### Interpretación de las gráficas:
        1. **Comportamiento ideal**:
            - Tanto "loss" como "val_loss" deberían disminuir con cada época, estabilizándose eventualmente.
            - De manera similar, tanto "mae" como "val_mae" deberían disminuir y estabilizarse.
            - Las curvas de "loss" y "val_loss" (y "mae" y "val_mae") deberían estar relativamente cerca una de la otra.
        2. **Sobreajuste (Overfitting)**:
            - "loss" sigue disminuyendo, pero "val_loss" comienza a aumentar después de cierto punto.
            - "mae" sigue disminuyendo, pero "val_mae" comienza a aumentar.
            - Esto indica que el modelo está aprendiendo demasiado bien los datos de entrenamiento (los memoriza), pero no generaliza bien a nuevos datos.
        3. **Subajuste (Underfitting)**:
            - Tanto "loss" como "val_loss" se estabilizan en un valor relativamente alto.
            - Tanto "mae" como "val_mae" se estabilizan en un valor relativamente alto.
            - Esto indica que el modelo no ha aprendido lo suficiente de los datos de entrenamiento.
        4. **Fluctuaciones**:
            - Las curvas pueden mostrar fluctuaciones, especialmente al principio del entrenamiento.
            - Fluctuaciones excesivas pueden indicar una tasa de aprendizaje demasiado alta.
        """)

    elif option == "Usar los modelos de predicción":
        st.title("Predicción del precio de tu coche")
        
        kilometraje = st.number_input("Kilometraje", min_value=0, max_value=375000, value=50000, step=1000)
        cambio_automatico = st.radio("¿Cambio automático?", ["No", "Sí"])
        potencia = st.number_input("Potencia (CV)", min_value=10, max_value=2500, value=150, step=10)
        marcas_validas = ['ABARTH', 'AIWAYS', 'ALFA', 'AUDI', 'ASTON', 'BENTLEY', 'BMW', 'CADILLAC', 'CHEVROLET', 'CHRYSLER', 'CITROEN', 'CUPRA', 'DACIA',
                          'DFSK', 'DODGE', 'DR', 'DS', 'EVO', 'FERRARI', 'FIAT', 'FORD', 'GMC', 'HONDA', 'HYUNDAI', 'INEOS', 'INFINITI', 'JAGUAR', 'JAECOO',
                          'JEEP', 'KGM', 'KIA', 'LAMBORGHINI', 'LANCIA', 'LAND-ROVER', 'LEAPMOTOR', 'LEXUS', 'LINCOLN', 'LIVAN', 'LOTUS', 'LYNK', 'MASERATI',
                          'MAZDA', 'McLAREN', 'MERCEDES-BENZ', 'MG', 'MINI', 'MITSUBISHI', 'MORGAN', 'NISSAN', 'OMODA', 'OPEL', 'PEUGEOT', 'PORSCHE', 'RAM',
                          'RENAULT', 'SAAB', 'SANTANA', 'SEAT', 'SKODA', 'SMART', 'SUBARU', 'SUZUKI', 'TESLA', 'TOYOTA', 'VOLKSWAGEN', 'VOLVO', 'WIESMANN',
                          'XEV', 'YES!']
        marca = st.selectbox("Marca", marcas_validas)
        anio_matricula = st.number_input("Año de matriculación", min_value=1900, max_value=datetime.datetime.now().year, value=2015, step=1)
        
        if st.button("Estimar precio"):
            anio_actual = datetime.datetime.now().year
            df = pd.DataFrame({
                "kilometraje": [kilometraje],
                "cambio_automatico": [1 if cambio_automatico == "Sí" else 0],
                "potencia": [potencia],
                "marca_sola": [marca],
                "antiguedad": [anio_actual - anio_matricula]
            })
            df = transforma_ML.normalizar(df, ["kilometraje", "potencia"])
            with open("bin/marca_sola_precio_encoder.pickle", "rb") as file:
                marca_sola_precio_encoder = pickle.load(file)
            with open("bin/min_max_scaler.pickle", "rb") as file:
                min_max_scaler = pickle.load(file)
            df["marca_sola"] = marca_sola_precio_encoder.transform(df[["marca_sola"]])
            df = min_max_scaler.transform(df)
            
            # Predicción con Random Forest
            with open("bin/mejor_modelo.pickle", "rb") as file:
                modelo_ml = pickle.load(file)
            prediccion_ml = modelo_ml.predict(df)[0]
            precio_estimado_ml = np.exp(prediccion_ml)
            
            # Predicción con Red Neuronal
            modelo_dl = load_model("bin/modelo_dl.keras")
            prediccion_dl = modelo_dl.predict(df)[0][0]
            precio_estimado_dl = np.exp(prediccion_dl)
            
            st.success(f"Estas son las estimaciones de precio de tu coche según modelo de predicción.\n"
                       f"- ML (random forest): {precio_estimado_ml:,.0f} €.".replace(",", ".") + "\n"
                       f"- DL (red neuronal): {precio_estimado_dl:,.0f} €.".replace(",", "."))
            if st.button("Reiniciar"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    show()