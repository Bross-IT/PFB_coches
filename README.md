# PFB_coches

PFB_coches es un sitio web de streamlit que trabaja con datos del sitio web autocasion.es.

Aquí se podrán explorar dichos datos con gráficas (EDA), comparar las características de dos coches y cotizar uno cualquiera poniendo los parámetros que más influyen en el precio.

Es un **P**royecto de **F**in de **B**ootcamp de Hackaboss creado por Jonathan Ordóñez, Santiago Tomás Ourel y Ambrosio Barceló en 2025. Tienes más info en la sección "About us" de la web de streamlit.

## Quick Start
Crea un entorno virtual de Python e instala las dependencias necesarias para asegurar que no te falta ninguna librería:
```bash
pip install -r requirements.txt
```

Para visualizar la página con los datos ya extraídos y listos en el repositorio, ejecuta en una terminal en local el comando para abrir streamlit en el navegador por defecto.
```bash
streamlit run src/app.py
```

Si no se pudiese ejecutar directamente de esa manera, usa python en su lugar:
```bash
python -m streamlit run src/app.py
```

Para ejecutar todo el proceso de actualización con una pequeña muestra (desde el scraping hasta el entrenamiento de modelos), ejecuta el siguiente script:
```bash
python src/elscriptencuestion.py
```

Para realizar una actualización completa (con una base de datos vacía puede llevar más de 10 horas), ejecuta el siguiente script:
```bash
python src/scriptdeactualizacióntotal.py
```