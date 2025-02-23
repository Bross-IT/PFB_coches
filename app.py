import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import pathlib
from src.ml_func import PAGE_CONFIG

def main():
    script_dir = pathlib.Path(__file__).resolve().parent

    st.set_page_config(**PAGE_CONFIG)

    menu = ["Main App", "Explorador de coches","Comparador de coches", "Cotiza tu coche"]

    choice = st.sidebar.selectbox(label = "Menu", options = menu, index = 0)

    if choice == "Main App":
        st.subheader(body = "Home :house:")

        st.write("**Bienvenidos a la mejor web para encontrar tu coche de segunda mano hecha con Streamlit**.")

        st.markdown("""Toda la información recopilada en este proyecto proviene de la siguiente web de coches: 
                       [Autocasión](https://www.autocasion.com/coches-segunda-mano).""")

        st.write("""Para entender bien los datos con los que se construyó nuestra calculadora de precios, dirígete a la sección `Explorador de coches` del menú lateral.""")

        st.write("""Si estas buscando tu próximo coche y no te decides por cual, puede usar nuestro `Comparador de coches` dirigiendote al menú lateral.""")
        
        st.write("""Para cotizar tu coche, dirígete a la sección `Cotiza tu coche` del menú lateral.""")

        
        df = pd.read_csv(f"{script_dir}\data\coches_segunda_mano-19-02-2025_limpio.csv")
        st.dataframe(df)
    elif choice == "Explorador de coches":
        #eda_app()
        st.write("**Sitio en construcción**.")
    elif choice == "Comparador de coches":
        #ml_app()
        st.write("**Sitio en construcción**.")
    else:
        #about_app()
        st.write("**Sitio en construcción**.")




if __name__ == "__main__":
    main()