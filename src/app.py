import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import pathlib
import json
import os
import streamlit.components.v1 as components

import explorador, comparador
from ml_func import PAGE_CONFIG

def main():
    script_dir = pathlib.Path(__file__).resolve().parent

    st.set_page_config(**PAGE_CONFIG)

    menu = ["Home", "Exploratory Data Analysis","Comparador de coches", "Cotiza tu coche", "Base de datos", "About us"]

    choice = st.sidebar.selectbox(label = "Menu", options = menu, index = 0)

    if choice == "Home":
        st.subheader(body = "Home :house:")

        st.write("**Bienvenidos a la mejor web para encontrar tu coche de segunda mano hecha con Streamlit**.")

        st.markdown("""Para este proyecto, desarrollaremos una aplicación web con Streamlit que permita navegar y visualizar de manera 
                    cómoda y sencilla los datos más relevantes en el mercado de coches de segunda mano, utilizando la web de 
                    [Autocasión](https://www.autocasion.com/coches-segunda-mano) como fuente principal de datos.
                     Crearemos una base de datos para almacenar eficientemente la información extraída y diseñaremos un proceso ETL 
                    para mantenerla actualizada.""")

        st.write("""Para entender bien los datos con los que se construyó nuestra calculadora de precios, dirígete a la sección 
                 `Exploratory Data Analysis` del menú lateral.""")

        st.write("""Si estas buscando tu próximo coche y no te decides por cual, puedes usar nuestro `Comparador de coches` 
                 dirigiendote al menú lateral.""")
        
        st.write("""Para cotizar tu coche, dirígete a la sección `Cotiza tu coche` del menú lateral.""")

        st.write("""Para conocer la estructura de nuestra base de datos, dirígete a la sección `Base de Datos` del menú lateral,
                  en la cual compartiremos los aspectos más relevantes de cada una de sus tablas.""")
        
        st.write("""Conoce más sobre nuestro equipo en la sección, `About us` del menú lateral y descubre todos nuestros proyectos.""")

        df = pd.read_csv(f'{script_dir}/../data/municipios_cloropetico.csv')

        mapa_opcion = st.selectbox(
            label="Selecciona el nivel de geografía para visualizar el mapa",
            options=["Comunidad", "Provincia"],
            #options=["Comunidad", "Provincia", "Municipio"],
            index=0  
        )

        if mapa_opcion == "Comunidad":
            mapa_html_comunidad = f"{script_dir}/../img/mapa_comunidades.html"

            with open(mapa_html_comunidad, "r", encoding="utf-8") as file:
                mapa_comunidad_html = file.read()
            st.components.v1.html(mapa_comunidad_html, height=1024, width=1180)

        elif mapa_opcion == "Provincia":
            mapa_html_provincia = f"{script_dir}/../img/mapa_provincias.html"
            with open(mapa_html_provincia, "r", encoding="utf-8") as file:
                mapa_provincia_html = file.read()
            st.components.v1.html(mapa_provincia_html, height=1024, width=1180)
        # Para mapa cloropetico municipio (Dmytry)
        elif mapa_opcion == "Municipio":
            geojson_url_municipios = f'{script_dir}/../geojson/municipios_espana.geojson'

            with open(geojson_url_municipios, encoding='utf-8') as f:
                geojson_data_municipios = json.load(f)

            municipios_geojson = pd.DataFrame([{
                'municipio': feature['properties']['NAMEUNIT'], 
                'geometry': feature['geometry'] 
            } for feature in geojson_data_municipios['features']])

            df_municipios_coches = municipios_geojson.merge(
                df[['municipio', 'cantidad_coches', 'precio_medio']], 
                on='municipio', how='left'
            )

            df_municipios_coches['cantidad_coches'] = df_municipios_coches['cantidad_coches'].fillna(0).astype(int)
            df_municipios_coches['precio_medio'] = df_municipios_coches['precio_medio'].fillna(0).astype(int)
            st.write(municipios_geojson.head())
            st.write(df[['municipio', 'cantidad_coches', 'precio_medio']].head())
            st.write(geojson_data_municipios['features'][0]['properties'].keys())
            fig = px.choropleth_mapbox(
                df_municipios_coches,
                geojson=geojson_url_municipios,               
                locations='municipio',                  
                featureidkey="properties.NAMEUNIT",    
                color='cantidad_coches',                
                color_continuous_scale="reds",          
                mapbox_style="carto-positron",          
                center={"lat": 40.4, "lon": -3.7},  
                zoom=5,                          
                title="Densidad de Coches en Venta y Precio Medio por Municipio",
                hover_data={'municipio': False, 'cantidad_coches': False, 'precio_medio': False},  
                custom_data=['municipio', 'cantidad_coches', 'precio_medio'],  
            )
            fig.update_layout(
                width=1180,  
                height=1024,  
                autosize=False,
                coloraxis_colorbar_title="Cantidad de Coches")  
            fig.update_traces(
                hovertemplate="<b>Municipio</b>: %{customdata[0]}<br><b>Cantidad de Autos</b>: %{customdata[1]}<br><b>Precio medio de Coches en el Municipio</b>: €%{customdata[2]}"
            )
            st.plotly_chart(fig)

    elif choice == "Exploratory Data Analysis":
        explorador.explorador_app()
    elif choice == "Comparador de coches":
        #comparador_app()
        comparador.show()
    elif choice == "Cotiza tu coche":
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

    elif choice == "Base de datos":
        st.markdown("""
        # BASE DE DATOS
        
        Hemos creado el modelo entidad-relación basándonos en aspectos de eficiencia computacional:
        
        - La tabla principal, en vez de contener campos con cadenas, tiene índices a otras tablas con ellos. Así se puede indexar más rápidamente.
        - Los tamaños de cada campo están estudiados para que sean lo más pequeños posible de forma coherente, para ahorrar espacio y hacer la indexación más rápida.
        
        De esta manera, la base de datos será sostenible aun con un volumen de datos mucho mayor del que disponíamos a día que desarrollamos este proyecto (pues todos los días se agregan nuevos coches).
        """)
    
        st.image("img/er_diagram.png", caption="Diagrama Entidad-Relación", use_container_width=False)
    
        st.markdown("""
        ### coches_en_venta: 
        Tabla principal, siendo `referencia` la original de autocasion.es sin `ref` delante (valor numérico solo). Contiene ids a los valores que se guardan en cadenas a sus respectivas tablas (*combustible, carroceria, distintivo_ambiental, color, modelo_titulo, concesionario, urls y ruta_imagen*), valores booleanos (*peninsula_y_baleares, cambio_automatico, vendedor_profesional y certificado*) y numéricos propios del coche:
        
        - **kilometraje** (enteros)
        - **potencia** (cv)
        - **garantia** (meses)
        - **plazas** (enteros)
        - **puertas** (enteros)
        - **consumo** (l/km, con dos decimales)
        - **antiguedad** (enteros que son año actual - anio_matricula)
        - **precio** (enteros)
        - **mes_matricula** (entero)
        - **anio_matricula** (entero)
        
        ### Otras tablas y relaciones:
        
        - **urls y ruta_imagen**: Lista de links a la página web de cada coche en autocasion.es y su respectiva ruta a la imagen principal del mismo (relación 1-1 con `coches_en_venta`).
        - **combustible, carroceria, distintivo_ambiental y color**: Contienen los distintos valores de cada uno, con ids referenciados en `coches_en_venta` (1-n).
        - **modelo_titulo**: Contiene el nombre tal y como viene en autocasion.es, pero sin la marca, que está listada en la tabla `marca` (relación 1-1 con `coches_en_venta`).
        - **marca**: Contiene todas las marcas de coches, con ids referenciados en `modelo_titulo` (1-n).
        - **concesionario**: Contiene los datos de los concesionarios que venden coches en autocasion.es, con una relación 1-n con `coches_en_venta`. Incluye referencias a ids de `municipio` y `provincia`.
        - **vendedor_particular**: Lista de vendedores particulares con un id autoincremental, relacionados 1-1 con `modelo_titulo`.
        - **municipio**: Lista de municipios indicados en los concesionarios de autocasion.es (1-n).
        - **provincia**: Contiene las provincias indicadas en los concesionarios y de los vendedores particulares (1-n con ambas).
        - **comunidad_autonoma**: Contiene las comunidades autónomas, cuyos ids están referenciados en `provincia` (1-n).
        """)    
    else:
        #about_app()
        st.write("**Sitio en construcción**.")




if __name__ == "__main__":
    main()