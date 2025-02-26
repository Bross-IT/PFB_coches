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

    st.subheader("Explorador de Coches 🚗🔍")

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
    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar el gráfico de distribución de precios.')
    else:
        marcas_txt = "de todas las marcas" if "Todos" in marcas_seleccionadas else f"marca {', '.join(marcas_seleccionadas)}"
        tipos_txt = "todos los tipos" if "Todos" in tipos_seleccionados else f"tipo {', '.join(tipos_seleccionados)}"
    
        st.write(f"En este gráfico Boxplot se muestra la distribución de precios de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")
        st.write("Se pueden observar valores máximos, mínimos, medianas, medias y cuartiles, y si corresponde, valores atípicos en la distribución de precio en cada categoría.")

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

    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar el gráfico de evolución del precio medio.')
    else:
        st.write(f"En este gráfico de línea se muestra la evolución del precio medio {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    

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

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del precio según distintivo ambiental y tipo de combustible.')
    else:
        st.write(f"En este gráfico se muestra la distribución de precios según distintivo ambiental y combustible de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write("Se pueden observar valores máximos, mínimos, medianas, medias y cuartiles, y si corresponde, valores atípicos en la distribución de precio en cada categoría.")
    
    fig = sp.make_subplots(
        rows=1, cols=2,  
        subplot_titles=("Kilometraje vs Precio en escala logarítmica", "Potencia vs Precio en escala logarítmica"),
        vertical_spacing=0.1
    )

    df_scatter = df_filtrado.copy()
    df_scatter['precio'] = df_scatter['precio'].replace(0,np.nan)
    df_scatter['kilometraje'] = df_scatter['kilometraje'].replace(0,np.nan)
    df_scatter['potencia'] = df_scatter['potencia'].replace(0,np.nan)

    fig.add_trace(go.Scatter(
        x=np.log(df_scatter['kilometraje']), 
        y=np.log(df_scatter['precio']),
        mode='markers',
        name='Kilometraje',
        marker=dict(color='lightblue', size=6),
        hovertext=df_scatter.apply(lambda row: f"Marca: {row['marca_sola']}<br>Modelo: {row['modelo_titulo']}<br>Precio: {row['precio']}<br>Kilometraje: {row['kilometraje']}", axis=1),
        hoverinfo='text'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=np.log(df_scatter['potencia']),
        y=np.log(df_scatter['precio']),
        mode='markers',
        name='Potencia',
        marker=dict(color='lightgreen', size=6),
        hovertext=df_scatter.apply(lambda row: f"Marca: {row['marca_sola']}<br>Modelo: {row['modelo_titulo']}<br>Precio: {row['precio']}<br>Potencia: {row['potencia']}", axis=1),
        hoverinfo='text'
    ), row=1, col=2)

    fig.update_layout(
        title="Relación entre Kilometraje, Potencia y Precio (escala logarítmica)",
        width=900,  
        height=500,  
        showlegend=True
    )

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar los gráficos de dispersión.')
    else:
        st.write(f"En estos gráficos de dispersión se muestra la distribución de precios de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]} en relación al kilometraje y la potencia.")
        st.write("En el gráfico de precios por kilometraje se puede observar que en general, a medida que aumenta el kilometraje, el precio disminuye.")
        st.write("En el gráfico de precios por potencia, la relacion es positiva, lo que indica que los coches con potencia más alta tienden a tener precios más altos.")

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

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del consumo medio según marca, tipo de coche ycombustible.')
    else:
        st.write(f"En este gráfico se muestra la distribución del consumo medio según marca, tipo de coche y combustible de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write("Se pueden observar valores máximos, mínimos, medianas, medias y cuartiles, y si corresponde, valores atípicos en la distribución de precio en cada categoría.")
    

if __name__ == "__main__":
    explorador_app()