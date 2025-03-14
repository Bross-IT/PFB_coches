import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import pathlib
import base64

from sklearn.preprocessing import StandardScaler

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def show(df: pd.DataFrame) -> None:
    st.title("🚗 Comparador de Coches")
    df = df.convert_dtypes()
    st.write(df.dtypes)
    script_dir = pathlib.Path(__file__).resolve().parent
    #df = pd.read_csv(f"{script_dir}/../data/coches_consolidado_limpio.csv")

    col_1, col_2 = st.columns(2)
    coches_seleccionados = {}

    for i, col in enumerate([col_1, col_2], start=1):
        with col:
            coche = st.selectbox(f"Selecciona el coche {i}", df["modelo_titulo"].unique(), key=f"coche_{i}")

            if coche:
                coche_data = df[df["modelo_titulo"] == coche].iloc[0, 1:]
                imagen = encode_image(f"{script_dir}/../{coche_data["ruta_imagen"]}")
                modelo = coche
                coches_seleccionados[f"coche_{i}"] = {"data": coche_data, "imagen": imagen, "modelo": modelo}

                with st.expander(f"📌 Información detallada del coche {i}", expanded=False):
                    st.dataframe(coche_data, use_container_width=True)
                    
    if coches_seleccionados.get("coche_1") and coches_seleccionados.get("coche_2"):
        if coches_seleccionados["coche_1"]["data"].name == coches_seleccionados["coche_2"]["data"].name:
            st.warning("⚠️ Selecciona dos coches diferentes para comparar.")

    st.markdown("---")
    st.header("📊 Selecciona las características que deseas comparar")

    opciones_caracteristicas = ["kilometraje", "cambio_automatico", "plazas",
                                "potencia", "puertas", "precio"]
    
    with st.form(key="form_caracteristicas"):
        caracteristicas = st.multiselect("### Selecciona al menos una caracteristica:", opciones_caracteristicas, default=None)
        confirmar = st.form_submit_button("Confirmar selección")
    
    if confirmar and caracteristicas:
        st.markdown(
                "<h2 style='text-align: center;'>📊 Comparación de Características</h>", 
                unsafe_allow_html=True
            )
        col_1, col_2, col_3 = st.columns([1, 2, 1])
        with col_1:
            st.subheader(coches_seleccionados["coche_1"]["modelo"])
            st.image(coches_seleccionados["coche_1"]["imagen"])
        
        with col_2:                               
            st.markdown(
                "<h3 style='text-align: center;'>Gráfico de radar</h3>", 
                unsafe_allow_html=True
            )
            scaler = StandardScaler()
            categorias = coches_seleccionados["coche_1"]["data"][caracteristicas].keys()
            valores_1: np.ndarray = scaler.fit_transform(coches_seleccionados["coche_1"]["data"][categorias].values.reshape(-1,1))
            valores_2: np.ndarray = scaler.fit_transform(coches_seleccionados["coche_2"]["data"][categorias].values.reshape(-1,1))

            df_comparar = pd.DataFrame({coches_seleccionados["coche_1"]["modelo"] :valores_1.flatten(),
                                        coches_seleccionados["coche_2"]["modelo"] :valores_2.flatten()},
                                        index=categorias).reset_index().rename(columns={'index':'Característica'})


            df_comparar = pd.melt(df_comparar, id_vars=['Característica'], var_name= "Modelos", value_name="Valor")
            fig = px.line_polar(df_comparar, r="Valor", theta="Característica", color="Modelos",
                                line_close=True)

            fig.update_traces(fill='toself', marker=dict(color="blue", size=2))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        tickfont=dict(color="black", size=14), 
                        range=[-1, max(df_comparar['Valor']) + 0.1]
                    )
                ),
                legend=dict(
                        orientation="v",
                        yanchor="bottom",
                        y=1.05,
                        xanchor="right",
                        x=0.25,
                        font=dict(size=12)
                    ),
                    margin=dict(t=0, b=0, l=0, r=0)
                )

            st.plotly_chart(fig)

        with col_3:
            st.subheader(coches_seleccionados["coche_2"]["modelo"])
            st.image(coches_seleccionados["coche_2"]["imagen"])
