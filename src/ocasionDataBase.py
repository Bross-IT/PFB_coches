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
        self.connection = mysql.connector.connect(**self.config)

    def close(self) -> None:
        self.connection.close()

    def get_max_fecha_extraccion(self) -> str|None:
        query = "SELECT MAX(fecha_extraccion) FROM coches_en_venta;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result[0] else None

    def get_concesionario_count(self) -> int:
        query = "SELECT COUNT(*) FROM concesionario;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0]

    def insert_or_get_id(self, table, column, value):
        with self.connection.cursor(buffered=True) as cursor:
            campo_id = "modelo" if table == "modelo_titulo" else table
            query_select = f"SELECT {campo_id}_id FROM {table} WHERE {column} = %s LIMIT 1;"
            cursor.execute(query_select, (value,))
            result = cursor.fetchone()
            
            if result:
                return result[0]

            query_insert = f"INSERT INTO {table} ({column}) VALUES (%s);"
            cursor.execute(query_insert, (value,))
            self.connection.commit()

            cursor.execute(query_select, (value,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_provincia_id(self, nombre_provincia):
        query = "SELECT provincia_id FROM provincia WHERE nombre_provincia = %s;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (nombre_provincia,))
            result = cursor.fetchone()
            return result[0] if result else None

    def insert_modelo_titulo(self, marca_id, nombre_modelo):
        query_select = "SELECT modelo_id FROM modelo_titulo WHERE nombre_modelo = %s AND marca_id = %s;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query_select, (nombre_modelo, marca_id))
            result = cursor.fetchone()
        
            if result:
                return result[0]
            
            query = "INSERT INTO modelo_titulo (marca_id, nombre_modelo) VALUES (%s, %s)"
            cursor.execute(query, (marca_id, nombre_modelo))
            self.connection.commit()
            
            cursor.execute(query_select, (nombre_modelo, marca_id))
            result = cursor.fetchone()
            return result[0] if result else None

    def insert_url(self, url):
        query_select = "SELECT url_id FROM urls WHERE url = %s;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query_select, (url,))
            result = cursor.fetchone()
            
            if result:
                return result[0]

            query = "INSERT INTO urls (url) VALUES (%s)"
            cursor.execute(query, (url,))
            self.connection.commit()
            
            cursor.execute(query_select, (url,))
            result = cursor.fetchone()
            return result[0] if result else None

    def insert_ruta_imagen(self, ruta_imagen):
        query_select = "SELECT ruta_imagen_id FROM ruta_imagen WHERE ruta_imagen = %s;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query_select, (ruta_imagen,))
            result = cursor.fetchone()
        
            if result:
                return result[0]
            
            query = "INSERT INTO ruta_imagen (ruta_imagen) VALUES (%s)"
            cursor.execute(query, (ruta_imagen,))
            self.connection.commit()
        
            cursor.execute(query_select, (ruta_imagen,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_concesionario_id(self, nombre_concesionario):
        query = "SELECT concesionario_id FROM concesionario WHERE nombre_concesionario = %s;"
        with self.connection.cursor(buffered=True) as cursor:
            cursor.execute(query, (nombre_concesionario.strip(),))
            result = cursor.fetchone()
            return result[0] if result else None

    def process_datos_concesionarios(self, df: pd.DataFrame) -> None:
        query = """
        INSERT INTO concesionario (nombre_concesionario, calle, provincia_id, codigo_postal, municipio_id)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE nombre_concesionario = VALUES(nombre_concesionario);"""    
        
        with self.connection.cursor(buffered=True) as cursor:
            for _, row in df.iterrows():
                provincia_id = None
                municipio_id = None
                if pd.notna(row["provincia"]) and row["provincia"] != "":
                    provincia_id = self.insert_or_get_id("provincia", "nombre_provincia", row["provincia"])
                if pd.notna(row["municipio"]) and row["municipio"] != "":
                    municipio_id = self.insert_or_get_id("municipio", "nombre_municipio", row["municipio"])
                
                cursor.execute(query, (
                    row["nombre"],
                    row["calle"] if pd.notna(row["calle"]) else None,
                    provincia_id,
                    int(row["codigo_postal"]) if pd.notna(row["codigo_postal"]) else None,
                    municipio_id
                ))
                self.connection.commit()

    def process_datos_coches(self, df: pd.DataFrame) -> None:
        anio_actual = datetime.now().year
        
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
                if concesionario_id is None:
                    print(f"Concesionario: {row['nombre_vendedor'].strip()} - referencia: {row['referencia']}")

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
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()

            if not row["vendedor_profesional"] and pd.notna(row['nombre_vendedor']):
                query = """
                INSERT INTO vendedor_particular (nombre_vendedor_particular, provincia_id, referencia)
                VALUES (%s, %s, %s)
                """
                provincia_id = self.get_provincia_id(row["provincia"])
                cursor.execute(query, (row["nombre_vendedor"].strip(), provincia_id, row["referencia"]))
                self.connection.commit()
            
            cursor.close()

    def obtener_marcas(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_marca FROM marca ORDER BY nombre_marca ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            marcas: list[dict] = cursor.fetchall()

        return marcas
        
    def obtener_modelos(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_modelo_titulo FROM modelo_titulo ORDER BY nombre_modelo_titulo ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            modelos: list[dict] = cursor.fetchall()

        return modelos

    def obtener_combustibles(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_combustible FROM combustible ORDER BY nombre_combustible ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            combustibles: list[dict] = cursor.fetchall()

        return combustibles
    
    def obtener_distintivos(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_distintivo FROM distintivo_ambiental ORDER BY nombre_distintivo ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            distintivos: list[dict] = cursor.fetchall()

        return distintivos
    
    def obtener_colores(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_color FROM color ORDER BY nombre_color ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            colores: list[dict] = cursor.fetchall()
            
        return colores
    
    def obtener_carrocerias(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_carroceria FROM carroceria ORDER BY nombre_carroceria ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            carrocerias: list[dict] = cursor.fetchall()
        
        return carrocerias

    def obtener_comunidades(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_comunidad FROM comunidad_autonoma ORDER BY nombre_comunidad ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            comunidades: list[dict] = cursor.fetchall()
        
        return comunidades
        
    def obtener_provincias(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_provincia FROM provincia ORDER BY nombre_provincia ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            provincias: list[dict] = cursor.fetchall()
            cursor.close()
        
        return provincias
    
    def obtener_municipios(self) -> list[dict]:
        query = "SELECT DISTINCT nombre_municipio FROM municipio ORDER BY nombre_municipio ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)   
            municipios: list[dict] = cursor.fetchall() 
         
        return municipios
    
    def obtener_particulares(self) -> list[dict]:
        query = "SELECT vendedor_particular_id, nombre_particular, (SELECT nombre_provincia FROM provincia WHERE provincia.provincia_id = vendedor_particular.provincia_id) as nombre_provincia FROM vendedor_particular ORDER BY nombre_particular ASC"
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            particulares: list[dict] = cursor.fetchall()
        
        return particulares
        
    def obtener_coches_venta(self) -> list[dict]:
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
                (SELECT nombre_modelo FROM modelo_titulo WHERE modelo_titulo.modelo_id = coches_en_venta.modelo_id) as modelo_titulo,
                antiguedad,
                precio,
                mes_matricula,
                anio_matricula,
                (SELECT nombre_concesionario FROM concesionario WHERE concesionario.concesionario_id = coches_en_venta.concesionario_id) as concesionario,
                (SELECT url FROM urls WHERE urls.url_id = coches_en_venta.url_id) as url,
                (SELECT ruta_imagen FROM ruta_imagen WHERE ruta_imagen.ruta_imagen_id = coches_en_venta.ruta_imagen_id) as ruta_imagen
            FROM coches_en_venta
            ORDER BY referencia ASC;
        """
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            coches_venta: list[dict] = cursor.fetchall()
            
        return coches_venta
    
    def obtener_concesionarios(self) -> list[dict]:
        query = """
            SELECT concesionario_id, 
                nombre_concesionario as nombre, 
                calle, 
                (SELECT nombre_municipio FROM municipio WHERE municipio.municipio_id = concesionario.municipio_id) as municipio,
                (SELECT nombre_provincia FROM provincia WHERE provincia.provincia_id = concesionario.provincia_id) as provincia,
                codigo_postal
            FROM concesionario
            ORDER BY nombre_concesionario ASC;
        """
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            concesionarios: list[dict] = cursor.fetchall()
        
        return concesionarios
        
    def obtener_referencias(self) -> list[str]:
        query = "SELECT referencia FROM coches_en_venta;"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            referencias: list[str] = [ f"ref{row[0]}" for row in result ]

        return referencias

    def obtener_nombres_concesionarios(self) -> list[str]:
        query = "SELECT nombre_concesionario FROM concesionario;"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            nombres_concesionarios: list[str] = [ row[0] for row in result ]
        
        return nombres_concesionarios

