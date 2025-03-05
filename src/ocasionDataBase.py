import mysql.connector
import toml

def load_config(config_path):
    config = toml.load(config_path)
    db_config = config.get("database", {})
    return db_config
class OcasionDataBase:
    def __init__(self, config: dict) -> None:
        self.config = config

    def connect(self):
        return mysql.connector.connect(**self.config)

    def obtener_marcas(self) -> dict:
        query = "SELECT DISTINCT nombre_marca FROM marca ORDER BY nombre_marca ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        
        return self.cursor.fetchall()
        
    # pensar si devolver solo modelo_titulo o marca+modelo_titulo
    def obtener_modelos(self) -> dict:
        query = "SELECT DISTINCT nombre_modelo_titulo FROM modelo_titulo ORDER BY nombre_modelo_titulo ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()

    def obtener_combustibles(self) -> dict:
        query = "SELECT DISTINCT nombre_combustible FROM combustible ORDER BY nombre_combustible ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    def obtener_distintivos(self) -> dict:
        query = "SELECT DISTINCT nombre_distintivo FROM distintivo_ambiental ORDER BY nombre_distintivo ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    def obtener_colores(self) -> dict:
        query = "SELECT DISTINCT nombre_color FROM color ORDER BY nombre_color ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    def obtener_carrocerias(self) -> dict:
        query = "SELECT DISTINCT nombre_carroceria FROM carroceria ORDER BY nombre_carroceria ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()

    def obtener_comunidades(self) -> dict:
        query = "SELECT DISTINCT nombre_comunidad FROM comunidad_autonoma ORDER BY nombre_comunidad ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        
    def obtener_provincias(self) -> dict:
        query = "SELECT DISTINCT nombre_provincia FROM provincia ORDER BY nombre_provincia ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    def obtener_municipios(self) -> dict:
        query = "SELECT DISTINCT nombre_municipio FROM municipio ORDER BY nombre_municipio ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)    
            return cursor.fetchall()
    
    def obtener_particulares(self) -> dict:
        query = "SELECT vendedor_particular_id, nombre_particular, (SELECT nombre_provincia FROM provincia WHERE provincia.provincia_id = vendedor_particular.provincia_id) as nombre_provincia FROM vendedor_particular ORDER BY nombre_particular ASC"
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
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
            ORDER BY referencia ASC
        """
        with self.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        
    def obtener_referencias(self) -> list[str]:
        query = "SELECT referencia FROM coches_en_venta ORDER BY referencia ASC"
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            referencias: list[str] = [f"ref{row[0]}" for row in cursor.fetchall()]
            return referencias


