import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import pathlib
import streamlit.components.v1 as components

from src import explorador

from src.ml_func import PAGE_CONFIG

def main():
    script_dir = pathlib.Path(__file__).resolve().parent

    st.set_page_config(**PAGE_CONFIG)

    menu = ["Home", "Explorador de coches","Comparador de coches", "Cotiza tu coche"]

    choice = st.sidebar.selectbox(label = "Menu", options = menu, index = 0)

    if choice == "Home":
        st.subheader(body = "Home :house:")

        st.write("**Bienvenidos a la mejor web para encontrar tu coche de segunda mano hecha con Streamlit**.")

        st.markdown("""Toda la información recopilada en este proyecto proviene de la siguiente web de coches: 
                       [Autocasión](https://www.autocasion.com/coches-segunda-mano).""")

        st.write("""Para entender bien los datos con los que se construyó nuestra calculadora de precios, dirígete a la sección `Explorador de coches` del menú lateral.""")

        st.write("""Si estas buscando tu próximo coche y no te decides por cual, puedes usar nuestro `Comparador de coches` dirigiendote al menú lateral.""")
        
        st.write("""Para cotizar tu coche, dirígete a la sección `Cotiza tu coche` del menú lateral.""")

        
        df = pd.read_csv(f"{script_dir}\data\coches_segunda_mano-19-02-2025_limpio.csv")
        
        mapa_opcion = st.selectbox(
            label="Selecciona el nivel de geografía para visualizar el mapa",
            options=["Comunidad", "Provincia", "Municipio"],
            index=0  
        )

        if mapa_opcion == "Comunidad":
            mapa_html_comunidad = f"{script_dir}\img\mapa_comunidades.html"
            with open(mapa_html_comunidad, "r", encoding="utf-8") as file:
                mapa_comunidad_html = file.read()
            st.components.v1.html(mapa_comunidad_html, height=1024, width=1180)

        elif mapa_opcion == "Provincia":
            mapa_html_provincia = f"{script_dir}\img\mapa_provincias.html"
            with open(mapa_html_provincia, "r", encoding="utf-8") as file:
                mapa_provincia_html = file.read()
            st.components.v1.html(mapa_provincia_html, height=1024, width=1180)

        elif mapa_opcion == "Municipio":
            mapa_html_municipio = f"{script_dir}\img\mapa_municipios.html"
            with open(mapa_html_municipio, "r", encoding="utf-8") as file:
                mapa_municipio_html = file.read()
            st.components.v1.html(mapa_municipio_html, height=1024, width=1180)





    elif choice == "Explorador de coches":
        explorador.explorador_app()
        st.write("**Sitio en construcción**.")
    elif choice == "Comparador de coches":
        #ml_app()
        st.write("**Sitio en construcción**.")
    else:
        #about_app()
        st.write("**Sitio en construcción**.")




if __name__ == "__main__":
    main()