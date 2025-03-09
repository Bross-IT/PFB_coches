import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import toml

def load_config(config_path: str, env: str = "database_admin") -> dict:
    config: dict = toml.load(config_path)
    db_config: dict = config.get(env, {})
    return db_config
class OcasionDataBase:
    def __init__(self, config: dict) -> None:
        self.config = config

    def connect(self):
        return mysql.connector.connect(**self.config)

    def get_max_fecha_extraccion(self) -> str|None:
        query = "SELECT MAX(fecha_extraccion) FROM coches_en_venta;"
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result[0] else None

    def get_concesionario_count(self) -> int:
        query = "SELECT COUNT(*) FROM concesionario;"
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_or_get_id(self, table, column, value):
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            
            campo_id = "modelo" if table == "modelo_titulo" else table
            query_select = f"SELECT {campo_id}_id FROM {table} WHERE {column} = %s LIMIT 1;"
            cursor.execute(query_select, (value,))
            result = cursor.fetchone()
            
            if result:
                cursor.close()
                return result[0]

            query_insert = f"INSERT INTO {table} ({column}) VALUES (%s);"
            cursor.execute(query_insert, (value,))
            connection.commit()

            cursor.execute(query_select, (value,))
            result = cursor.fetchone()

            cursor.close()
            return result[0] if result else None
    
    def insert_modelo_titulo(self, marca_id, nombre_modelo):
        query = """
        INSERT IGNORE INTO modelo_titulo (marca_id, nombre_modelo) VALUES (%s, %s);
        """
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            print(f"insert_modelo_titulo {marca_id} {nombre_modelo}")
            cursor.execute(query, (marca_id, nombre_modelo))
            connection.commit()
            query_select = "SELECT modelo_id FROM modelo_titulo WHERE nombre_modelo = %s AND marca_id = %s;"
            cursor.execute(query_select, (nombre_modelo, marca_id))
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_url(self, url):
        query = """
        INSERT INTO urls (url)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE url = VALUES(url);"""
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query, (url,))
            query_select = "SELECT url_id FROM urls WHERE url = %s;"
            cursor.execute(query_select, (url,))
            result = cursor.fetchone()
            connection.commit()
            cursor.close()
            return result[0]

    def insert_ruta_imagen(self, ruta_imagen):
        query = """
        INSERT INTO ruta_imagen (ruta_imagen)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE ruta_imagen = VALUES(ruta_imagen);"""
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query, (ruta_imagen,))
            query_select = "SELECT ruta_imagen_id FROM ruta_imagen WHERE ruta_imagen = %s;"
            cursor.execute(query_select, (ruta_imagen,))
            result = cursor.fetchone()
            connection.commit()
            return result[0]

    def get_concesionario_id(self, nombre_concesionario):
        query = "SELECT concesionario_id FROM concesionario WHERE nombre_concesionario = %s;"
        with self.connect() as connection:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query, (nombre_concesionario,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None

    def process_csv_concesionarios(self, file_path):
        df = pd.read_csv(file_path)
        if len(df) > self.get_concesionario_count():
            query = """
            INSERT INTO concesionario (nombre_concesionario, calle, provincia_id, codigo_postal, municipio_id)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre_concesionario = VALUES(nombre_concesionario);"""    
            
            with self.connect() as connection:
                for _, row in df.iterrows():
                    provincia_id = None
                    municipio_id = None
                    if pd.notna(row["provincia"]) and row["provincia"] != "":
                        provincia_id = self.insert_or_get_id("provincia", "nombre_provincia", row["provincia"])
                    if pd.notna(row["municipio"]) and row["municipio"] != "":
                        municipio_id = self.insert_or_get_id("municipio", "nombre_municipio", row["municipio"])

                    cursor = connection.cursor(buffered=True)
                    cursor.execute(query, (
                        row["nombre"],
                        row["calle"] if pd.notna(row["calle"]) else None,
                        provincia_id,
                        int(row["codigo_postal"]) if pd.notna(row["codigo_postal"]) else None,
                        municipio_id
                    ))
                    connection.commit()
                    cursor.close()

    def process_csv_coches(self, file_path):
        df = pd.read_csv(file_path, parse_dates=["fecha_extraccion"], dtype={
            "puertas": "Int64", "mes_matricula": "Int64", "anio_matricula": "Int64"
        })
        max_fecha = self.get_max_fecha_extraccion()
        df = df[df["fecha_extraccion"] >= max_fecha] if max_fecha else df
        anio_actual = datetime.now().year
        mes_actual = datetime.now().month
        with self.connect() as connection:
            for _, row in df.iterrows():
                if row["combustible"] != "" and pd.notna(row["combustible"]):
                    combustible_id = self.insert_or_get_id("combustible", "nombre_combustible", row["combustible"])
                else:
                    combustible_id = None
                marca_id = self.insert_or_get_id("marca", "nombre_marca", row["marca_sola"])
                modelo_id = self.insert_modelo_titulo(marca_id, row["modelo_titulo"])
                color_id = self.insert_or_get_id("color", "nombre_color", row["color"])
                if row["carroceria"] != "" and pd.notna(row["carroceria"]):
                    carroceria_id = self.insert_or_get_id("carroceria", "nombre_carroceria", row["carroceria"])
                else:
                    carroceria_id = None
                if row["distintivo_ambiental"] != "" and pd.notna(row["distintivo_ambiental"]):
                    distintivo_ambiental_id = self.insert_or_get_id("distintivo_ambiental", "nombre_distintivo", row["distintivo_ambiental"])
                else:
                    distintivo_ambiental_id = None
                url_id = self.insert_url(row["url"])
                if row["ruta_imagen"] != "" and pd.notna(row["ruta_imagen"]):
                    ruta_imagen_id = self.insert_ruta_imagen(row["ruta_imagen"])
                else:
                    ruta_imagen_id = None
                concesionario_id = None
                if row["vendedor_profesional"]:
                    concesionario_id = self.get_concesionario_id(row["nombre_vendedor"])
                
                data = {
                    "referencia": row["referencia"],
                    "peninsula_baleares": int(row["peninsula_y_baleares"]) if pd.notna(row["peninsula_y_baleares"]) else None,
                    "combustible_id": combustible_id,
                    "potencia": row["potencia"] if pd.notna(row["potencia"]) else None,
                    "cambio_automatico": int(row["cambio_automatico"]) if pd.notna(row["cambio_automatico"]) else None,
                    "carroceria_id": carroceria_id,
                    "kilometraje": row["kilometraje"] if pd.notna(row["kilometraje"]) else None,
                    "distintivo_ambiental_id": distintivo_ambiental_id,
                    "color_id": color_id,
                    "garantia": row["garantia"] if pd.notna(row["garantia"]) else None,
                    "vendedor_profesional": int(row["vendedor_profesional"]) if pd.notna(row["vendedor_profesional"]) else None,
                    "plazas": row["plazas"] if pd.notna(row["plazas"]) else None,
                    "puertas": row["puertas"] if pd.notna(row["puertas"]) else None,
                    "certificado": int(row["certificado"]) if pd.notna(row["certificado"]) else None,
                    "fecha_extraccion": row["fecha_extraccion"].strftime('%Y-%m-%d %H:%M:%S'),
                    "consumo": row["consumo_medio"] if pd.notna(row["consumo_medio"]) else None,
                    "modelo_id": modelo_id,
                    "antiguedad": anio_actual - row["anio_matricula"] if pd.notna(row["anio_matricula"]) else None,
                    "precio": row["precio"] if pd.notna(row["precio"]) else None,
                    "mes_matricula": row["mes_matricula"] if pd.notna(row["mes_matricula"]) else None,
                    "anio_matricula": row["anio_matricula"] if pd.notna(row["anio_matricula"]) else None,
                    "concesionario_id": concesionario_id,
                    "url_id": url_id,
                    "ruta_imagen_id": ruta_imagen_id
                }

                query = f"""
                INSERT IGNORE INTO coches_en_venta ({', '.join(data.keys())})
                VALUES ({', '.join(['%s' for _ in data.keys()])})
                """
                cursor = connection.cursor(buffered=True)
                cursor.execute(query, tuple(data.values()))
                connection.commit()
                cursor.close()

    def obtener_marcas(self) -> dict:
        query = "SELECT DISTINCT nombre_marca FROM marca ORDER BY nombre_marca ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
        
    # pensar si devolver solo modelo_titulo o marca+modelo_titulo
    def obtener_modelos(self) -> dict:
        query = "SELECT DISTINCT nombre_modelo_titulo FROM modelo_titulo ORDER BY nombre_modelo_titulo ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()

    def obtener_combustibles(self) -> dict:
        query = "SELECT DISTINCT nombre_combustible FROM combustible ORDER BY nombre_combustible ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
    
    def obtener_distintivos(self) -> dict:
        query = "SELECT DISTINCT nombre_distintivo FROM distintivo_ambiental ORDER BY nombre_distintivo ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
    
    def obtener_colores(self) -> dict:
        query = "SELECT DISTINCT nombre_color FROM color ORDER BY nombre_color ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
    
    def obtener_carrocerias(self) -> dict:
        query = "SELECT DISTINCT nombre_carroceria FROM carroceria ORDER BY nombre_carroceria ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()

    def obtener_comunidades(self) -> dict:
        query = "SELECT DISTINCT nombre_comunidad FROM comunidad_autonoma ORDER BY nombre_comunidad ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
        
    def obtener_provincias(self) -> dict:
        query = "SELECT DISTINCT nombre_provincia FROM provincia ORDER BY nombre_provincia ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
    
    def obtener_municipios(self) -> dict:
        query = "SELECT DISTINCT nombre_municipio FROM municipio ORDER BY nombre_municipio ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)    
            cursor.close()
            return cursor.fetchall()
    
    def obtener_particulares(self) -> dict:
        query = "SELECT vendedor_particular_id, nombre_particular, (SELECT nombre_provincia FROM provincia WHERE provincia.provincia_id = vendedor_particular.provincia_id) as nombre_provincia FROM vendedor_particular ORDER BY nombre_particular ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
        
    def obtener_coches_venta(self) -> dict:
        query = """
            SELECT referencia,
                peninsula_baleares,
                (SELECT nombre_combustible FROM combustible WHERE combustible.combustible_id = coches_en_venta.combustible_id) as combustible,
                potencia,
                cambio_automatico,
                (SELECT nombre_carroceria FROM carroceria WHERE carroceria.carroceria_id = coches_en_venta.carroceria_id) as carroceria,
                kilometraje,
                (SELECT nombre_distintivo FROM distintivo_ambiental WHERE distintivo_ambiental.distintivo_ambiental_id = coches_en_venta.distintivo_ambiental_id) as distintivo_ambiental,
                (SELECT nombre_color FROM color WHERE color.color_id = coches_en_venta.color_id) as color,
                garantia,
                vendedor_profesional,
                plazas,
                puertas,
                certificado,
                fecha_extraccion,
                consumo,
                (SELECT nombre_modelo FROM modelo_titulo WHERE modelo_titulo.modelo_id = coches_en_venta.modelo_id) as modelo,
                antiguedad,
                precio,
                mes_matricula,
                anio_matricula,
                (SELECT nombre_concesionario FROM concesionario WHERE concesionario.concesionario_id = coches_en_venta.concesionario_id) as concesionario,
                (SELECT url FROM url WHERE url.url_id = coches_en_venta.url_id) as url,
                (SELECT ruta_imagen FROM ruta_imagen WHERE ruta_imagen.ruta_imagen_id = coches_en_venta.ruta_imagen_id) as ruta_imagen
            FROM coches_en_venta
            ORDER BY referencia ASC;
        """
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            cursor.close()
            return cursor.fetchall()
        
    def obtener_last_referencia(self) -> str:
        query = "SELECT referencia FROM coches_en_venta WHERE fecha_extraccion = (SELECT MAX(fecha_extraccion) FROM coches_en_venta) LIMIT 1;"
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            referencia: str = cursor.fetchone()[0]
            return referencia


