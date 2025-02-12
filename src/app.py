from scraper.scraper import Scraper
import numpy as np
import random

#https://www.autocasion.com/coches-ocasion
#https://www.autocasion.com/coches-segunda-mano

with open("../bin/user-agents.txt", "r") as file:
    user_agents: np.array = file.read().splitlines()

url: str = "https://www.autocasion.com/coches-segunda-mano"
headers: dict[str, str] = {
    "User-Agent": str(user_agents[random.randint(0, len(user_agents) - 1)])
}


scraper = Scraper(url, headers)
print(headers["User-Agent"])
print(scraper._get_soup())
#lista_links_coches = scraper.get_links()
#print(lista_links_coches)