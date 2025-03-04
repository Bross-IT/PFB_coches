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

    #Eliminar duplicados
    df =  df.drop_duplicates(subset=['referencia'], keep='first')

    # Extraer marca sola
    df['marca_sola'] = df['marca'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)

    # Dejar modelo
    df.rename(columns={'marca': 'modelo_titulo'}, inplace=True)
    df['modelo_titulo'] = df['modelo_titulo'].apply(lambda x: ' '.join(x.split()[1:]) if isinstance(x, str) else x)

    # fecha de matriculación
    df[['mes_matricula', 'anio_matricula']] = df['anio'].str.split('/', expand=True)
    df['mes_matricula'] = pd.to_numeric(df['mes_matricula'], errors='coerce').fillna(0).astype(int)
    df['anio_matricula'] = pd.to_numeric(df['anio_matricula'], errors='coerce').fillna(0).astype(int)
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
    df["vendedor"] = df["vendedor"].fillna("-")  # llenar nan con "-"
    df["nombre_vendedor"] = pd.Series(dtype="string")
    mask_profesional = df["vendedor"].str.endswith("\nProfesional")
    mask_particular = df["vendedor"].str.contains("\nParticular")
    df.loc[mask_profesional, "nombre_vendedor"] = df.loc[mask_profesional, "vendedor"].str.split("\nProfesional").str[0]
    df.loc[mask_particular, "nombre_vendedor"] = df.loc[mask_particular, "vendedor"].str.split("\nParticular").str[0]
    df["vendedor"] = df["vendedor"].apply(lambda x: True if "\nProfesional" in x else False)
    df.rename(columns={"vendedor": "vendedor_profesional"}, inplace=True)
    df["vendedor_profesional"] = df["vendedor_profesional"].astype(bool)

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
    df["carroceria"] = df["carroceria"].replace("Targa", "Berlina")
    df["carroceria"] = df["carroceria"].replace("Coupe", "Deportivo o coupé")
    df["carroceria"] = df["carroceria"].replace("Convertible", "Descapotable o convertible")
    df["carroceria"] = df["carroceria"].replace("Roadster", "Descapotable o convertible")
    df["carroceria"] = df["carroceria"].replace("-", "Pequeño")
    df["carroceria"] = df["carroceria"].replace("Stationwagon", "Familiar")

    # plazas
    df["plazas"] = pd.to_numeric(df["plazas"].str.replace(" asientos", ""), errors='coerce')

    # puertas
    df["puertas"] = pd.to_numeric(df["puertas"].str.replace(" Puertas", ""), errors='coerce')
 
    # Consumo medio
    sin_valor_en_regex = r"^\D*100 km$"
    df["consumo_medio"] = df["consumo_medio"].replace(sin_valor_en_regex, np.nan, regex=True)
    digitos_en_regex = r"([\d,]+,[\d]+)"
    df["consumo_medio"] = df["consumo_medio"].str.extract(digitos_en_regex)
    df["consumo_medio"] = df["consumo_medio"].str.replace(",", ".").astype(float).round(2)
    df.loc[df["consumo_medio"] == 0, "consumo_medio"] = np.nan

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
    df['cambio_automatico'] = df['cambio_automatico'] == 'Automático'

    # combustible
    df["combustible"] = df["combustible"].replace("Diesel", "Diésel")
    df["combustible"] = df["combustible"].replace("Gasolina y corriente eléctrica", "Híbrido")
    df["combustible"] = df["combustible"].replace("Corriente eléctrica", "Eléctrico")
    df["combustible"] = df["combustible"].replace("Gas", "Gasolina")
    df["combustible"] = df["combustible"].replace("Gasolina/gas", "Gasolina")
    df["combustible"] = df["combustible"].replace("Diesel y corriente eléctrica", "Híbrido")

    #rename de localizacion a provincia y creacion de columna comunidad 
    df.rename(columns={"localizacion": "provincia"}, inplace=True)
    provincias_comunidades = {
    "La Coruña": "Galicia",
    "Álava": "País Vasco",
    "Albacete": "Castilla-La Mancha",
    "Alicante": "Comunidad Valenciana",
    "Almería": "Andalucía",
    "Asturias": "Asturias",
    "Ávila": "Castilla y León",
    "Badajoz": "Extremadura",
    "Islas Baleares": "Islas Baleares",
    "Barcelona": "Cataluña",
    "Burgos": "Castilla y León",
    "Cáceres": "Extremadura",
    "Cádiz": "Andalucía",
    "Cantabria": "Cantabria",
    "Castellón": "Comunidad Valenciana",
    "Ciudad Real": "Castilla-La Mancha",
    "Córdoba": "Andalucía",
    "Cuenca": "Castilla-La Mancha",
    "Girona": "Cataluña",
    "Granada": "Andalucía",
    "Guadalajara": "Castilla-La Mancha",
    "Guipúzcoa": "País Vasco",
    "Huelva": "Andalucía",
    "Huesca": "Aragón",
    "Jaén": "Andalucía",
    "La Rioja": "La Rioja",
    "Las Palmas": "Canarias",
    "León": "Castilla y León",
    "Lleida": "Cataluña",
    "Lugo": "Galicia",
    "Madrid": "Comunidad de Madrid",
    "Málaga": "Andalucía",
    "Murcia": "Región de Murcia",
    "Navarra": "Navarra",
    "Orense": "Galicia",
    "Palencia": "Castilla y León",
    "Pontevedra": "Galicia",
    "Salamanca": "Castilla y León",
    "Tenerife": "Canarias",
    "Segovia": "Castilla y León",
    "Sevilla": "Andalucía",
    "Soria": "Castilla y León",
    "Tarragona": "Cataluña",
    "Teruel": "Aragón",
    "Toledo": "Castilla-La Mancha",
    "Valencia": "Comunidad Valenciana",
    "Valladolid": "Castilla y León",
    "Vizcaya": "País Vasco",
    "Zamora": "Castilla y León",
    "Zaragoza": "Aragón",
    "Ceuta": "Ceuta",
    "Melilla": "Melilla"
    }
    df["comunidad"] = df["provincia"].map(provincias_comunidades)

    # guardar df limpio en nuevo csv
    ruta_archivo_limpio = ruta_archivo_csv.replace(".csv", "_limpio.csv")
    df.to_csv(ruta_archivo_limpio, index=False)

    return df

def limpiar_csv_conces(ruta_csv_conces):
        """
    Limpia los datos de concesionarios en bruto extraídos de la web autocasion y guarda un csv con el df resultante.
    
    Parameters:
    ruta_csv_conces: ruta del archivo generado por función scraper
    
    Returns:
    pd.DataFrame: el df limpio
    """
        
        df_conces = pd.read_csv(ruta_csv_conces)
        df_conces["codigo_postal"] = pd.to_numeric(df_conces["codigo_postal"], errors='coerce')
        df_conces.loc[(df_conces["codigo_postal"] < 1000) | (df_conces["codigo_postal"] > 52999) | (df_conces["codigo_postal"].isna()), "codigo_postal"] = 0
        # Como es solo para consulta, si sale el código postal como 00000, se entiende que no hay.

        df_conces = df_conces.drop_duplicates(keep="first") # Saco duplicados

        #Homogeinizo muestra
        df_conces['municipio'] = df_conces['municipio'].str.replace('Á', 'A', regex=True).str.replace('É', 'E', regex=True) \
                                               .str.replace('Í', 'I', regex=True).str.replace('Ó', 'O', regex=True) \
                                               .str.replace('Ú', 'U', regex=True).str.replace('Ñ', 'N', regex=True) \
                                               .str.replace('À', 'A', regex=True).str.upper()

        df_conces['provincia'] = df_conces['provincia'].str.replace('Á', 'A', regex=True).str.replace('É', 'E', regex=True) \
                                               .str.replace('Í', 'I', regex=True).str.replace('Ó', 'O', regex=True) \
                                               .str.replace('Ú', 'U', regex=True).str.replace('Ñ', 'N', regex=True) \
                                               .str.replace('À', 'A', regex=True).str.upper()

        df_conces['municipio'] = df_conces['municipio'].str.replace(r'\s*\(.*?\)', '', regex=True) # Saco texto entre paréntesis
        #Lleno Nans de provincias con la provincia del municipio
        municipios_provincias1 = {
            'DON BENITO': 'Badajoz', 
            'MALAGA': 'Málaga',
            'ALMERIA': 'Almería',
            'NIJAR': 'Almería',
            'PLAYA DEL INGLES': 'Las Palmas',
            'ARTESA DEL SEGRE': 'Lleida',
            'VICOLOZANO': 'Ávila',
            'OROSO': 'A Coruña',
            'PONFERRADA': 'León',
            'ALTORRICON': 'Huesca',
            'ONDARA': 'Alicante',
            'GRANADA': 'Granada',
            'ESTEPONA': 'Málaga',
            'FUENTE EL SAZ DEL JARAMA': 'Madrid',
            'LEMOA': 'Bizkaia',
            'A CORUNA': 'A Coruña',
            'ARTEIXO': 'A Coruña',
            'UTRERA SEVILLA': 'Sevilla',
            'ALMORADI': 'Alicante',
            'CASTELLON': 'Castellón',
            'MARTORELLES': 'Barcelona',
            'ALGETE': 'Madrid',
            'BAZA': 'Granada',
            'ZAMORA': 'Zamora',
            'GIJON': 'Asturias',
            'BENIDORM': 'Alicante',
            'TORREVIEJA': 'Alicante',
            'CERCEDA': 'A Coruña',
            'ALCALA DE GUADAIRA': 'Sevilla',
            'MANLLEU': 'Barcelona',
            'MADRID': 'Madrid',
            'LEGANES': 'Madrid',
            'HOSPITALET LLOBREGAT': 'Barcelona',
            'TORRE DEL MAR': 'Málaga',
            'CADRETE': 'Zaragoza',
            'VALLADOLID': 'Valladolid',
            'CERDANYOLA DEL VALLES': 'Barcelona',
            'CORIA DE RIO': 'Sevilla',
            'BOADILLA DEL MONTE': 'Madrid',
            'TALAVERA DE LA REINA': 'Toledo',
            'EL CUERVO , SEVILLA': 'Sevilla',
            'CAMANZO': 'Pontevedra',
            'MOS': 'Pontevedra',
            'LA GUARDIA': 'Pontevedra',
            "LA VALL D'UIXO": 'Castellón',
            'GIRONA': 'Girona',
            'ABANTO Y CIERVANA-ABANTO ZIERBENA': 'Bizkaia',
            'ROIS': 'A Coruña',
            'CULLEREDO': 'A Coruña',
            'ZUERA': 'Zaragoza',
            'HINOJOS': 'Huelva',
            'VILLAFRANCA DE LOS BARROS': 'Badajoz',
            'TORREJON DE ARDOZ, MADRID': 'Madrid',
            'ALAQUAS': 'Valencia',
            'LIERES -': 'Asturias',
            'PULPI - ALMERIA': 'Almería',
            'IGUALADA': 'Barcelona',
            'SANT CUGAT': 'Barcelona',
            'ARGANDA DEL REY': 'Madrid',
            'OLÈRDOLA': 'Barcelona',
            'LA PUEBLA DE ALFINDEN': 'Zaragoza',
            'OLOT': 'Girona',
            'ALGUAIRE': 'Lleida',
            'VALENCIA - MONCADA': 'Valencia',
            'LUGO': 'Lugo',
            'BALMASEDA': 'Bizkaia',
            'SANTA CRUZ DE TENERIFE': 'Santa Cruz de Tenerife',
            'ORDIZIA': 'Gipuzkoa',
            'BARCELONA': 'Barcelona',
            'MANSILLA DEL ESLA': 'León',
            'BADALONA': 'Barcelona',
            'LA BARCA DE LA FLORIDA': 'Cádiz',
            'GODELLA': 'Valencia',
            'SANTA COLOMA DE GRAMANET': 'Barcelona',
            'RIVAS VACIAMADRID': 'Madrid',
            'SORIA': 'Soria',
            'ALCALA DE HENARES': 'Madrid',
            'SAN SEBASTIAN': 'Gipuzkoa',
            'PALENCIA': 'Palencia',
            'ABENGIBRE': 'Albacete',
            'CABRIANES': 'Barcelona',
            'GUARGACHO, ARONA': 'Santa Cruz de Tenerife',
            'BENAVIDES DE ORBIGO': 'León',
            'CACERES': 'Cáceres',
            'ALZIRA': 'Valencia',
            'RIBARROJA DEL TURIA': 'Valencia',
            'MORA DE RUBIELOS': 'Teruel',
            'TRAPAGARAN': 'Bizkaia',
            'BENIPARRELL': 'Valencia',
            'ALCUESCAR': 'Cáceres',
            'PERALES DE TAJUNA': 'Madrid',
            'MURCIA': 'Murcia',
            'BENALMADENA': 'Málaga',
            'CALAMONTE': 'Badajoz',
            'PALMA DE MALLORCA': 'Illes Balears',
            'MATARO': 'Barcelona',
            'RAJADELL': 'Barcelona',
            'IBARRA': 'Gipuzkoa',
            'LEON': 'León',
            'TERUEL': 'Teruel',
            'LANTEJUELA': 'Sevilla',
            'FONTETA': 'Girona',
            'MONTEMAYOR': 'Córdoba',
            'LEGAZPIA': 'Gipuzkoa',
            'GRANOLLERS': 'Barcelona',
            'LA RINCONADA': 'Sevilla',
            'ALJARAQUE': 'Huelva',
            'PARLA': 'Madrid',
            'GERNIKA': 'Bizkaia',
            'VIZCAYA': 'Bizkaia',
            'QUER': 'Guadalajara',
            'LA HOYA': 'Murcia',
            'IBIZA': 'Illes Balears',
            'GUIPUZCOA': 'Gipuzkoa',
            'ARENYS DE MAR': 'Barcelona',
            'QUINTANAR DE LA ORDEN': 'Toledo',
            'HUELVA': 'Huelva',
            'PENARROYA DE TASTAVINS': 'Teruel',
            'SANTPEDOR': 'Barcelona',
            'TOEN': 'Ourense',
            'SEGOVIA': 'Segovia',
            'ROTA': 'Cádiz',
            'MOLINA DE SEGURA': 'Murcia',
            'VILANOVA I LA GELTRU': 'Barcelona',
            'MOLINS DE REI': 'Barcelona',
            'AVINYONET DEL PENEDES': 'Barcelona',
            'JAEN': 'Jaén',
            'MARBELLA': 'Málaga',
            'LALIN': 'Pontevedra',
            'HELLIN': 'Albacete',
            'CEREZO DE ABAJO': 'Segovia',
            'CAMARENA': 'Guadalajara',
            'VILADECANS': 'Barcelona',
            'CARLET': 'Valencia',
            'CARRAL': 'A Coruña',
            'AZKOITIA': 'Gipuzkoa',
            'MEDINA DE RIOSECO': 'Valladolid',
            'DAIMIEL': 'Ciudad Real',
            'GANDIA': 'Valencia',
            'VALVERDE DEL FRESNO': 'Badajoz',
            'VALDES': 'Asturias',
            'SANTIAGO DE COMPOSTELA': 'A Coruña',
            'VIGO': 'Pontevedra',
            'VALENCIA': 'Valencia',
            'PONTEVEDRA': 'Pontevedra',
            'SANTA FE': 'Granada',
            'OLESA DE MONTSERRAT': 'Barcelona',
            'PINTO': 'Madrid',
            'LA HORMILLA': 'Madrid',
            'OURENSE': 'Ourense',
            'GAVA': 'Barcelona',
            'SANT FOST DE CAMPSENTELLES': 'Barcelona',
            'DENIA': 'Alicante',
            'PINEDA MAR': 'Barcelona',
            'TORA': 'Tarragona',
            'ELCHE': 'Alicante',
            'VALENCIA DE LAS TORRES': 'Badajoz',
            'RAVAL DE CRIST': 'Valencia',
            'ARAHAL': 'Sevilla',
            'MONGIA': 'Barcelona',
            'MUNGIA': 'Bizkaia',
            'EL PUERTO DE SANTA MARIA': 'Cádiz',
            'HUESCA': 'Huesca',
            'TROBAJO DEL CAMINO': 'León',
            'GETAFE': 'Madrid',
            "L'ESCALA": 'Girona',
            'VITORIA-GASTEIZ': 'Álava',
            'FOZ': 'Lugo',
            'FAZOURO': 'Lugo',
            'MECO': 'Madrid',
            'ALAVA': 'Álava',
            'CASTROVERDE': 'Lugo',
            'ARZUA': 'A Coruña',
            'LEZAMA': 'Bizkaia',
            'CARNOTA': 'A Coruña',
            'FUENSALDANA': 'Valladolid',
            'LA CORONADA': 'Badajoz',
            'LA CORUNA': 'A Coruña',
            'MARCHENA': 'Sevilla',
            'VILLAREZO': 'Burgos',
            'HONDARRIBI': 'Gipuzkoa',
            'TOLEDO': 'Toledo',
            'CORIA': 'Cáceres',
            'BAILEN': 'Jaén',
            'BENAVENTE': 'Zamora',
            'ZARAGOZA': 'Zaragoza',
            'ALBA DE TORMES': 'Salamanca',
            'PALMA DEL RIO': 'Córdoba',
            'LAS ROZAS DE MADRID': 'Madrid',
            'PUEBLA DEL RIO': 'Sevilla',
            'CABRERA DE MAR': 'Barcelona',
            'FUENLABRADA': 'Madrid'
        }

        df_conces['provincia'] = df_conces.apply(lambda row: municipios_provincias1.get(row['municipio'], row['provincia']), axis=1)
        
        #Segundo dict para llenar Nan de provincia con la provincia del municipio
        municipios_provincias2 = {
            'LLUCMAJOR': 'Illes Balears',
            'LAGOA, A': 'Pontevedra',
            'MARTORELL': 'Barcelona',
            'LLEIDA': 'Lleida',
            'ASTURIAS': 'Asturias',
            'ALBACETE': 'Albacete',
            'OROZKO': 'Bizkaia',
            'VILAFRANCA DEL PENEDES': 'Barcelona',
            'SARRIA DE TER': 'Girona',
            'CAN PASTILLA': 'Illes Balears',
            'IRUN': 'Gipuzkoa',
            'SUBIRATS': 'Barcelona',
            'CALDES DE MONTBUI': 'Barcelona',
            'VILLANUEVA DEL RIO Y MINAS': 'Sevilla',
            'SAN FERNANDO DE HENARES': 'Madrid',
            'PALAU-SOLITA I PLEGAMANS': 'Barcelona',
            'VILLANUEVA DE GALLEGO': 'Zaragoza',
            'CAMARENA DE LA SIERRA': 'Guadalajara',
            'AGUILAR DE CAMPOO': 'Palencia',
            'LOIU': 'Bizkaia',
            'CIUTADELLA DE MENORCA': 'Illes Balears',
            'RAFAL': 'Alicante',
            'MONTCADA I REIXAC': 'Barcelona',
            'ARONA': 'Santa Cruz de Tenerife',
            'ZALLA': 'Bizkaia',
            'CARRACEDELO': 'León',
            'RIBADESELLA': 'Asturias',
            'MADRIGUERAS': 'Albacete',
            'PALOS DE LA FRONTERA': 'Huelva',
            'BERGA': 'Barcelona',
            'CUARTE DE HUERVA': 'Zaragoza',
            'TORRELAMEU': 'Lleida',
            'PERATALLADA': 'Girona',
            'QUINTO': 'Zaragoza',
            'EL CAMPILLO': 'Huelva',
            'GALLUR': 'Zaragoza',
            'TERRASSA': 'Barcelona',
            'O BARCO': 'Ourense',
            'MORALZARZAL': 'Madrid',
            'LAGUNA DE DUERO': 'Valladolid',
            'PELABRAVO': 'Salamanca',
            'CARTAYA': 'Huelva',
            'LAS PALMAS DE GRAN CANARIA': 'Las Palmas',
            'GUADALAJARA': 'Guadalajara',
            'BECERRIL DE LA SIERRA': 'Madrid',
            'OCANA': 'Toledo',
            'ALQUERIAS DEL NINO PERDIDO': 'Castellón',
            'SEVILLA': 'Sevilla',
            'PATERNA': 'Valencia',
            'VILA-SANA MOLLERUSSA': 'Lleida',
            'BETANZOS': 'A Coruña',
            'EL ESPINAR': 'Segovia',
            'CORNELLA DE LLOBREGAT': 'Barcelona',
            'OCANA - TOLEDO': 'Toledo',
            'MILAGROS': 'Burgos',
            'VILA-REAL': 'Castellón',
            'NULES': 'Castellón',
            'SAN MIGUEL DEL CAMINO': 'Asturias',
            'O CARBALLINO': 'Ourense',
            'CORUNA': 'A Coruña',
            'O GROVE': 'Pontevedra',
            'AGUAUDLCE': 'Almería',
            'MONTIJO': 'Badajoz',
            'MONTORNES DEL VALLES': 'Barcelona',
            'TRES CANTOS': 'Madrid',
            'FENE': 'A Coruña',
            'VILLAMARTIN': 'Cádiz',
            'PAIPORTA': 'Valencia',
            'MIJAS': 'Málaga',
            'MANCHA REAL': 'Jaén',
            'AZUQUECA DE HENARES': 'Guadalajara',
            'SAN TIRSO DE ABRES': 'Asturias',
            'ALDAYA - VALENCIA': 'Valencia',
            'NORENA': 'Asturias',
            'SAN MARTIN DE LA VEGA': 'Madrid',
            'HERENCIA': 'Ciudad Real',
            'SALVATERRA DE MINO': 'Pontevedra',
            'BUSOT': 'Alicante',
            "L'AMETLLA DE MAR": 'Tarragona',
            'COIN': 'Málaga',
            'GUIJON- ASTURIAS': 'Asturias',
            'ARGAMASILLA DE CALATRAVA': 'Ciudad Real',
            'MIAJADAS': 'Cáceres',
            'TARRAGONA': 'Tarragona',
            'TERESA': 'Valencia',
            'OVIEDO': 'Asturias',
            'LES FRANQUESES DEL VALLÈS': 'Barcelona',
            'MONTMELO': 'Barcelona',
            'QUART DE POBLET': 'Valencia',
            'SAN ADRIAN LA LOSILLA': 'Navarra',
            'VEDRA': 'A Coruña',
            'MALPARTIDA DE CACERES': 'Cáceres',
            'LUCENA': 'Córdoba',
            'AIGUAVIVA': 'Girona',
            'FONDARELLA,': 'Tarragona',
            'SANFULGENCIO': 'Alicante',
            'CAMPOHERMOSO': 'Almería',
            'SERON': 'Almería',
            'CIUDAD REAL': 'Ciudad Real',
            'CARBALLO': 'A Coruña',
            'RIUDELLOTS DE LA SELVA': 'Girona',
            'ORENSE': 'Ourense',
            'SILLA': 'Valencia'
        }

        df_conces['provincia'] = df_conces.apply(lambda row: municipios_provincias2.get(row['municipio'], row['provincia']), axis=1)
        #Unifico provincias y capitalizo
        unificar_provincias = {
            'A CORUNA': 'A Coruña',
            'ALAVA': 'Álava',
            'ALBACETE': 'Albacete',
            'ALICANTE': 'Alicante',
            'ALMERIA': 'Almería',
            'ASTURIAS': 'Asturias',
            'AVILA': 'Ávila',
            'BADAJOZ': 'Badajoz',
            'BARCELONA': 'Barcelona',
            'BIZKAIA': 'Vizcaya',
            'BURGOS': 'Burgos',
            'CACERES': 'Cáceres',
            'CADIZ': 'Cádiz',
            'CANTABRIA': 'Cantabria',
            'CASTELLON': 'Castellón',
            'CEUTA': 'Ceuta',
            'CIUDAD REAL': 'Ciudad Real',
            'CORDOBA': 'Córdoba',
            'CUENCA': 'Cuenca',
            'GIPUZKOA': 'Guipúzcoa',
            'GIRONA': 'Gerona',
            'GRANADA': 'Granada',
            'GUADALAJARA': 'Guadalajara',
            'GUIPUZCOA': 'Guipúzcoa',
            'HUELVA': 'Huelva',
            'HUESCA': 'Huesca',
            'ILLES BALEARS': 'Islas Baleares',
            'ISLAS BALEARES': 'Islas Baleares',
            'JAEN': 'Jaén',
            'LA CORUNA': 'A Coruña',
            'LA RIOJA': 'La Rioja',
            'LAS PALMAS': 'Las Palmas',
            'LEON': 'León',
            'LLEIDA': 'Lérida',
            'LUGO': 'Lugo',
            'MADRID': 'Madrid',
            'MALAGA': 'Málaga',
            'MELILLA': 'Melilla',
            'MURCIA': 'Murcia',
            'NAVARRA': 'Navarra',
            'ORENSE': 'Ourense',
            'OURENSE': 'Ourense',
            'PALENCIA': 'Palencia',
            'PONTEVEDRA': 'Pontevedra',
            'SALAMANCA': 'Salamanca',
            'SANTA CRUZ DE TENERIFE': 'Santa Cruz de Tenerife',
            'SEGOVIA': 'Segovia',
            'SEVILLA': 'Sevilla',
            'SORIA': 'Soria',
            'TARRAGONA': 'Tarragona',
            'TENERIFE': 'Santa Cruz de Tenerife',
            'TERUEL': 'Teruel',
            'TOLEDO': 'Toledo',
            'VALENCIA': 'Valencia',
            'VALLADOLID': 'Valladolid',
            'VIZCAYA': 'Vizcaya',
            'ZAMORA': 'Zamora',
            'ZARAGOZA': 'Zaragoza'
        }

        df_conces['provincia'] = df_conces['provincia'].replace(unificar_provincias)
        #Asigno la capital de la provincia a municipios Nans
        capitales = {
            'Barcelona': 'Barcelona',
            'Madrid': 'Madrid',
            'Tarragona': 'Tarragona',
            'Segovia': 'Segovia',
            'Toledo': 'Toledo',
            'Sevilla': 'Sevilla',
            'Zaragoza': 'Zaragoza',
            'Murcia': 'Murcia',
            'Lérida': 'Lleida',
            'Cádiz': 'Cádiz',
            'Castellón': 'Castellón',
            'Pontevedra': 'Pontevedra',
            'Albacete': 'Albacete',
            'Valencia': 'Valencia',
            'Lugo': 'Lugo',
            'Málaga': 'Málaga',
            'Salamanca': 'Salamanca',
            'Valladolid': 'Valladolid',
            'Cantabria': 'Santander',
            'León': 'León',
            'La Rioja': 'Logroño',
            'A Coruña': 'A Coruña',
            'Burgos': 'Burgos',
            'Palencia': 'Palencia',
            'Alicante': 'Alicante',
            'Almería': 'Almería',
            'Guipúzcoa': 'San Sebastián',
            'Huesca': 'Huesca',
            'Soria': 'Soria',
            'Granada': 'Granada',
            'Gerona': 'Gerona',
            'Santa Cruz de Tenerife': 'Santa Cruz de Tenerife',
            'Las Palmas': 'Las Palmas de Gran Canaria',
            'Asturias': 'Oviedo',
            'Guadalajara': 'Guadalajara',
            'Islas Baleares': 'Palma',
            'Jaén': 'Jaén',
            'Navarra': 'Pamplona',
            'Vizcaya': 'Bilbao',
            'Córdoba': 'Córdoba',
            'Ciudad Real': 'Ciudad Real',
            'Cuenca': 'Cuenca',
            'Badajoz': 'Badajoz',
            'Álava': 'Vitoria-Gasteiz',
            'Ávila': 'Ávila'
        }

        #Capitalizo municipios
        df_conces['municipio'] = df_conces.apply(lambda row: capitales.get(row['provincia'], row['municipio']) if pd.isna(row['municipio']) else row['municipio'],axis=1)

        df_conces['municipio'] = df_conces['municipio'].str.capitalize() 
        #A nombres duplicados de diferences sucursales le agrego el municipio al que pertenecen
        duplicados = df_conces[df_conces.duplicated(subset='nombre', keep=False)]

        duplicados['nombre'] = duplicados.apply(lambda x: f"{x['nombre']} - {x['municipio']}", axis=1)

        df_conces.update(duplicados)

        ruta_archivo_limpio = ruta_csv_conces.replace(".csv", "_limpio.csv")
        df_conces.to_csv(ruta_archivo_limpio, index=False)

        return df_conces

def tratamiento_nans(ruta_csv_consolidado):
      
    df = pd.read_csv(ruta_csv_consolidado)

    def tratamiento_combustible(row, df):
        if pd.notna(row['combustible']):  
            return row['combustible']

        modelo_upper = row['modelo_titulo'].upper()

        if any(x in modelo_upper for x in ['HÍBRIDO ENCHUFABLE', 'HIBRIDO ENCHUFABLE', 'PHEV', 'E-HYBRID', 'PLUG-IN HYBRID', 'P-HEV']):
            return 'Híbrido Enchufable'
        
        if any(x in modelo_upper for x in ['ELÉCTRICO', 'ELECTRICO']):
            return 'Eléctrico'
        
        if any(x in modelo_upper for x in ['HÍBRIDO', 'HYBRID', 'HIBRIDO']):
            return 'Híbrido'
        
        if any(x in modelo_upper for x in ['DIÉSEL', 'DIESEL']):
            return 'Diésel'
        
        if any(x in modelo_upper for x in ['GASOLINA', 'TSI', 'TFSI', 'MPI', 'FSI']):
            return 'Gasolina'
        # Selecciono el primer elemento de modelo titulo (generalmente el modelo) y si es igual y no tiene nan en combustible, elijo el combustible mmoda
        primera_palabra = row['modelo_titulo'].split()[0] 
        similares = df[df['modelo_titulo'].str.contains(primera_palabra, case=False, na=False)]

        if not similares['combustible'].dropna().empty:
            return similares['combustible'].mode()[0] if not similares['combustible'].mode().empty else None
        
        return None 

    df['combustible'] = df.apply(lambda row: tratamiento_combustible(row, df), axis=1)

    def tratamiento_potencia(df):
        df['potencia'] = df['potencia'].fillna(df.groupby(['marca_sola', 'carroceria'])['potencia'].transform('mean'))
        df['potencia'] =df['potencia'].apply(lambda x: round(x,2))
        return df

        #Actualizo valores puntuales sin datos
    df.loc[df['referencia'] == 14960284, 'potencia'] = 717
    df.loc[df['referencia'] == 13860766, 'potencia'] = 570
    df.loc[df['referencia'] == 14288267, 'potencia'] = 163
    df.loc[df['referencia'] == 14436440, 'potencia'] = 211
    df.loc[df['referencia'] == 15403075, 'potencia'] = 707
    df.loc[df['referencia'] == 15497025, 'potencia'] = 163
    df.loc[df['referencia'] == 15487722, 'potencia'] = 163
    df.loc[df['referencia'] == 11748727, 'potencia'] = 401
    df = tratamiento_potencia(df)

    def segmentar_potencia(potencia):
        if potencia < 70:
            return '<70'
        elif 70 <= potencia < 110:
            return '70-110'
        elif 110 <= potencia < 150:
            return '110-150'
        elif 150 <= potencia < 200:
            return '150-200'
        elif 200 <= potencia < 300:
            return '200-300'
        elif 300 <= potencia < 450:
            return '300-450'
        elif potencia >= 450:
            return '>450'
    df['potencia_segmentado'] = df['potencia'].apply(segmentar_potencia)

    def tratamiento_consumo(df):
    
        df.loc[(df['combustible'] == 'Eléctrico'), 'consumo_medio'] = 0

        df_consumo_agg = df[df['combustible']!= 'Eléctrico'].groupby(['potencia_segmentado']).agg({'consumo_medio':'mean'})
        dict_consumo = df_consumo_agg.to_dict() 

        df['consumo_medio'] = df.apply(lambda row: dict_consumo['consumo_medio'].get(row['potencia_segmentado'], row['consumo_medio']) 
        if pd.isna(row['consumo_medio']) else row['consumo_medio'], axis=1)

        return df
        
    df = tratamiento_consumo(df)

    def tratamiento_plazas(df):
        df.loc[df['carroceria'] == '4x4, SUV o pickup', 'plazas'] = df['plazas'].fillna(5)
        df.loc[df['carroceria'] == 'Berlina', 'plazas'] = df['plazas'].fillna(5)
        df.loc[df['carroceria'] == 'Familiar', 'plazas'] = df['plazas'].fillna(5)
        df.loc[df['carroceria'] == 'Monovolumen', 'plazas'] = df['plazas'].fillna(7)
        df.loc[df['puertas'].isin([2, 3]), 'plazas'] = df['plazas'].fillna(2) 
        df.loc[df['puertas'].isin([4, 5]), 'plazas'] = df['plazas'].fillna(5) 

        return df

    df = tratamiento_plazas(df)

    def tratamiento_carroceria(row, df):
        if pd.notna(row['carroceria']):  
            return row['carroceria']

        modelo_titulo = str(row['modelo_titulo']).upper()  

        if any(word in modelo_titulo for word in ['SUV', '4X4', 'PICKUP']):
            return '4x4, SUV o pickup'

        if any(word in modelo_titulo for word in ['ALLROAD', 'TODO TERRENO']):
            return 'Todo Terreno'

        if any(word in modelo_titulo for word in ['COUPÉ', 'DEPORTIVO']):
            return 'Deportivo o coupé'
        
        if 'BERLINA' in modelo_titulo:
            return 'Berlina'
        
        if 'FAMILIAR' in modelo_titulo:
            return 'Familiar'

        if any(word in modelo_titulo for word in ['DESCAPOTABLE', 'CONVERTIBLE']):
            return 'Descapotable o Convertible'
        
        if 'MONOVOLUME' in modelo_titulo:
            return 'Monovolumen'
        
        if 'PEQUEÑO' in modelo_titulo:
            return 'Pequeño'

        primera_palabra = modelo_titulo.split()[0]  
        similares = df[df['modelo_titulo'].str.contains(primera_palabra, case=False, na=False)]

        if not similares['carroceria'].dropna().empty:
            return similares['carroceria'].mode()[0] if not similares['carroceria'].mode().empty else None  

        return None  
    
    df['carroceria'] = df.apply(lambda row: tratamiento_carroceria(row, df), axis=1)

    def tratamiento_distintivo_ambiental(row, df):
        if pd.notna(row['distintivo_ambiental']):  
            return row['distintivo_ambiental']
        
        combustible = str(row['combustible']).upper() if pd.notna(row['combustible']) else None  

        if combustible is None:
            return None  

        if 'ELÉCTRICO' in combustible:
            return '0 EMISIONES'
        if 'HÍBRIDO' in combustible:
            return 'ECO'
        if 'DIÉSEL' in combustible:
            return 'B'
        if 'GASOLINA' in combustible:
            return 'C'

        return None  

    df['distintivo_ambiental'] = df.apply(lambda row: tratamiento_distintivo_ambiental(row, df), axis=1)

    # guardar df limpio en nuevo csv
    ruta_archivo_limpio = ruta_csv_consolidado.replace(".csv", "_limpio.csv")
    df.to_csv(ruta_archivo_limpio, index=False)

    return df
