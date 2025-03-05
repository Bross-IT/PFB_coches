from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from urllib.parse import urlparse, parse_qs
import pathlib
import requests

import numpy as np
import pandas as pd

import time
import datetime
import random

class SeleniumScraper:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()

    def open_url(self, url) -> None:
        self.driver.get(url)

    def current_url(self) -> str:
        return self.driver.current_url

    def back(self) -> None:
        self.driver.back()

    def find_element(self, by: By, value: str) -> WebElement|None:
        try:
            return self.driver.find_element(by, value)
        except:
            return None

    def find_elements(self, by: By, value: str) -> list[WebElement]:
        return self.driver.find_elements(by, value)

    def get_text(self, by: By, value: str) -> str:
        element = self.find_element(by, value)
        return element.text if element else ''

    def get_attribute(self, by: By, value: str, attribute: str) -> str:
        element = self.find_element(by, value)
        return element.get_attribute(attribute) if element else ''
        
    def close(self) -> None:
        self.driver.quit()

    def script_scroll(self, pixels: int) -> None:
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")

        # Damos una espera aleatoria para simular la accion de un humano
        time.sleep(random.uniform(0.5, 2))

    def get_current_page(self, url: str) -> int:
        parametros: dict = parse_qs(urlparse(url).query)
        return int(parametros.get("page", [1])[0]) 
    
    def get_features_cars(self) -> np.array:
        script_dir = pathlib.Path(__file__).resolve().parent

        marca: str = self.driver.find_element(by = By.TAG_NAME, value = "h1").text
        spans = self.driver.find_element(by=By.XPATH, value="//div[@class='etiquetas']").find_elements(by = By.TAG_NAME, value = "span")
        
        localizacion: str = [ spans[-1].text if spans[-1].text != "" else spans[-2].text ][0]
        if localizacion == "":
            with open(f"{script_dir}/../../data/localizacion_errors.txt", "w") as file:
                file.write(str(f"localizacion: {localizacion} , url: {self.driver.current_url}"))
        try:
            distintivo_ambiental: str = self.driver.find_element(by=By.XPATH, value="//div[@class='etiquetas']").find_element(by = By.TAG_NAME, value = "img").get_attribute("alt")
        except NoSuchElementException as nse:
            distintivo_ambiental: str =''
        try:
            anio: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-calendario']").find_element(By.XPATH, "./parent::li").text.split(":")[1].strip()
        except NoSuchElementException as nse:
            anio: str = ''
        try:
            kilometraje: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-velocimetro']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            kilometraje: str = ''
        try:
            combustible: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-combustible']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            combustible: str = ''
        try:
            garantia: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-file']").find_element(By.XPATH, "./parent::li").text.split(":")[1].strip()
        except NoSuchElementException as nse:
            garantia: str = ''
        try:
            cambio: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-cambio-manual']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            cambio: str = ''
        try:
            carroceria: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-coche-masa']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            carroceria: str = ''
        try:
            plazas: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-chairs']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            plazas: str = ''
        try:
            potencia: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-motor']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            potencia: str = ''
        try:
            puertas: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-puerta']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            puertas: str = ''
        try:
            color: str = self.driver.find_element(by = By.XPATH, value = "//li//span[@class='icon icon-cubo']").find_element(By.XPATH, "./parent::li").text.strip()
        except NoSuchElementException as nse:
            color: str = ''
        try:
            precio: str = self.get_text(by=By.XPATH, value="//ul[@class='tabla-precio']//li").split(":")[1].strip()
        except IndexError as ie:
            precio: str = self.get_text(By.CLASS_NAME, "precio").strip()
            print(f"IndexError: {ie}")
            print(self.driver.current_url)
        #marca: str = self.driver.find_elements(by=By.XPATH, value="//input[@id='brand-name']")[0].get_attribute("value")
        #modelo: str = self.driver.find_elements(by=By.XPATH, value="//input[@id='family-name']")[0].get_attribute("value")

        tab_spec_2 = self.find_element(By.XPATH, '//li[@class="tab-spec-2"]')
        if tab_spec_2 is not None:
            time.sleep(random.uniform(0.5, 2))
            ActionChains(self.driver).move_to_element(tab_spec_2).perform()
            #self.driver.execute_script("arguments[0].scrollIntoView();", tab_spec_2)
            tab_spec_2.click()
            
        consumo_medio: str = self.get_text(by = By.XPATH, value = '//ul[contains(@class,"tab-spec-2")]/li').strip()

        try:
            vendedor: str = self.driver.find_element(by = By.XPATH, value = "//div[@class='datos-concesionario']").find_element(By.TAG_NAME, "p").text.strip()
        except NoSuchElementException as nse:
            vendedor: str = ''
        try:
            self.driver.find_element(by = By.XPATH, value = "//span[@class='icon icon-certificado']").text.strip()
            certificado: str = "Si"
        except NoSuchElementException as nse:
            certificado: str = 'No'
        
        fecha_extraccion: datetime.datetime = datetime.datetime.now()
        url_actual: str = self.current_url()
        referencia: str = url_actual.split("-")[-1]

        try:
            url_imagen: str = self.get_attribute(by=By.XPATH, value="//img[contains(normalize-space(@class), 'type-image')]", attribute = "src")
            if url_imagen != '':
                response_img = requests.get(url_imagen)
                ruta_imagen: str = f"{script_dir}/../../img/coches/{url_imagen.split('/')[-1].split("?")[0]}"
                with open(ruta_imagen, "wb") as file:
                    file.write(response_img.content)
            else:
                ruta_imagen = ''
        except NoSuchElementException as nse:
            ruta_imagen = ''
            print(f"No se encontro imagen para {self.driver.current_url} \n {nse}")

        return np.array([marca, anio, localizacion, kilometraje, combustible, distintivo_ambiental, garantia, cambio, carroceria, plazas, potencia, puertas, color, precio, vendedor, consumo_medio, certificado, fecha_extraccion, referencia, url_actual, ruta_imagen])

