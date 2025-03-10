import streamlit as st
import pathlib

def show():
    script_dir = pathlib.Path(__file__).resolve().parent

    st.markdown("<h1 style='text-align: center;'>👥 Sobre Nosotros</h1>", unsafe_allow_html=True)

    st.write("---")

    col_1, col_2, col_3 = st.columns(3)


    equipo = [
        {"nombre": "🧠 Ambrosio Barceló", "imagen": f"{script_dir}/../img/ambrosio_barcelo.jpg", "descripcion": "Espíritu procesador de datos y mente adaptada a la programación desde los once años de edad. Con amplio background tecnológico en el campo informático y audiovisual, busco ayudar a empresas a solucionar problemas del mundo real a través de la ciencia de datos."},
        {"nombre": "📊 Santiago Tomás Courel", "imagen": f"{script_dir}/../img/santiago_courel_.JPG", "descripcion": "Graduado en Máster en Dirección Financiera con sólida experiencia en planificación y análisis financiero. Actualmente integrando Data Science para potenciar la toma de decisiones estratégicas y optimizar procesos clave. Apasionado por los retos que impulsan la innovación y la transformación digital, busco contribuir con mi experiencia y visión estratégica a proyectos dinámicos que generen impacto y valor."},
        {"nombre": "💾 Jonathan Ordóñez", "imagen": f"{script_dir}/../img/jonathan_ordonez.jpg", "descripcion": ""},
    ]

    for col, miembro in zip([col_1, col_2, col_3], equipo):
        with col:
            st.image(miembro['imagen'], width=200)
            st.markdown(f"### {miembro['nombre']}")
            st.markdown(f"<p style='text-align: left; margin-right: 10px;'>{miembro['descripcion']}</p>", unsafe_allow_html=True)
            st.write("")

    st.write("---")

    st.markdown("<h3 style='text-align: center;'>🚀 Transformamos datos en conocimiento</h3>", unsafe_allow_html=True)
