import pandas as pd
import numpy as np

def normalizar(df: pd.DataFrame, columnas: list[str] = ["precio", "kilometraje"]) -> pd.DataFrame:
    df_normalizado: pd.DataFrame = df.copy()
    # Hay registros que hemos decidido dejar para consulta en la web, pero no
    # para los modelos de predicción. Aquí los eliminamos.

    # Por haber encontrado casos con valores erróneos de kilometraje,
    # eliminamos los que superen cierto umbral.
    # Asimismo, por seguridad para las predicciones, eliminamos los coches
    # con potencia fuera de un rango razonable y de precio demasiado pequeño.
    df_normalizado = df_normalizado[(df_normalizado["kilometraje"] <= 375_000) & 
            (df_normalizado["potencia"] >= 10) & (df_normalizado["potencia"] <= 2_500) &
            (df_normalizado["precio"] >= 100)]
    
    # Esta eliminación no la aplicamos en limpia por tener referencias distintas
    # (algunos concesionarios ponen más de una vez el mismo coche, porque se puede
    # recoger en puntos físicos distintos en España).
    columnas_clave = ["modelo_titulo", "kilometraje", "precio"]
    df_normalizado = df_normalizado.drop_duplicates(subset=columnas_clave, keep="first")

    for colunmna in columnas:
        df_normalizado[colunmna] = np.log1p(df_normalizado[colunmna])

    return df_normalizado

