import pandas as pd
import streamlit as st
import pickle
import numpy as np
import datetime
from tensorflow.keras.models import load_model
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
            Tras probar con distintas variantes de una red neuronal completamente conectada de regresión, con distintos hiperparámetros, distintas variantes de arquitectura y con funciones de pérdida MSE y MAE, hemos determinado que la óptima es la siguiente (numero_entradas = 5, las features seleccionadas):
        """)
        st.code("""
            model = Sequential()
            model.add(Dense(units = 64, activation='relu', input_dim=numero_entradas))
            model.add(Dense(units = 32, activation='relu'))
            model.add(Dense(units = 1, activation='linear'))
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        """, language="python")

        # Mostrar las métricas almacenadas en el df
        with open("bin/metrics_dl.pickle", "rb") as file:
            df_metrics = pickle.load(file)
        st.dataframe(df_metrics)

        # Indicar la precisión de predicción
        r2 = df_metrics['R2'][0]
        porcentaje = round(r2 * 100)
        st.markdown(f"Tiene una precisión de predicción del **{porcentaje}%**, tal y como se puede ver en el campo R².")

        # Imprimir el título para las gráficas
        st.markdown("### Gráficas del resultado del último entrenamiento de la red neuronal")

        # Mostrar la imagen de las gráficas
        st.image("img/graficas_dl.png", use_container_width=False)

        # Agregar la explicación en texto
        st.markdown("""
        #### Conceptos básicos: ####
        - **Epoch**: Una época representa una pasada completa de todo el conjunto de datos de entrenamiento a través de la red neuronal.
        - **Loss (Pérdida)**: La función de pérdida mide qué tan bien (o mal) está realizando predicciones el modelo. Un valor bajo de pérdida indica que está haciendo buenas predicciones.
        - **MAE (Error Absoluto Medio)**: El MAE mide la magnitud promedio de los errores en las predicciones del modelo. Si es bajo, significa que las predicciones están cerca de los valores reales.
        - **val_loss y val_mae**: Estos representan la pérdida y el MAE calculados en el conjunto de datos de validación (unos separados y no vistos durante el entrenamiento).

        #### Interpretación de las gráficas: ####
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

    elif option == "Usa los modelos de predicción de precio":
        st.title("Predicción del precio de tu coche")
        
        if "step" not in st.session_state:
            st.session_state["step"] = 0
        if "datos_usuario" not in st.session_state:
            st.session_state["datos_usuario"] = {}
        
        step = st.session_state["step"]
        datos_usuario = st.session_state["datos_usuario"]
        
        if datos_usuario and step > 0:
            st.markdown("### Datos seleccionados hasta ahora:")
            for key, value in datos_usuario.items():
                if key == "anio_matricula":
                    st.write(f"**Año de matriculación:** {value}")
                elif key == "cambio_automatico":
                    st.write(f"**Cambio automático:** {value}")
                else:
                    st.write(f"**{key.replace('_', ' ').capitalize()}:** {value}")
        
        error = False
        
        if step == 0:
            kilometraje = st.number_input("Kilometraje", min_value=0, max_value=375000, value=50000, step=1000)
            if kilometraje < 0 or kilometraje > 375000:
                st.error("Por favor, introduce un valor de kilometraje entre 0 y 375000.")
                error = True
            else:
                datos_usuario["kilometraje"] = kilometraje
        elif step == 1:
            cambio_automatico = st.radio("¿Cambio automático?", ["No", "Sí"])
            datos_usuario["cambio_automatico"] = cambio_automatico
        elif step == 2:
            potencia = st.number_input("Potencia (CV)", min_value=10, max_value=2500, value=150, step=10)
            if potencia < 10 or potencia > 2500:
                st.error("Por favor, introduce un valor de potencia entre 10 y 2500.")
                error = True
            else:
                datos_usuario["potencia"] = potencia
        elif step == 3:
            marcas_validas = ['ABARTH', 'AIWAYS', 'ALFA', 'AUDI', 'ASTON', 'BENTLEY', 'BMW', 'CADILLAC', 'CHEVROLET', 'CHRYSLER', 'CITROEN', 'CUPRA', 'DACIA',
                              'DFSK', 'DODGE', 'DR', 'DS', 'EVO', 'FERRARI', 'FIAT', 'FORD', 'GMC', 'HONDA', 'HYUNDAI', 'INEOS', 'INFINITI', 'JAGUAR', 'JAECOO',
                              'JEEP', 'KGM', 'KIA', 'LAMBORGHINI', 'LANCIA', 'LAND-ROVER', 'LEAPMOTOR', 'LEXUS', 'LINCOLN', 'LIVAN', 'LOTUS', 'LYNK', 'MASERATI',
                              'MAZDA', 'McLAREN', 'MERCEDES-BENZ', 'MG', 'MINI', 'MITSUBISHI', 'MORGAN', 'NISSAN', 'OMODA', 'OPEL', 'PEUGEOT', 'PORSCHE', 'RAM',
                              'RENAULT', 'SAAB', 'SANTANA', 'SEAT', 'SKODA', 'SMART', 'SUBARU', 'SUZUKI', 'TESLA', 'TOYOTA', 'VOLKSWAGEN', 'VOLVO', 'WIESMANN',
                              'XEV', 'YES!']
            marca = st.selectbox("Marca", marcas_validas)
        elif step == 4:
            anio_matricula = st.number_input("Año de matriculación", min_value=1900, max_value=datetime.datetime.now().year, value=2015, step=1)
            if anio_matricula < 1900 or anio_matricula > datetime.datetime.now().year:
                st.error("Por favor, introduce un año de matriculación válido.")
                error = True
            else:
                datos_usuario["anio_matricula"] = anio_matricula
        
        if step < 5:
            if st.button("Atrás") and step > 0:
                st.session_state["step"] -= 1
                st.session_state["datos_usuario"].pop(list(datos_usuario.keys())[-1], None)
                st.rerun()
            
            if st.button("Siguiente") and not error:
                if step == 3:
                    datos_usuario["marca"] = marca
                st.session_state["step"] += 1
                st.rerun()
        
        if step == 5:
            modelo_prediccion = st.radio("Modelo de predicción", ["Random forest", "Red neuronal"])
            anio_actual = datetime.datetime.now().year
            df = pd.DataFrame({
                "kilometraje": [datos_usuario["kilometraje"]],
                "cambio_automatico": [1 if datos_usuario["cambio_automatico"] == "Sí" else 0],
                "potencia": [datos_usuario["potencia"]],
                "marca_sola": [datos_usuario["marca"]],
                "anio_matricula": [anio_actual - datos_usuario["anio_matricula"]]
            })
            df = transforma_ML.normalizar(df, ["kilometraje", "potencia"])
            with open("bin/marca_sola_precio_encoder.pickle", "rb") as file:
                marca_sola_precio_encoder = pickle.load(file)
            with open("bin/min_max_scaler.pickle", "rb") as file:
                min_max_scaler = pickle.load(file)
            df["marca_sola"] = marca_sola_precio_encoder.transform(df[["marca_sola"]])
            df = min_max_scaler.transform(df)
            if modelo_prediccion == "Random forest":
                with open("bin/mejor_modelo.pickle", "rb") as file:
                    modelo = pickle.load(file)
                prediccion = modelo.predict(df)[0]
            else:
                modelo = load_model("bin/modelo_dl.keras")
                prediccion = modelo.predict(df)[0][0]
            precio_estimado = np.exp(prediccion)
            st.success(f"El precio estimado de tu coche en el mercado actual es de {precio_estimado:,.0f} €.".replace(",", "."))
            if st.button("Reiniciar"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    show()