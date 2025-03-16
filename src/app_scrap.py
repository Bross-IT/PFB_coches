from extraction import extraction_func

print("Scraping concesionarios...")
extraction_func.scraper_concesionario("https://www.autocasion.com/concesionarios?order=nombre-a-z", 20)
print("Scraping concesionarios terminado! Iniciamos el scraping de coches...")
extraction_func.scraper_coches("https://www.autocasion.com/coches-ocasion?direction=desc&page=1&sort=updated_at", 30)
print("Scraping coches terminado!")

