# PFB_coches

PFB_coches es un sitio web de streamlit que trabaja con datos del sitio web autocasion.es.

Aquí se podrán explorar dichos datos con gráficas (EDA), comparar las características de dos coches y cotizar uno cualquiera poniendo los parámetros que más influyen en el precio.

Es un **P**royecto de **F**in de **B**ootcamp de Hackaboss creado por Jonathan Ordóñez, Santiago Tomás Courel y Ambrosio Barceló en 2025. Tienes más info en la sección "About us" de la web de streamlit.

## Requisitos previos
Crea un entorno virtual de Python e instala las dependencias necesarias para asegurar que no te falta ninguna librería:
```bash
pip install -r requirements.txt
```

## Ver página de streamlit
Para visualizar la página con los datos ya extraídos y listos en el repositorio, ejecuta en una terminal en local el comando para abrir streamlit en el navegador por defecto.
```bash
streamlit run src/app.py
```

Si no se pudiese ejecutar directamente de esa manera, usa python en su lugar:
```bash
python -m streamlit run src/app.py
```
## Extracción de datos y actualización de base de datos
Para ejecutar todo el proceso de actualización con una pequeña muestra de coches/concesionarios (desde el scraping hasta el guardado en BBDD), 20 en el ejemplo, ejecuta los siguientes scripts:
```bash
python scripts_proceso/script_coches.py 20
```
ó
```bash
python scripts_proceso/script_concesionario.py 20
```

Para realizar una actualización completa (con una base de datos vacía puede llevar más de 10 horas), ejecuta los siguientes scripts:
```bash
python scripts_proceso/script_coches.py
```
ó
```bash
python scripts_proceso/script_concesionario.py
```
## Entrenamiento de modelos predictivos
Para entrenar el modelo de machine learning (predicción con random forest), ejecuta:
```bash
python src/machinelearning/modelo_ml.py
```
Para entrenar el modelo de deep learning (predicción con red neuronal), ejecuta:
```bash
python src/machinelearning/modelo_dl.py
```
### NOTA:
Hay un bug en este último script, ya que el archivo pickle del history para graficar luego en Cotiza Tu Coche en streamlit se genera mal (a pesar de que el código sea igual que en el notebook). Sin estar resuelto, en su lugar, ejecuta las celdas del notebook hasta la parte de red neuronal de regresión (es decir, hasta la 6ª celda, pues las dos siguientes no hacen falta):
```bash
notebooks/ejecutar_deep_learning.ipynb
```