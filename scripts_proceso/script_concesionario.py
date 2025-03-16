import pandas as pd
import pathlib
import sys
import argparse

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
src_path = CURRENT_DIR.parent / "src"
sys.path.append(str(src_path))

from extraction import extraction_func
from ocasionDataBase import OcasionDataBase, load_config
from limpieza import limpia

parser = argparse.ArgumentParser(description="Script que extrae datos de concesionarios de la web autocasion.es.")
parser.add_argument("num_extraer", type=int, nargs="?", default=None, help="Número de concesionarios a extraer (por defecto todos).")

args = parser.parse_args()
extraction_func.scraper_concesionario("https://www.autocasion.com/concesionarios?order=nombre-a-z", args.num_extraer)

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






