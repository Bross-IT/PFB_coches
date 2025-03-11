import streamlit as st
import pathlib

def show():
    script_dir = pathlib.Path(__file__).resolve().parent

    st.markdown("<h1 style='text-align: center;'>👥 Sobre Nosotros</h1>", unsafe_allow_html=True)

    st.write("---")

    col_1, col_2, col_3 = st.columns(3)


    equipo = [
        {
            "nombre": "🧠 Ambrosio Barceló", 
            "imagen": f"{script_dir}/../img/ambrosio_barcelo.jpg",
            "linkedin" : "https://www.linkedin.com/in/bronxio",
            "github" : "https://github.com/Bross-IT",
            "descripcion": "Con una mentalidad analítica y experiencia con la programación desde los once años, tengo una sólida formación en informática y audiovisuales. Me especializo en transformar datos en soluciones estratégicas, ayudando a empresas a resolver problemas del mundo real mediante la ciencia de datos. Siempre estoy en busca de nuevas formas de optimizar la toma de decisiones a través del poder de los datos."
         },
        {
            "nombre": "📊 Santiago Tomás Courel", 
            "imagen": f"{script_dir}/../img/santiago_courel.jpg", 
            "linkedin" : "https://www.linkedin.com/in/santiago-tom%C3%A1s-courel-779092186",
            "github" : "https://github.com/19santic92",
            "descripcion": "Graduado en Máster en Dirección Financiera con sólida experiencia en planificación y análisis financiero. Actualmente integrando Data Science para potenciar la toma de decisiones estratégicas y optimizar procesos clave. Apasionado por los retos que impulsan la innovación y la transformación digital, busco contribuir con mi experiencia y visión estratégica a proyectos dinámicos que generen impacto y valor."
        },
        {
            "nombre": "💾 Jonathan Ordóñez", 
            "imagen": f"{script_dir}/../img/jonathan_ordonez.jpg", 
            "linkedin" : "https://www.linkedin.com/in/jonathan-ordo%C3%B1ez-396575a5",
            "github" : "https://github.com/Jonathan-hab",
            "descripcion": "Apasionado por la tecnología y los datos, con experiencia en desarrollo de software y análisis de información. Disfruto explorando nuevas técnicas de Machine Learning, Big Data y visualización de datos para transformar información en conocimiento valioso. Mi objetivo es seguir aprendiendo y creciendo en un entorno dinámico, donde la innovación y la toma de decisiones basadas en datos sean clave para generar impacto."
        },
    ]

    for col, miembro in zip([col_1, col_2, col_3], equipo):
        with col:
            st.image(miembro['imagen'], width=200)
            
            st.markdown(
                f"""
                <p style='text-align: left;'>
                    <a href="{miembro['linkedin']}" target="_blank">
                        <img src="https://img.icons8.com/ios-filled/50/0077B5/linkedin.png" width="20">
                    </a>
                    &nbsp;&nbsp;
                    <a href="{miembro['github']}" target="_blank">
                        <img src="https://img.icons8.com/ios-filled/50/ffffff/github.png" width="20">
                    </a>
                </p>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"### {miembro['nombre']}")
            st.markdown(f"<p style='text-align: left; margin-right: 10px;'>{miembro['descripcion']}</p>", unsafe_allow_html=True)
            st.write("")

    st.write("---")

    st.markdown("<h3 style='text-align: center;'>🚀 Transformamos datos en conocimiento</h3>", unsafe_allow_html=True)
