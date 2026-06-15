import requests
import re
import csv
import time
from bs4 import BeautifulSoup
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.telemetro.com/nacionales",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
}

CATEGORIAS = [
    "nacionales",
    "internacionales",
    "actualidad",
    "economia",
    "deportes",
    "politica",
    "entretenimiento",
]

MONTHS = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}


def parse_telemetro_date(raw_date: str) -> str:
    match = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", raw_date)
    if not match:
        return ""
    day = match.group(1).zfill(2)
    month = MONTHS.get(match.group(2).lower(), "")
    year = match.group(3)
    if not month:
        return ""
    return f"{year}-{month}-{day}"


def obtener_links_categoria(categoria):
    url = f"https://www.telemetro.com/{categoria}"
    response = requests.get(url, headers=HEADERS)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    noticias = soup.find_all("h2", class_="news-article__title")
    for noticia in noticias:
        enlace = noticia.find("a")
        if enlace:
            links.append(enlace["href"])
    return links


def obtener_links_pagina(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    noticias = soup.find_all("h2", class_="news-article__title")
    for noticia in noticias:
        enlace = noticia.find("a")
        if enlace:
            links.append(enlace["href"])
    return links


def obtener_datos_noticia(url, categoria):
    response = requests.get(url, headers=HEADERS)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    titulo = soup.find("h1", class_="news-headline__title")
    fecha = soup.find("span", class_="news-headline__date")
    categoria_original = soup.find("span", class_="news-headline__topic")

    # Texto completo: múltiples article.article-body, luego fallback al resumen
    cuerpos = soup.find_all("article", class_="article-body")
    if cuerpos:
        parrafos = [p.text.strip() for c in cuerpos for p in c.find_all("p") if p.text.strip()]
        texto = "\n".join(parrafos)
    else:
        contenedor = soup.find("h2", class_="news-headline__article-summary")
        parrafo = contenedor.find("p") if contenedor else None
        texto = parrafo.text.strip() if parrafo else ""

    cat = categoria_original.text.replace("\xa0", " ").strip().strip("-").strip() if categoria_original else categoria

    return {
        "titulo": titulo.text.strip() if titulo else "",
        "fecha": parse_telemetro_date(fecha.text.strip()) if fecha else "",
        "texto": texto,
        "url": url,
        "medio": "Telemetro",
        "categoria_original": cat,
    }


def scrap_telemetro_news_section(url: str, pages: int = 1) -> list:
    categoria = url.rstrip("/").split("/")[-1]

    links = obtener_links_pagina(url)
    for page in range(2, pages + 1):
        links.extend(obtener_links_pagina(f"{url}/{page}"))

    return [obtener_datos_noticia(link, categoria) for link in links if link]


def scraper_telemetro():
    resultados = []
    OUTPUT = Path(__file__).parent / "../data/raw/noticias_telemetro.csv"

    for categoria in CATEGORIAS:
        print(f"categoría: {categoria}")
        links = obtener_links_categoria(categoria)

        for link in links:
            print(f"  → {link}")
            datos = obtener_datos_noticia(link, categoria)
            resultados.append(datos)
            time.sleep(1)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        campos = ["fecha", "medio", "titulo", "categoria_original", "texto"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nListo. {len(resultados)} noticias guardadas.")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    scraper_telemetro()
