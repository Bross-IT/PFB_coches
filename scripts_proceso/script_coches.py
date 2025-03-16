import pandas as pd
import pathlib
import sys

from datetime import datetime

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
src_path = CURRENT_DIR.parent / "src"
sys.path.append(str(src_path))

from extraction import extraction_func
from ocasionDataBase import OcasionDataBase, load_config
from limpieza import limpia


extraction_func.scraper_coches("https://www.autocasion.com/coches-ocasion?direction=desc&page=1&sort=updated_at", 30)

hoy = datetime.now().strftime('%d-%m-%Y')
limpia.limpiar_csv(f"{CURRENT_DIR}/../data/coches_segunda_mano-{hoy}.csv")
limpia.tratamiento_nans(f"{CURRENT_DIR}/../data/coches_segunda_mano-{hoy}_limpio.csv")

df_coches = pd.read_csv(f"{CURRENT_DIR}/../data/coches_segunda_mano-{hoy}_limpio_nonans.csv", parse_dates=["fecha_extraccion"], dtype={
            "puertas": "Int64", "mes_matricula": "Int64", "anio_matricula": "Int64"
        })

config = load_config(f"{CURRENT_DIR}/../.streamlit/secrets.toml", "database_user")
odb = OcasionDataBase(config)
listado_referencias = odb.obtener_referencias()
df_coches_filtrado = df_coches[~df_coches["referencia"].isin(listado_referencias)]

if len(df_coches_filtrado) > 0:
    odb.process_datos_coches(df_coches_filtrado)
else:
    print("No hay coches que procesar.")

