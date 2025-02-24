import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import pathlib
  


def explorador_app():

    script_dir = pathlib.Path(__file__).resolve().parent

    st.subheader(body = "Explodor de Coches :chart:")

    st.sidebar.markdown("*"*10)
    st.sidebar.markdown("Selecciona `Año`, `Marca` y `Tipo de Coche` para explorar los datos.")

    df = pd.read_csv(f"{script_dir}\..\data\coches_segunda_mano-19-02-2025_limpio.csv")
    # Obtener rango de años
    min_año = int(df["anio_matricula"].min())
    max_año = int(df["anio_matricula"].max())

    # Slider para filtrar por rango de años
    año_seleccionado = st.sidebar.slider("Selecciona el rango de años", min_año, max_año, (min_año, max_año))

    marcas_disponibles = ["Todos"] + sorted(df["marca_sola"].astype(str).unique().tolist())
    tipos_disponibles = ["Todos"] + sorted(df["carroceria"].astype(str).unique().tolist())

    # Selectores
    marcas_seleccionadas = st.sidebar.multiselect("Selecciona Marca(s)", marcas_disponibles, default="Todos")
    tipos_seleccionados = st.sidebar.multiselect("Selecciona Tipo de Coche", tipos_disponibles, default="Todos")

    # 🔹 APLICAR FILTROS
    df_filtrado = df.copy()
    
    df_filtrado = df[(df["anio_matricula"] >= año_seleccionado[0]) & (df["anio_matricula"] <= año_seleccionado[1])]

    if "Todos" not in marcas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["marca_sola"].isin(marcas_seleccionadas)]
    if "Todos" not in tipos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado["carroceria"].isin(tipos_seleccionados)]

    # 🔹 GRÁFICO DE CAJA (BOXPLOT)
    fig = px.box(df_filtrado, x="marca_sola", y="precio", color="carroceria",
                title="Distribución de precios por Marca y Tipo de Coche",
                labels={"precio": "Precio en Euros", "marca_sola": "Marca", "carroceria": "Tipo de Coche"},
                hover_data=["anio_matricula"])

    fig.update_layout(xaxis_tickangle=-45, width=900, height=500)

    st.plotly_chart(fig)

    
    

if __name__ == "__explorador_app__":
    explorador_app()