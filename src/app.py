import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import pathlib
import json
import os
import streamlit.components.v1 as components

import explorador
import comparador
import bd_page as bd
import cotiza_tu_coche as ml
import about_us
import ocasionDataBase as odb

from ml_func import PAGE_CONFIG

def main():
    script_dir = pathlib.Path(__file__).resolve().parent
    config = odb.load_config(f"{script_dir}/../.streamlit/secrets.toml", "database_user")
    database = odb.OcasionDataBase(config)
    dataframe = pd.DataFrame(database.obtener_coches_venta())
    st.set_page_config(**PAGE_CONFIG)

    menu = ["Home", "Exploratory Data Analysis","Comparador de coches", "Cotiza tu coche", "Base de datos", "Sobre nosotros"]

    choice = st.sidebar.selectbox(label = "Menu", options = menu, index = 0)

    if choice == "Home":
        st.title(body = "Home :house:")

        st.subheader("**Bienvenidos a la mejor web para encontrar tu coche de segunda mano hecha con Streamlit**.")

        st.markdown("""Para este proyecto, desarrollamos una aplicación web con Streamlit que permite navegar y visualizar de manera 
                    cómoda y sencilla los datos más relevantes en el mercado de coches de segunda mano, utilizando la web de 
                    [Autocasión](https://www.autocasion.com/coches-segunda-mano) como fuente principal de datos.
                     Creamos una base de datos para almacenar eficientemente la información extraída y diseñamos un proceso ETL 
                    para mantenerla actualizada. 
                     Además, implementamos modelos de Machine Learning y Deep Learning para predecir el precio de coches según las 
                    características ingresadas por el usuario, permitiéndole obtener una estimación precisa basada en datos históricos
                    del mercado. 🚗📊✨""")
        
        st.subheader("**Secciones:**")

        st.markdown("""
                    - **Para entender bien los datos** con los que se construyó nuestra calculadora de precios, dirígete a la sección `Exploratory Data Analysis` del menú lateral.  
                    - **Si estás buscando tu próximo coche** y no te decides por cuál, puedes usar nuestro `Comparador de coches` dirigiéndote al menú lateral.  
                    - **Para cotizar tu coche**, dirígete a la sección `Cotiza tu coche` del menú lateral.  
                    - **Para conocer la estructura de nuestra base de datos**, dirígete a la sección `Base de Datos` del menú lateral, en la cual compartiremos los aspectos más relevantes de cada una de sus tablas.  
                    - **Conoce más sobre nuestro equipo** en la sección `About us` del menú lateral y descubre todos nuestros proyectos.  
                                
                    """)

        df = pd.read_csv(f'{script_dir}/../data/municipios_coropletico.csv')

        mapa_opcion = st.selectbox(
            label="Selecciona el nivel de geografía para visualizar el mapa",
            #options=["Comunidad", "Provincia"],
            options=["Comunidad", "Provincia", "Municipio"],
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
        
        elif mapa_opcion == "Municipio":

            mapa_html_municipio = f"{script_dir}/../img/folium_coches.html"
            with open(mapa_html_municipio, "r", encoding="utf-8") as file:
                mapa_municipio_html = file.read()
            st.components.v1.html(mapa_municipio_html, height=1024, width=1180)

    elif choice == "Exploratory Data Analysis":
        explorador.explorador_app()
    elif choice == "Comparador de coches":
        comparador.show(dataframe)
    elif choice == "Cotiza tu coche":
        ml.show()
    elif choice == "Base de datos":
        bd.show()
    else:
        about_us.show()




if __name__ == "__main__":
    main()