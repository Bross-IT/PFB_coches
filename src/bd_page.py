import streamlit as st

def show():
    st.markdown("""
    # BASE DE DATOS
    
    Hemos creado el modelo entidad-relación basándonos en aspectos de eficiencia computacional:
    
    - La tabla principal, en vez de contener campos con cadenas, tiene índices a otras tablas con ellos. Así se puede indexar más rápidamente.
    - Los tamaños de cada campo están estudiados para que sean lo más pequeños posible de forma coherente, para ahorrar espacio y hacer la indexación más rápida.
    
    De esta manera, la base de datos será sostenible aun con un volumen de datos mucho mayor del que disponíamos a día que desarrollamos este proyecto (pues todos los días se agregan nuevos coches).
    """)

    st.image("img/er_diagram.png", caption="Diagrama Entidad-Relación", use_container_width=False)

    st.markdown("""
    ### coches_en_venta: 
    Tabla principal, siendo `referencia` la original de autocasion.es sin `ref` delante (valor numérico solo). Contiene ids a los valores que se guardan en cadenas a sus respectivas tablas (*combustible, carroceria, distintivo_ambiental, color, modelo_titulo, concesionario, urls y ruta_imagen*), valores booleanos (*peninsula_y_baleares, cambio_automatico, vendedor_profesional y certificado*) y numéricos propios del coche:
    
    - **kilometraje** (enteros)
    - **potencia** (cv)
    - **garantia** (meses)
    - **plazas** (enteros)
    - **puertas** (enteros)
    - **consumo** (l/km, con dos decimales)
    - **antiguedad** (enteros que son año actual - anio_matricula)
    - **precio** (enteros)
    - **mes_matricula** (entero)
    - **anio_matricula** (entero)
    
    ### Otras tablas y relaciones:
    
    - **urls y ruta_imagen**: Lista de links a la página web de cada coche en autocasion.es y su respectiva ruta a la imagen principal del mismo (relación 1-1 con `coches_en_venta`).
    - **combustible, carroceria, distintivo_ambiental y color**: Contienen los distintos valores de cada uno, con ids referenciados en `coches_en_venta` (1-n).
    - **modelo_titulo**: Contiene el nombre tal y como viene en autocasion.es, pero sin la marca, que está listada en la tabla `marca` (relación 1-n con `coches_en_venta`).
    - **marca**: Contiene todas las marcas de coches, con ids referenciados en `modelo_titulo` (1-n).
    - **concesionario**: Contiene los datos de los concesionarios que venden coches en autocasion.es, con una relación 1-n con `coches_en_venta`. Incluye referencias a ids de `municipio` y `provincia`.
    - **vendedor_particular**: Lista de vendedores particulares con un id autoincremental, relacionados 1-1 con `coches_en_venta`.
    - **municipio**: Lista de municipios indicados en los concesionarios de autocasion.es (1-n).
    - **provincia**: Contiene las provincias indicadas en los concesionarios y de los vendedores particulares (1-n con ambas).
    - **comunidad_autonoma**: Contiene las comunidades autónomas, cuyos ids están referenciados en `provincia` (1-n).
    """)

    return