from extraction.seleniumScraper import SeleniumScraper

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse, parse_qs

import numpy as np
import pandas as pd

import time
import pathlib
from pathlib import Path

import time
import datetime
import random

def contiene(lista: list[str], cadena: str) -> str:
    elemento = next((elemento for elemento in lista if str.lower(cadena) in str.lower(elemento)), '')
    return elemento.split(':')[1].strip() if elemento != '' else elemento

#"https://www.autocasion.com/concesionarios?order=nombre-a-z"
def scraper_concesionario(url_page: str, num_extraer: int = None) -> None:
    script_dir = pathlib.Path(__file__).resolve().parent
    dict_concesionario: dict[str, np.array] = {
        "nombre": np.array([]),
        "calle": np.array([]),
        "municipio": np.array([]),
        "provincia": np.array([]),
        "codigo_postal": np.array([]),
    }
    extraidos: int = 0
    try:
        
        selenium_scraper = SeleniumScraper()
        selenium_scraper.open_url(url_page)
        selenium_scraper.find_element(by = By.CSS_SELECTOR, value = "#didomi-notice-disagree-button").click()

        next_pag = True
        while next_pag is not None and (num_extraer is None or extraidos <= num_extraer):
            actual_url = selenium_scraper.current_url()
            actual_pag = int(selenium_scraper.get_current_page(actual_url))

            print("actual page " + str(actual_pag) + " ...")
            time.sleep(1)
            li_concesionarios = selenium_scraper.find_elements(by = By.XPATH, value = "//ul[contains(@class, 'listado-concesionarios')]//li")
            selenium_scraper.script_scroll(180)
            for concesionario in li_concesionarios:
                lista_info: list[str] = concesionario.find_element(by = By.XPATH, value = ".//a").text.split("\n")
                dict_concesionario["nombre"] = np.append(dict_concesionario["nombre"], lista_info[0])

                dict_concesionario["calle"] = np.append(dict_concesionario["calle"], contiene(lista_info, "Calle:"))
                dict_concesionario["municipio"] = np.append(dict_concesionario["municipio"], contiene(lista_info, "Municipio:"))
                dict_concesionario["provincia"] = np.append(dict_concesionario["provincia"], contiene(lista_info, "Provincia:"))
                dict_concesionario["codigo_postal"] = np.append(dict_concesionario["codigo_postal"], contiene(lista_info, "Código postal:"))
                extraidos += 1

                if extraidos == num_extraer:
                    next_pag = None
                    break
            if next_pag is None:
                break
            try:
                if "disabled" in selenium_scraper.get_attribute(by = By.XPATH, value = "//span[contains(@class, 'icon-arrow-right')]", attribute = "class"):
                    next_pag = None
                else:
                    next_pag = selenium_scraper.find_element(by= By.XPATH, value= "//span[contains(@class, 'icon-arrow-right')]//ancestor::li")
                    next_pag.click()
            except NoSuchElementException as nse:
                next_pag = None

        time.sleep(1)
    except Exception as e:
        print(e)
    finally:
        selenium_scraper.close()
        ruta_archivo: str = f"{script_dir}/../../data/concesionarios.csv"
        df_concesionario = pd.DataFrame(dict_concesionario)
        df_concesionario.to_csv(ruta_archivo, mode= "w", index = False)

#"https://www.autocasion.com/coches-ocasion?direction=desc&page=1&sort=updated_at"
def scraper_coches(url_page: str, num_extraer: int = None) -> None:
    CURRENT_DIR = pathlib.Path(__file__).resolve().parent
    DAILY_CARS_PATH = Path(f"{CURRENT_DIR}/../../data/coches_segunda_mano-{datetime.datetime.now().strftime('%d-%m-%Y')}.csv")

    referencias_guardadas: list[str] = []
    primer_guardado: bool = True
    if DAILY_CARS_PATH.exists():
        primer_guardado = False	
        df = pd.read_csv(DAILY_CARS_PATH)
        referencias_guardadas = df["referencia"].tolist()

    try:
        selenium_scraper = SeleniumScraper()
        selenium_scraper.open_url(url_page)
        selenium_scraper.find_element(by = By.CSS_SELECTOR, value = "#didomi-notice-disagree-button").click()

        nombre_caracteristicas: list[str] = ["marca", "anio", "localizacion", "kilometraje", "combustible", "distintivo_ambiental", "garantia", "cambio", "carroceria", "plazas",
                                            "potencia", "puertas", "color", "precio", "vendedor", "consumo_medio", "certificado", "fecha_extraccion", "referencia", "url", "ruta_imagen"]
        total_extraidos : int = 0
        actual_pag: int = 1
        total_pags: int = int(selenium_scraper.get_text(by = By.XPATH, value = "//a[@class='total_pages']"))

        while (num_extraer is None or total_extraidos <= num_extraer) and actual_pag != total_pags:
            selenium_scraper.script_scroll(100)
            actual_pag = int(selenium_scraper.get_current_page(selenium_scraper.current_url()))
            with open(f"{CURRENT_DIR}/../../data/last-page-coches.txt", "w") as file:
                file.write(str(f"{actual_pag}\n{selenium_scraper.current_url()}"))
            print(f"actual page ... {actual_pag} - datos extraidos: {total_extraidos}")
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
                total_extraidos += 1
                if total_extraidos == num_extraer:
                    break
                selenium_scraper.script_scroll(-250)
                selenium_scraper.back()
                time.sleep(3)
            
            df_pag: pd.DataFrame = pd.DataFrame(data_coches, columns = nombre_caracteristicas)
            total_extraidos += len(df_pag)
            data_coches.clear()
            df_pag.to_csv(DAILY_CARS_PATH, mode= "w" if primer_guardado else "a", header= primer_guardado, index = False)

            if total_extraidos != num_extraer:
                time.sleep(random.randint(10, 25))
                next_pag: WebElement = selenium_scraper.find_element(by = By.XPATH, value = "//a[@class='last']")
                if next_pag:
                    next_pag.click()
    except Exception as e:
        with open(f"{CURRENT_DIR}/../../data/errores.txt", "a") as file:
            file.write(str(f"{datetime.datetime.now().strftime("%d-%m-%Y")}|{selenium_scraper.find_element(by = By.XPATH, value = "//a[@class='last']")}| - {selenium_scraper.current_url()} \n {e}\n"))
        print(f"exception: {e}")

    finally:
        selenium_scraper.close()