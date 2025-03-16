import pandas as pd
import pathlib
import sys

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
src_path = CURRENT_DIR.parent / "src"
sys.path.append(str(src_path))

from extraction import extraction_func
from ocasionDataBase import OcasionDataBase, load_config
from limpieza import limpia


extraction_func.scraper_concesionario("https://www.autocasion.com/concesionarios?order=nombre-a-z", 10)

limpia.limpiar_csv_conces(f"{CURRENT_DIR}/../data/concesionarios.csv")
df_concesionarios = pd.read_csv(f"{CURRENT_DIR}/../data/concesionarios_limpio.csv")

config = load_config(f"{CURRENT_DIR}/../.streamlit/secrets.toml", "database_user")
odb = OcasionDataBase(config)
lista_nombres_concesionarios = odb.obtener_nombres_concesionarios()
df_concesionarios_filtrado = df_concesionarios[~df_concesionarios["nombre"].isin(lista_nombres_concesionarios)]

if len(df_concesionarios_filtrado) > 0:
    odb.process_datos_concesionarios(df_concesionarios_filtrado)
else:
    print("No hay concesionarios que procesar")






