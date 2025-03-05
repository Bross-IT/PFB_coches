from sklearn.preprocessing import RobustScaler
import pandas as pd

def normalizar(df, campos):
    df = df.copy()

    # Hay registros que hemos decidido dejar para consulta en la web, pero no
    # para los modelos de predicción. Aquí los eliminamos.

    # Por haber encontrado casos con valores erróneos de kilometraje,
    # eliminamos los que superen cierto umbral.
    # Asimismo, por seguridad para las predicciones, eliminamos los coches
    # con potencia fuera de un rango razonable y de precio demasiado pequeño.
    df = df[(df["kilometraje"] <= 375_000) & 
            (df["potencia"] >= 10) & (df["potencia"] <= 2_500)
            (df["precio"] >= 100)]
    
    # Esta eliminación no la aplicamos en limpia por tener referencias distintas
    # (algunos concesionarios ponen más de una vez el mismo coche, porque se puede
    # recoger en puntos físicos distintos en España).
    columnas_clave = ["modelo_titulo", "kilometraje", "precio"]
    df = df.drop_duplicates(subset=columnas_clave, keep="first")

    scaler = RobustScaler()
    
    df[campos] = scaler.fit_transform(df[campos])  

    return df

