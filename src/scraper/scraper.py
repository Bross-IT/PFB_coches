import numpy as np

import requests
import bs4 # para ver la versión
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, url: str, headers: dict[str, str]) -> None:
        self.url = url
        self.headers = headers
        
    def _get_soup(self) -> BeautifulSoup:
        response = requests.get(self.url, self.headers)
        print(response.status_code)
        print(self.url)
        print(self.headers)
        print("---"*10)
        print(response.text)
        return BeautifulSoup(response.text, 'html.parser')
    
    def get_links(self) -> np.array:
        soup = self._get_soup()        
        links = soup.find(class_ = "anuncio").find_all()

        return links

