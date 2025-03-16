import pandas as pd
import pickle
import pathlib
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder

import sys
import os

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
src_path = CURRENT_DIR.parent
sys.path.append(str(src_path))

from limpieza import limpia, transforma_ML
import ocasionDataBase as odb


TARGET: str = "precio"

ruta_config: str = f"{CURRENT_DIR}/../../.streamlit/secrets.toml"
dict_config: dict = odb.load_config(ruta_config, "database_user")

db: odb.OcasionDataBase = odb.OcasionDataBase(dict_config)

df: pd.DataFrame = pd.DataFrame(db.obtener_coches_venta())
df = transforma_ML.normalizar(df, ["kilometraje", "potencia", "precio"])

anio_actual: int = datetime.now().year
df['anio_matricula'] = df['anio_matricula'].apply(lambda x: anio_actual - x)

# a raíz de la feature selection
df_modelo: pd.DataFrame = df[['kilometraje', 'cambio_automatico', 'potencia', 'marca_sola', 'antiguedad', TARGET]]

with open(f"{CURRENT_DIR}/../../bin/cambio_automatico_encoder.pickle", "rb") as file:
    cambio_automatico_encoder: OneHotEncoder = pickle.load(file)

cambio_automatico_transformed = cambio_automatico_encoder.transform(df_modelo[["cambio_automatico"]]).astype(int)
df_modelo.loc[:, "cambio_automatico"] = cambio_automatico_transformed

with open(f"{CURRENT_DIR}/../../bin/dataframe_ml.pickle", "wb") as file:
    pickle.dump(df_modelo, file)
    print(f"Pickle dataframe_ml.pickle generado.")



