import pandas as pd
import numpy as np
from datetime import datetime

def limpiar_csv(ruta_archivo_csv):
    """
    Limpia los datos en bruto extraídos de la web autocasion y guarda un csv con el df resultante.
    
    Parameters:
    ruta_archivo_csv: ruta del archivo generado por función scraper
    
    Returns:
    pd.DataFrame: el df limpio
    """
    df = pd.read_csv(ruta_archivo_csv)

    # Extraer marca sola
    df['marca_sola'] = df['marca'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)

    # Dejar modelo
    df.rename(columns={'marca': 'modelo_titulo'}, inplace=True)
    df['modelo_titulo'] = df['modelo_titulo'].apply(lambda x: ' '.join(x.split()[1:]) if isinstance(x, str) else x)

    # fecha de matriculación
    df[['mes_matricula', 'anio_matricula']] = df['anio'].str.split('/', expand=True)
    df['mes_matricula'] = df['mes_matricula'].astype(int)
    df['anio_matricula'] = df['anio_matricula'].astype(int)
    df.drop(columns=["anio"], inplace=True)

    # kilometraje
    df["kilometraje"] = df["kilometraje"].apply(lambda x: x.replace(".","").replace(" km","") if isinstance(x, str) else np.nan)
    
    # garantía
    df["garantia"] = df["garantia"].replace("No", 0)
    df["garantia"] = df["garantia"].replace("Sí", np.nan)
    df["garantia"] = pd.to_numeric(df["garantia"].str.replace(" meses", ""), errors='coerce')
    media_garantia = pd.to_numeric(round(df["garantia"].mean(), 0))
    df['garantia'] = df["garantia"].fillna(media_garantia)

    # referencia
    df['referencia'] = pd.to_numeric(df['referencia'].str.replace('ref', ''), errors='coerce')

    # tipo_vendedor
    df["nombre_vendedor_profesional"] = pd.Series(dtype="string")
    mask = df['vendedor'].str.endswith('\nProfesional')
    df.loc[mask, 'nombre_vendedor_profesional'] = df.loc[mask, 'vendedor'].str.split('\nProfesional').str[0]
    df['vendedor'] = df['vendedor'].apply(lambda x: True if '\nProfesional' in x else False)
    df.rename(columns={'vendedor':'vendedor_profesional'}, inplace=True)
    df['vendedor_profesional'].astype(bool)

    # color
    df['color']=df['color'].apply(lambda x: x.upper())
    # Traducir al español los colores en inglés y alemán
    # "plateado" va al saco de grises
    df.loc[df["color"].str.contains("BLACK|SCHWARZ", regex=True), "color"] = "NEGRO"
    df.loc[df["color"].str.contains("WHITE|WEISS", regex=True), "color"] = "BLANCO"
    df.loc[df["color"].str.contains("RED|ROT", regex=True), "color"] = "ROJO"
    df.loc[df["color"].str.contains("BLUE|BLAU", regex=True), "color"] = "AZUL"
    df.loc[df["color"].str.contains("GRAY|GREY|GRAU|PLATEADO|SILVER", regex=True), "color"] = "GRIS"
    df['color'] = df['color'].str.split().str[0]
    colores = ["NEGRO", "BLANCO", "AZUL", "ROJO", "GRIS"]
    df['color'] = df['color'].apply(lambda x: x if x in colores else 'OTROS')

    # carrocería
    df["carroceria"] = df["carroceria"].replace("Berlina mediana o grande", "Berlina")
    df["carroceria"] = df["carroceria"].replace("Stationwagon", "Familiar")

    # plazas
    df["plazas"] = pd.to_numeric(df["plazas"].str.replace(" asientos", ""), errors='coerce')

    # puertas
    df["puertas"] = pd.to_numeric(df["puertas"].str.replace(" Puertas", ""), errors='coerce')

    # consumo_medio
    df['consumo_medio'] = df['consumo_medio'].replace([r'.*medio\n0,00\nlitros.*', r'.*medio\nlitros.*'], np.nan, regex=True)
    df['consumo_medio'] = df['consumo_medio'].str.extract(r'medio\n(.*?)\nlitros')[0]
    df['consumo_medio'] = df['consumo_medio'].str.replace(',', '.').astype(float).round(2)

    # precio
    df['precio'] = df['precio'].str.replace('.', '').str.replace(' €', '')
    df['precio'] = df['precio'].str.split('\n').str[0]
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce')

    # potencia
    df['potencia'] = df['potencia'].str.replace(' cv', '')
    df['potencia'] = pd.to_numeric(df['potencia'], errors='coerce')

    # crear campo peninsula_baleares
    fuera_de_peninsula_baleares = ["Tenerife", "Las Palmas", "Ceuta", "Melilla"]
    df['peninsula_y_baleares'] = True
    df.loc[df['localizacion'].isin(fuera_de_peninsula_baleares), 'peninsula_y_baleares'] = False

    # certificado
    df["certificado"] = df["certificado"].replace("No", False)
    df["certificado"] = df["certificado"].replace("Sí", True)
    df["certificado"] = df["certificado"].astype(bool)

    # fecha_extraccion
    df['fecha_extraccion'] = pd.to_datetime(df['fecha_extraccion'])

    # cambio
    df.rename(columns={'cambio': 'cambio_automatico'}, inplace=True)
    df['cambio_automatico'] = df['cambio_automatico'].apply(lambda x: True if x == 'Automático' else False)

    # combustible
    df["combustible"] = df["combustible"].replace("Diesel", "Diésel")
    df["combustible"] = df["combustible"].replace("Gasolina y corriente eléctrica", "Híbrido")
    df["combustible"] = df["combustible"].replace("Corriente eléctrica", "Eléctrico")

    # guardar df limpio en nuevo csv
    ruta_archivo_limpio = ruta_archivo_csv.replace(".csv", "_limpio.csv")
    df.to_csv(ruta_archivo_limpio, index=False)

    return df