import pandas as pd
import streamlit as st

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
            Por tanto, hemos seleccionado **Random Forest**, el cual nos da una precisión de predicción del **89%**, como se puede ver con la métrica de R².
            
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
            El cual nos da una precisión de predicción del **66%**.
        """)
    
    elif option == "Usa los modelos de predicción de precio":
        st.markdown("""
            ## USA LOS MODELOS DE PREDICCIÓN DE PRECIO
            
            *En construcción*
        """)