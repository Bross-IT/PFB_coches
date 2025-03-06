import pandas as pd
import pickle
import pathlib

import sys
import os

CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "..")))

from limpieza import limpia, transforma_ML
from sklearn.preprocessing import OneHotEncoder

TARGET: str = "precio"

df: pd.DataFrame = limpia.tratamiento_nans(f"{CURRENT_DIR}/../../data/coches_consolidado_limpio.csv")
df = transforma_ML.normalizar(df, ["kilometraje", "potencia", "precio"])

# Dejo solo las variables que nos interesan para el modelo
df_modelo: pd.DataFrame = df[['kilometraje', 'cambio_automatico', 'potencia', 'marca_sola', 'anio_matricula', TARGET]] #cambiar anio_matricula por antiguedad

with open(f"{CURRENT_DIR}/../../bin/cambio_automatico_encoder.pickle", "rb") as file:
    cambio_automatico_encoder: OneHotEncoder = pickle.load(file)

df_modelo["cambio_automatico"] = cambio_automatico_encoder.transform(df_modelo[["cambio_automatico"]])

with open(f"{CURRENT_DIR}/../../bin/dataframe_ml.pickle", "wb") as file:
    pickle.dump(df_modelo, file)
    print(f"Pickle dataframe_ml.pickle generado.")



