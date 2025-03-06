from extraction.seleniumScraper import SeleniumScraper

import numpy as np
import pandas as pd

from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
import os
import pathlib

import time
import datetime
import random

#https://www.autocasion.com/coches-ocasion?direction=desc&sort=updated_at&page=1
script_dir = pathlib.Path(__file__).resolve().parent

# Sustituir por obtener ref de BBDD
df = pd.read_csv(f"{script_dir}/../data/coches_consolidado_limpio.csv")
referencias_guardadas: list[str] = df["referencia"].tolist()

try:
    selenium_scraper = SeleniumScraper()
    selenium_scraper.open_url("https://www.autocasion.com/coches-ocasion?direction=desc&page=1&sort=updated_at")
    selenium_scraper.find_element(by = By.CSS_SELECTOR, value = "#didomi-notice-disagree-button").click()

    nombre_caracteristicas: list[str] = ["marca", "anio", "localizacion", "kilometraje", "combustible", "distintivo_ambiental", "garantia", "cambio", "carroceria", "plazas",
                                        "potencia", "puertas", "color", "precio", "vendedor", "consumo_medio", "certificado", "fecha_extraccion", "referencia", "url", "ruta_imagen"]
    total_extraidos : int = 0
    actual_pag: int = 1
    total_pags: int = int(selenium_scraper.get_text(by = By.XPATH, value = "//a[@class='total_pages']"))

    while actual_pag != total_pags:
        selenium_scraper.script_scroll(100)
        actual_pag = int(selenium_scraper.get_current_page(selenium_scraper.current_url()))
        with open(f"{script_dir}/../data/last-page-coches.txt", "w") as file:
            file.write(str(f"{actual_pag}\n{selenium_scraper.current_url()}"))
        print("actual page ... " + str(actual_pag))
        articles = selenium_scraper.find_elements(by = By.XPATH, value = "//article[contains(@class, 'anuncio')]")
        time.sleep(3)

        urls_coches: list[str] = [ article.find_element(by = By.TAG_NAME, value = "a").get_attribute("href") for article in articles ]
        urls_coches = [ url for url in urls_coches if url.split("-")[-1] not in referencias_guardadas]
        data_coches: np.array = []  

        for url in urls_coches:
            selenium_scraper.script_scroll(200)
            selenium_scraper.open_url(url)

            caracteristicas_coche: np.array = selenium_scraper.get_features_cars()
            data_coches.append(caracteristicas_coche)
            referencias_guardadas.append(url.split("-")[-1])
            selenium_scraper.script_scroll(-250)
            selenium_scraper.back()
            time.sleep(3)
        
        df_pag: pd.DataFrame = pd.DataFrame(data_coches, columns = nombre_caracteristicas)

        total_extraidos += len(df_pag)
        data_coches.clear()

        ruta_archivo: str = f"{script_dir}/../data/coches_segunda_mano-{datetime.datetime.now().strftime("%d-%m-%Y")}.csv"
        primer_guardado: bool = not os.path.exists(ruta_archivo)
        df_pag.to_csv(ruta_archivo, mode= "w" if primer_guardado else "a", header= primer_guardado, index = False)
        
        time.sleep(random.randint(10, 25))
        selenium_scraper.find_element(by = By.XPATH, value = "//a[@class='last']").click()
except Exception as e:
    with open(f"{script_dir}/../data/errores.txt", "a") as file:
        file.write(str(f"{datetime.datetime.now().strftime("%d-%m-%Y")}|{selenium_scraper.find_element(by = By.XPATH, value = "//a[@class='last']")}| - {selenium_scraper.current_url()} \n {e}\n"))
    print(f"exception: {e}")

finally:
    selenium_scraper.close()