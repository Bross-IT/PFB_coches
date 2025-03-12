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

    st.write("""Descubre todo lo que sabes sobre los coches de segunda mano en este espacio interactivo, 
             donde encontrarás la información necesaria para enteder nuestra calculadora de precios pudiendo,
             además, filtrar por marca, tipo de coche y año.""")

    st.sidebar.markdown("*" * 10)
    st.sidebar.markdown("Selecciona `Año`, `Marca` y `Tipo de Coche` para explorar los datos.")

    df = pd.read_csv(f"{script_dir}/../data/coches_consolidado_limpio.csv")
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

    marcas_txt = "de todas las marcas" if "Todos" in marcas_seleccionadas else f"marca {', '.join(marcas_seleccionadas)}"
    tipos_txt = "todos los tipos" if "Todos" in tipos_seleccionados else f"tipo {', '.join(tipos_seleccionados)}"
    observacion_boxplot = """Se pueden observar valores máximos, mínimos, medianas, medias y cuartiles, y si corresponde, 
                            valores atípicos en la distribución de precio en cada categoría."""

    df_filtrado = df_sin_outliers.copy()
    
    df_filtrado = df_filtrado[(df_filtrado["anio_matricula"] >= año_seleccionado[0]) & (df_filtrado["anio_matricula"] <= año_seleccionado[1])]

    if "Todos" not in marcas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["marca_sola"].isin(marcas_seleccionadas)]
    if "Todos" not in tipos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado["carroceria"].isin(tipos_seleccionados)]

    #Heatmap de correlación de variables

    label_dict =   {'kilometraje': 'Kilometraje',
                    'garantia': 'Garantía',
                    'plazas': 'Plazas',
                    'potencia': 'Potencia',
                    'puertas': 'Puertas',
                    'precio': 'Precio',
                    'consumo_medio': 'Consumo Medio',
                    'mes_matricula': 'Mes de Matrícula',
                    'anio_matricula': 'Año de Matrícula'
                    }
    columnas_heatmap = ['kilometraje','garantia', 'plazas', 'potencia', 'puertas', 'precio', 'consumo_medio', 'mes_matricula', 'anio_matricula']
    matriz_correl = df_filtrado[columnas_heatmap].corr()
    heatmap = px.imshow(img = matriz_correl,
                        labels = label_dict,
                        title = "Correlación de las variables de Coches",
                        color_continuous_scale=[(0, "blue"), (0.5, "white"), (1, "green")],
                        text_auto = True)
    heatmap.update_layout(
    xaxis=dict(tickmode='array', tickvals=list(range(len(matriz_correl.columns))), ticktext=[label_dict[col] for col in matriz_correl.columns]),
    yaxis=dict(tickmode='array', tickvals=list(range(len(matriz_correl.columns))), ticktext=[label_dict[col] for col in matriz_correl.columns])
)
    st.plotly_chart(heatmap)

    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar el gráfico de correlación de variables.')
    else:
       
        st.write(f"En este Heatmap se muestra la correlación de variables de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")

    #Histograma de distribución de precios

    df_histograma = df.copy()
    df_histograma['tipo'] = df_histograma['precio'].apply(lambda x: "Outlier" if x > lim_der or x < lim_izq else "Normal") 

    df_histograma = df_histograma[(df_histograma["anio_matricula"] >= año_seleccionado[0]) & (df_histograma["anio_matricula"] <= año_seleccionado[1])]

    if "Todos" not in marcas_seleccionadas:
        df_histograma = df_histograma[df_histograma["marca_sola"].isin(marcas_seleccionadas)]
    if "Todos" not in tipos_seleccionados:
        df_histograma = df_histograma[df_histograma["carroceria"].isin(tipos_seleccionados)]

    histograma = px.histogram(data_frame = df_histograma, 
             x                  = "precio",
             nbins              = 50,
             color              = 'tipo',
             color_discrete_map = {'Normal':'blue','Outlier':'red'},
             title              = 'Distribución de precios y sus outliers',
             labels             = {'precio': 'Precio en Euros', 'tipo': 'Tipo'})

    st.plotly_chart(histograma)

    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar el gráfico de distribución de precios.')
    else:
       
        st.write(f"En este Histograma se muestra la distribución de precios de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}, diferenciando a sus outliers.")

    #Evolución del precio medio según el año de antigüedad

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

    # Gráfico de distribución de precios por marca y tipo de coche
    orden_marcas = df_filtrado.groupby("marca_sola")["precio"].mean().sort_values(ascending=False).index.tolist()

    df_filtrado["marca_sola"] = pd.Categorical(df_filtrado["marca_sola"], categories=orden_marcas, ordered=True)

    df_ordenado = df_filtrado.sort_values(by="marca_sola", key=lambda x: x.map({val: i for i, val in enumerate(orden_marcas)}))

    fig = px.box(df_ordenado, 
                x="marca_sola", 
                y="precio", 
                color="carroceria",
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
    
        st.write(f"En este Boxplot se muestra la distribución de precios de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")
        st.write(observacion_boxplot)

    #Gráfico distribución de precios según distintivo ambiental y tipo de combustible
    
    orden_distintivo = df_filtrado.groupby("distintivo_ambiental")["precio"].mean().sort_values(ascending=False).index.tolist()
    orden_combustible = df_filtrado.groupby("combustible")["precio"].mean().sort_values(ascending=False).index.tolist()

    df_filtrado["distintivo_ambiental"] = pd.Categorical(df_filtrado["distintivo_ambiental"], categories=orden_distintivo, ordered=True)
    df_filtrado["combustible"] = pd.Categorical(df_filtrado["combustible"], categories=orden_combustible, ordered=True)

    df_ordenado_distintivo = df_filtrado.sort_values(by="distintivo_ambiental", key=lambda x: x.map({val: i for i, val in enumerate(orden_distintivo)}))
    df_ordenado_combustible = df_filtrado.sort_values(by="combustible", key=lambda x: x.map({val: i for i, val in enumerate(orden_combustible)}))

    fig = sp.make_subplots(
        rows=1, cols=2,  
        subplot_titles=("Distribución de precios según Distintivo Ambiental", "Distribución de precios según Combustible"),
        vertical_spacing=0.15
    )

    fig.add_trace(go.Box(
        y=df_ordenado_distintivo['precio'],
        x=df_ordenado_distintivo['distintivo_ambiental'],
        name='Distribución de precios según Distintivo Ambiental',
        boxmean='sd',  
        marker=dict(color='lightblue')
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=df_ordenado_combustible['precio'],
        x=df_ordenado_combustible['combustible'],
        name='Distribución de precios según Combustible',
        boxmean='sd', 
        marker=dict(color='lightgreen')
    ), row=1, col=2)

    fig.update_layout(
        title="Distribución de Precios según Distintivo Ambiental y Combustible",
        width=900,  
        height=500,  
        showlegend=False
    )

    fig.update_xaxes(title_text="Distintivo Ambiental", row=1, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=1)

    fig.update_xaxes(title_text="Tipo de Combustible", row=1, col=2)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=2)

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del precio según distintivo ambiental y tipo de combustible.')
    else:
        st.write(f"En este Boxplot se muestra la distribución de precios según distintivo ambiental y combustible de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write(observacion_boxplot)

    #Subplots de distribución de precios segun distintos variables

    fig = sp.make_subplots(
    rows=2, cols=2,  
    subplot_titles=("Distribución de precios según Plazas", "Distribución de precios según Puertas","Distribución de precios según Garantía", "Distribución de precios según Color"),
    vertical_spacing=0.25
    )

    fig.add_trace(go.Box(
        y=df_filtrado['precio'],
        x=df_filtrado['plazas'].astype(str),
        name='Distribución de precios según Plazas',
        boxmean='sd',  
        marker=dict(color='lightblue')
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=df_filtrado['precio'],
        x=df_filtrado['puertas'],
        name='Distribución de precios según Puertas',
        boxmean='sd', 
        marker=dict(color='lightgreen')
    ), row=1, col=2)

    fig.add_trace(go.Box(
        y=df_filtrado['precio'],
        x=df_filtrado['garantia'],
        name='Distribución de precios según Garantía',
        boxmean='sd', 
        marker=dict(color='red')
    ), row=2, col=1)

    fig.add_trace(go.Box(
        y=df_filtrado['precio'],
        x=df_filtrado['color'],
        name='Distribución de precios según Color',
        boxmean='sd', 
        marker=dict(color='orange')
    ), row=2, col=2)

    fig.update_layout(
        title="Distribución de Precios según distintas variables",
        width=900,  
        height=500,  
        showlegend=False
    )

    fig.update_xaxes(title_text="Número de Plazas", row=1, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=1)

    fig.update_xaxes(title_text="Número de Puertas", row=1, col=2)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=2)

    fig.update_xaxes(title_text="Garantía en meses", row=2, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=2, col=1)

    fig.update_xaxes(title_text="Color", row=2, col=2)
    fig.update_yaxes(title_text="Precio en Euros", row=2, col=2)

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del precio según variables.')
    else:
        st.write(f"En este caso, podemos ver la distribución de precios según distintas variables de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write(observacion_boxplot)

    #Subplots de relación entre Kilometraje, Potencia y Precio (escala logarítmica)

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

    fig.update_xaxes(title_text="Kilómetros", row=1, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=1)

    fig.update_xaxes(title_text="Potencia", row=1, col=2)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=2)

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
        st.write('Introduzca un tipo de coche y una marca para visualizar los gráficos de dispersión.')
    else:
        st.write(f"En estos gráficos de dispersión se muestra la distribución de precios de los coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]} en relación al kilometraje y la potencia.")
        st.write("En el gráfico de precios por kilometraje se puede observar que en general, a medida que aumenta el kilometraje, el precio disminuye.")
        st.write("En el de precios por potencia, la relacion es positiva, lo que indica que los coches con potencia más alta tienden a tener precios más altos.")

    #Subplots de distribución de precios según Comunidad, Provincia y Municipio

    orden_marca = df_filtrado.groupby("marca_sola")["consumo_medio"].mean().sort_values(ascending=False).index.tolist()
    orden_combustible = df_filtrado.groupby("combustible")["consumo_medio"].mean().sort_values(ascending=False).index.tolist()

    df_filtrado["marca_sola"] = pd.Categorical(df_filtrado["marca_sola"], categories=orden_marca, ordered=True)
    df_filtrado["combustible"] = pd.Categorical(df_filtrado["combustible"], categories=orden_combustible, ordered=True)

    df_ordenado_marca = df_filtrado.sort_values(by="marca_sola", key=lambda x: x.map({val: i for i, val in enumerate(orden_marca)}))
    df_ordenado_combustible = df_filtrado.sort_values(by="combustible", key=lambda x: x.map({val: i for i, val in enumerate(orden_combustible)}))

    fig = sp.make_subplots(
        rows=1, cols=2,  
        subplot_titles=("Consumo Medio por Marca", "Consumo Medio por Combustible"),
        vertical_spacing=0.1
    )

    fig.add_trace(go.Box(
        y=df_ordenado_marca['consumo_medio'],
        x=df_ordenado_marca['marca_sola'],
        name='Consumo Medio por Marca',
        boxmean='sd',  
        marker=dict(color='lightblue')
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=df_ordenado_combustible['consumo_medio'],
        x=df_ordenado_combustible['combustible'],
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

    fig.update_xaxes(title_text="Marca", row=1, col=1)
    fig.update_yaxes(title_text="Consumo Medio (L/100km)", row=1, col=1)

    fig.update_xaxes(title_text="Tipo de Combustible", row=1, col=2)
    fig.update_yaxes(title_text="Consumo Medio (L/100km)", row=1, col=2)

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del consumo medio según marca, tipo de coche ycombustible.')
    else:
        st.write(f"Aquí podemos apreciar la distribución del consumo medio según marca, tipo de coche y combustible de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write(observacion_boxplot)

    concesionarios = pd.read_csv(f"{script_dir}/../data/concesionarios_limpio.csv")
    concesionarios["municipio"] = concesionarios["municipio"].str.replace("Municipio: ", "", regex=True)
    
    concesionarios['nombre'] = concesionarios['nombre'].apply(lambda x: x.upper())
    concesionarios = concesionarios.rename(columns={'nombre': 'nombre_vendedor'})
    concesionarios = concesionarios[["nombre_vendedor", "municipio", "codigo_postal"]]

    df_municipios = df_sin_outliers.copy()
    df_municipios['nombre_vendedor'] = df_municipios['nombre_vendedor'].fillna('').apply(lambda x: x.replace('\r', ''))
    df_unido = pd.merge(df_municipios, concesionarios, on='nombre_vendedor', how='left')

    orden_comunidad = df_filtrado.groupby("comunidad")["precio"].mean().sort_values(ascending=False).index.tolist()
    orden_provincia = df_filtrado.groupby("provincia")["precio"].mean().sort_values(ascending=False).index.tolist()
    orden_municipio = df_unido.groupby("municipio")["precio"].mean().sort_values(ascending=False).index.tolist()

    df_filtrado["comunidad"] = pd.Categorical(df_filtrado["comunidad"], categories=orden_comunidad, ordered=True)
    df_filtrado["provincia"] = pd.Categorical(df_filtrado["provincia"], categories=orden_provincia, ordered=True)
    df_unido["municipio"] = pd.Categorical(df_unido["municipio"], categories=orden_municipio, ordered=True)

    df_ordenado_comunidad = df_filtrado.sort_values(by="comunidad", key=lambda x: x.map({val: i for i, val in enumerate(orden_comunidad)}))
    df_ordenado_provincia = df_filtrado.sort_values(by="provincia", key=lambda x: x.map({val: i for i, val in enumerate(orden_provincia)}))
    df_ordenado_municipio = df_unido.sort_values(by="municipio", key=lambda x: x.map({val: i for i, val in enumerate(orden_municipio)}))

    fig = sp.make_subplots(
        rows=3, cols=1,  
        subplot_titles=("Distribución de Precio por Comunidad", "Distribución de Precio por Provincia", "Distribución de Precio por Municipio"),
        vertical_spacing=0.3
    )

    fig.add_trace(go.Box(
        y=df_ordenado_comunidad['precio'],
        x=df_ordenado_comunidad['comunidad'],
        name='Distribución de Precio por Comunidad',
        boxmean='sd',  
        marker=dict(color='lightblue')
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=df_ordenado_provincia['precio'],
        x=df_ordenado_provincia['provincia'],
        name='Distribución de Precio por Provincia',
        boxmean='sd', 
        marker=dict(color='lightgreen')
    ), row=2, col=1)

    fig.add_trace(go.Box(
        y=df_ordenado_municipio['precio'],
        x=df_ordenado_municipio['municipio'],
        name='Distribución de Precio por Municipio',
        boxmean='sd', 
        marker=dict(color='lightgreen')
    ), row=3, col=1)

    fig.update_layout(
        title="Distribución de Precio por Comunidad, Provincia y Municipio",
        width=900,  
        height=800,  
        showlegend=False
    )

    fig.update_xaxes(title_text="Comunidad", row=1, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=1, col=1)

    fig.update_xaxes(title_text="Provincia", row=2, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=2, col=1)

    fig.update_xaxes(title_text="Municipio", row=3, col=1)
    fig.update_yaxes(title_text="Precio en Euros", row=3, col=1)

    st.plotly_chart(fig)

    if not marcas_seleccionadas or not tipos_seleccionados:
            st.write('Introduzca tipo de coche y una marca para visualizar la distribución del precio según Comunidad, Provincia y Municipio.')
    else:
        st.write(f"A partir destros tres gráficos, podemos notar la distribución de precios según Comunidad, Provincia y Municipio de coches {marcas_txt} de {tipos_txt} entre los años {año_seleccionado[0]} y {año_seleccionado[1]}.")    
        st.write(observacion_boxplot)
         

if __name__ == "__main__":
    explorador_app()