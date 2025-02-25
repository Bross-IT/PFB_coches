import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import pathlib
import json
import os
import streamlit.components.v1 as components

import explorador

from ml_func import PAGE_CONFIG

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

        df = pd.read_csv(f'{script_dir}\..\data\municipios_cloropetico.csv')
        
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
            geojson_url_municipios = f'{script_dir}/geojson/municipios_espana.geojson'

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

    elif choice == "Explorador de coches":
        explorador.explorador_app()
    elif choice == "Comparador de coches":
        #ml_app()
        st.write("**Sitio en construcción**.")
    else:
        #about_app()
        st.write("**Sitio en construcción**.")




if __name__ == "__main__":
    main()