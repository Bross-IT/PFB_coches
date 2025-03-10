import streamlit as st

st.set_page_config(page_title="Sobre Nosotros", page_icon="🌟", layout="wide")

st.markdown("<h1 style='text-align: center;'>👥 Sobre Nosotros</h1>", unsafe_allow_html=True)

st.write("---")

col_1, col_2, col_3 = st.columns(3)


equipo = [
    {"nombre": "🧠 Ambrosio Barceló", "imagen": "../img/ambrosio_barcelo.jpg", "descripcion": ""},
    {"nombre": "📊 Santiago Tomás Courel", "imagen": "../img/santiago_courel.jpg", "descripcion": ""},
    {"nombre": "💾 Jonathan Ordóñez", "imagen": "../img/jonathan_ordonez.jpg", "descripcion": ""},
]

for col, miembro in zip([col_1, col_2, col_3], equipo):
    with col:
        st.image(miembro["imagen"], width=200)
        st.markdown(f"### {miembro['nombre']}")
        st.write(miembro["descripcion"])
        st.write("")

st.write("---")

st.markdown("<h3 style='text-align: center;'>🚀 Transformamos datos en conocimiento</h3>", unsafe_allow_html=True)
