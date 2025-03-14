import pandas as pd
import numpy as np
import pickle

import os
import sys

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor

import encoding_func

def entrenar_modelo():

    notebook_path = os.path.abspath(".")
    sys.path.append(os.path.abspath(os.path.join(notebook_path, '..', 'src')))

    df_modelo = pd.read_pickle('../bin/dataframe_ml.pickle')

    with open(f"../bin/marca_sola_precio_encoder.pickle", "rb") as file:
        marca_sola_precio_encoder = pickle.load(file)

    with open(f"../bin/min_max_scaler.pickle", "rb") as file:
        min_max_scaler = pickle.load(file)   

    TARGET = "precio"

    X_train, X_test, y_train, y_test = encoding_func.dividir_dataframe(df_modelo, TARGET, test_size=0.2, random_state=42)

    X_train["marca_sola"] = marca_sola_precio_encoder.transform(X_train["marca_sola"])
    X_test["marca_sola"] = marca_sola_precio_encoder.transform(X_test["marca_sola"])

    X_train = min_max_scaler.transform(X_train)
    X_test = min_max_scaler.transform(X_test)

    modelos = {
        "Regresión Lineal": LinearRegression(),
        "Árbol de Decisión": DecisionTreeRegressor(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "K-Vecinos": KNeighborsRegressor(n_neighbors=5)
    }

    resultados = []

    for nombre, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        
        resultados.append({
            "Modelo": nombre,
            "MAE": mean_absolute_error(y_test, y_pred),
            "MSE": mean_squared_error(y_test, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
            "R2": r2_score(y_test, y_pred)
        })


    df_resultados = pd.DataFrame(resultados).sort_values(by="R2", ascending=False)

    df_resultados.to_pickle("../bin/resultados_modelos_ml.pickle")

    from sklearn.model_selection import GridSearchCV

    parametros_rf = {
        "n_estimators": [100, 150, 200, 250],
        "max_depth": [None, 5],
        "min_samples_split": [8, 10, 12],
        "min_samples_leaf": [4, 6, 8]
    }
    modelo_rf = RandomForestRegressor(random_state=42)

    grid_search_rf = GridSearchCV(
        modelo_rf,
        parametros_rf,
        cv=5,  
        scoring="r2",  
        n_jobs=-1,  
        verbose=1
    )

    grid_search_rf.fit(X_train, y_train)

    print("Mejores hiperparámetros:", grid_search_rf.best_params_)
    print("Mejor R2 obtenido:", grid_search_rf.best_score_)

    modelo_final_rf = grid_search_rf.best_estimator_

    with open("../bin/best_score_ml.pickle", "wb") as file:
        pickle.dump(grid_search_rf.best_score_, file)

    importancias = modelo_final_rf.feature_importances_

    df_importancias = pd.DataFrame({
                    'Feature': X_train.columns,  
                    'Importance': importancias
                    })

    df_importancias = df_importancias.sort_values(by='Importance', ascending=False).reset_index(drop=True)
    df_importancias['Feature'] =  df_importancias['Feature'].map( {'potencia': 'Potencia',
                                                                    'anio_matricula': 'Año de Matrícula',
                                                                    'kilometraje':'Kilometraje',
                                                                    'marca_sola': 'Marca',
                                                                    'cambio_automatico': 'Cambio Automático'})

    df_importancias.to_pickle("../bin/feature_importance.pickle")

    with open("../bin/mejor_modelo.pickle", "wb") as archivo:
        pickle.dump(grid_search_rf.best_estimator_, archivo)

    return