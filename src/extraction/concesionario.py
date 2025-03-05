from seleniumScraper import SeleniumScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

import numpy as np
import pandas as pd

import os
import time
import pathlib

def contiene(lista: list[str], cadena: str) -> str:
    elemento = next((elemento for elemento in lista if str.lower(cadena) in str.lower(elemento)), '')
    return elemento.split(':')[1].strip() if elemento != '' else elemento

dict_concesionario: dict[str, np.array] = {
    "nombre": np.array([]),
    "calle": np.array([]),
    "municipio": np.array([]),
    "provincia": np.array([]),
    "codigo_postal": np.array([]),
}

try:
    script_dir = pathlib.Path(__file__).resolve().parent
    selenium_scraper = SeleniumScraper()
    selenium_scraper.open_url("https://www.autocasion.com/concesionarios?order=nombre-a-z")
    selenium_scraper.find_element(by = By.CSS_SELECTOR, value = "#didomi-notice-disagree-button").click()

    next_pag = True
    while True and next_pag is not None:
        actual_url = selenium_scraper.current_url()
        actual_pag = int(selenium_scraper.get_current_page(actual_url))
        with open(f"{script_dir}/../../data/last-page-concesionarios.txt", "w") as file:
            file.write(str(f"{actual_pag}\n{actual_url}"))
        print("actual page " + str(actual_pag) + " ...")
        time.sleep(1.5)
        li_concesionarios = selenium_scraper.find_elements(by = By.XPATH, value = "//ul[contains(@class, 'listado-concesionarios')]//li")
        selenium_scraper.script_scroll(180)
        for concesionario in li_concesionarios:
            lista_info: list[str] = concesionario.find_element(by = By.XPATH, value = ".//a").text.split("\n")
            dict_concesionario["nombre"] = np.append(dict_concesionario["nombre"], lista_info[0])

            dict_concesionario["calle"] = np.append(dict_concesionario["calle"], contiene(lista_info, "Calle:"))
            dict_concesionario["municipio"] = np.append(dict_concesionario["municipio"], contiene(lista_info, "Municipio:"))
            dict_concesionario["provincia"] = np.append(dict_concesionario["provincia"], contiene(lista_info, "Provincia:"))
            dict_concesionario["codigo_postal"] = np.append(dict_concesionario["codigo_postal"], contiene(lista_info, "Código postal:"))

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
    primer_guardado: bool = not os.path.exists(ruta_archivo)
    df_concesionario = pd.DataFrame(dict_concesionario)
    df_concesionario.to_csv(ruta_archivo, mode= "w" if primer_guardado else "a", header= primer_guardado, index = False)
