import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import pathlib
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def show():
    st.title("🚗 Comparador de Coches")

    script_dir = pathlib.Path(__file__).resolve().parent
    df = pd.read_csv(f"{script_dir}/../../data/coches_segunda_mano-19-02-2025_limpio.csv")

    col_1, col_2 = st.columns(2)
    with col_1:
        coche_1 = st.selectbox("Selecciona el primer coche", df["modelo_titulo"].unique())

    with col_2:
        coche_2 = st.selectbox("Selecciona el segundo coche", df["modelo_titulo"].unique())

    if coche_1 == coche_2:
        st.warning("Selecciona dos coches diferentes para comparar.")
    else:
        coche_1_data = df[df["modelo_titulo"] == coche_1].iloc[0,1:]
        coche_2_data = df[df["modelo_titulo"] == coche_2].iloc[0,1:]
        imagen_1 = encode_image(coche_1['ruta_imagen'])
        imagen_2 = encode_image(coche_2['ruta_imagen'])


        opciones_caracteristicas = ["kilometraje", "combustible", "distintivo_ambiental", "garantia", "cambio_automatico", "carroceria", "plazas",
                                    "potencia", "puertas", "precio", "consumo_medio", "certificado"]
        caracteristicas = st.multiselect("### Selecciona las características que deseas comparar:", opciones_caracteristicas, default=None)

        if caracteristicas:

            st.write("### 📊 Comparación de Características")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(coche_1)
                if st.checkbox(label = "Mostrar/Ocultar información del coche", key="info_coche_1"):
                    st.write(coche_1_data)

            with col2:
                st.subheader(coche_2)
                if st.checkbox(label = "Mostrar/Ocultar información del coche", key="info_coche_2"):
                    st.write(coche_2_data)