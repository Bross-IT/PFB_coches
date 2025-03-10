import numpy as np
import pandas as pd

import pickle
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from limpieza import limpia
import pathlib


def dividir_dataframe(df: pd.DataFrame, target: str, test_size: float = 0.2, random_state: int = 42) -> pd.DataFrame:
    X = df.drop(columns=target)
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test

def generar_pickle_label_encoding(df: pd.DataFrame, columnas: list[str]) -> None:
    for columna in columnas:
        le = LabelEncoder()
        le.fit(df[columna].astype(str))

        with open(f"../bin/{columna}_encoder.pickle", "wb") as file:
            pickle.dump(le, file)
            print(f"Pickle LE {columna}_encoder.pickle generado.")
    
def generar_pickle_onehot_encoding(df: pd.DataFrame, columnas: list[str]) -> None:
    for columna in columnas:
        ol = OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False)
        ol.fit(df[[columna]])

        with open(f"../bin/{columna}_encoder.pickle", "wb") as file:
            pickle.dump(ol, file)
            print(f"Pickle OHE {columna}_encoder.pickle generado.")

def generar_pickle_target_encoding(x: pd.DataFrame, y: pd.DataFrame, columnas: list[str], target: str) -> None:

    for columna in columnas:
        te = ce.TargetEncoder(cols=[columna])
        te.fit(x[columna], y)

        with open(f"../bin/{columna}_{target}_encoder.pickle", "wb") as file:
            pickle.dump(te, file)
            print(f"Pickle TE {columna}_{target}_encoder.pickle generado.")

