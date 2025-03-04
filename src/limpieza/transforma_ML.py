from sklearn.preprocessing import RobustScaler
import pandas as pd

def normalizar(df, campos):
    df = df.copy()

    df = df[(df["kilometraje"] >= 375000) & 
            (df["potencia"] >= 10) & 
            (df["precio"] >= 100)]

    scaler = RobustScaler()
    
    df[campos] = scaler.fit_transform(df[campos])  

    return df

