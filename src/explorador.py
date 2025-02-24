import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import pathlib
  


def explorador_app():

    script_dir = pathlib.Path(__file__).resolve().parent

    st.subheader("Explorador de Coches :chart:")

    st.sidebar.markdown("*" * 10)
    st.sidebar.markdown("Selecciona `Año`, `Marca` y `Tipo de Coche` para explorar los datos.")

    df = pd.read_csv(f"{script_dir}/../data/coches_segunda_mano-19-02-2025_limpio.csv")
    q1 = df['precio'].quantile(0.25)
    q3 = df['precio'].quantile(0.75)
    ric = q3 - q1

    lim_izq = q1 - 1.5 * ric
    lim_der = q3 + 1.5 * ric

    df_sin_outliers = df[(df['precio'] >= lim_izq) & (df['precio'] <= lim_der)]

    min_año = int(df["anio_matricula"].min())
    max_año = int(df["anio_matricula"].max())

    año_seleccionado = st.sidebar.slider("Selecciona el rango de años", min_año, max_año, (min_año, max_año))

    marcas_disponibles = ["Todos"] + sorted(df["marca_sola"].astype(str).unique().tolist())
    tipos_disponibles = ["Todos"] + sorted(df["carroceria"].astype(str).unique().tolist())

    marcas_seleccionadas = st.sidebar.multiselect("Selecciona Marca(s)", marcas_disponibles, default="Todos")
    tipos_seleccionados = st.sidebar.multiselect("Selecciona Tipo de Coche", tipos_disponibles, default="Todos")

    df_filtrado = df_sin_outliers.copy()
    
    df_filtrado = df_filtrado[(df_filtrado["anio_matricula"] >= año_seleccionado[0]) & (df_filtrado["anio_matricula"] <= año_seleccionado[1])]

    if "Todos" not in marcas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["marca_sola"].isin(marcas_seleccionadas)]
    if "Todos" not in tipos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado["carroceria"].isin(tipos_seleccionados)]

    fig = px.box(df_filtrado, x="marca_sola", y="precio", color="carroceria",
                 title="Distribución de precios por Marca y Tipo de Coche",
                 labels={"precio": "Precio en Euros", "marca_sola": "Marca", "carroceria": "Tipo de Coche", "modelo_titulo": "Modelo"},
                 hover_data=["modelo_titulo"])

    fig.update_layout(xaxis_tickangle=-45, width=900, height=500)

    st.plotly_chart(fig)

    df_promedio = df_filtrado.groupby('anio_matricula')['precio'].mean().reset_index()

    fig_anio_matricula = px.line(df_promedio, x='anio_matricula', y='precio', 
                                title='Evolución del precio medio según el año de antigüedad',
                                labels={'anio_matricula': 'Año', 'precio': 'Precio Medio en Euros'})

    fig_anio_matricula.update_layout(
        xaxis_title="Año", 
        yaxis_title="Precio Medio en Euros",
        width=900, 
        height=500
    )

    st.plotly_chart(fig_anio_matricula)

    fig = go.Figure()

    fig.add_trace(go.Box(
        x=df_filtrado['distintivo_ambiental'],
        y=df_filtrado['precio'],
        name='Distintivo Ambiental',
        boxmean='sd',
        marker_color='lightblue'
    ))

    fig.add_trace(go.Box(
        x=df_filtrado['combustible'],
        y=df_filtrado['precio'],
        name='Combustible',
        boxmean='sd',
        marker_color='lightgreen'
    ))

    fig.update_layout(
        title="Distribución de precios por Distintivo Ambiental y Combustible",
        xaxis_title="Categorías",
        yaxis_title="Precio en Euros",
        width=900, 
        height=500
    )

    st.plotly_chart(fig)

    fig = sp.make_subplots(
        rows=1, cols=2,  
        subplot_titles=("Kilometraje vs Precio", "Potencia vs Precio"),
        vertical_spacing=0.1
    )

    fig.add_trace(go.Scatter(
        x=df_filtrado['kilometraje'],
        y=df_filtrado['precio'],
        mode='markers',
        name='Kilometraje',
        marker=dict(color='lightblue', size=6)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_filtrado['potencia'],
        y=df_filtrado['precio'],
        mode='markers',
        name='Potencia',
        marker=dict(color='lightgreen', size=6)
    ), row=1, col=2)

    fig.update_layout(
        title="Relación entre Kilometraje, Potencia y Precio",
        width=900,  
        height=500,  
        showlegend=True
    )

    st.plotly_chart(fig)

    fig = sp.make_subplots(
        rows=1, cols=2,  
        subplot_titles=("Consumo Medio por Marca", "Consumo Medio por Combustible"),
        vertical_spacing=0.1
    )

    fig.add_trace(go.Box(
        y=df_filtrado['consumo_medio'],
        x=df_filtrado['marca_sola'],
        name='Consumo Medio por Marca',
        boxmean='sd',  
        marker=dict(color='lightblue')
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=df_filtrado['consumo_medio'],
        x=df_filtrado['combustible'],
        name='Consumo Medio por Combustible',
        boxmean='sd', 
        marker=dict(color='lightgreen')
    ), row=1, col=2)

    fig.update_layout(
        title="Distribución del Consumo Medio por Marca y Combustible",
        width=900,  
        height=500,  
        showlegend=False
    )

    st.plotly_chart(fig)

if __name__ == "__main__":
    explorador_app()