import requests, re
from pathlib import Path
from .commons import create_html_parser, save_to_csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.telemetro.com/nacionales",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest"
}

CATEGORIAS = [
    "https://www.telemetro.com/nacionales",
    "https://www.telemetro.com/internacionales",
    "https://www.telemetro.com/actualidad",
    "https://www.telemetro.com/economia",
    "https://www.telemetro.com/deportes",
    "https://www.telemetro.com/politica",
    "https://www.telemetro.com/entretenimiento"
]


def parse_telemetro_date(raw_date: str) -> str:
    MONTHS = {
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12"
    }
    DATE_PATTERN = r"(\d{1,2}) de (\w+) de (\d{4})"

    match = re.search(DATE_PATTERN, raw_date)
    if not match:
        return ""
    
    day = match.group(1).zfill(2)
    month = MONTHS.get(match.group(2).lower(), "")
    year = match.group(3)

    if not month:
        return ""
    
    return f"{year}-{month}-{day}"


def obtener_links_pagina(url: str) -> list[str]:
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return []
    
    response.encoding = "utf-8"
    soup = create_html_parser(response.text)

    links = []
    noticias = soup.find_all("h2", class_="news-article__title")
    for noticia in noticias:
        enlace = noticia.find("a")
        if enlace:
            links.append(enlace["href"])
    return links


def obtener_datos_noticia(url: str) -> dict:
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {
            "medio": "Telemetro",
            "titulo": "",
            "fecha": "",
            "categoria_original": "",
            "texto": "",
            "url": url
        }
    response.encoding = "utf-8"
    soup = create_html_parser(response.text)

    titulo = soup.find("h1", class_="news-headline__title")
    fecha = soup.find("span", class_="news-headline__date")
    categoria = soup.find("span", class_="news-headline__topic")
    categoria_original = categoria.text.replace("\xa0", " ").strip().strip("-").strip() if categoria else url.rstrip("/").split("/")[-1]

    cuerpos = soup.find_all("article", class_="article-body")
    if cuerpos:
        parrafos = [
            parrafo.text.strip() for cuerpo in cuerpos
            for parrafo in cuerpo.find_all("p")
            if parrafo.text.strip()
        ]
        texto = "\n".join(parrafos)
    else:
        resumen = soup.find("h2", class_="news-headline__article-summary")
        parrafo = resumen.find("p") if resumen else None
        texto = parrafo.text.strip() if parrafo else ""

    return {
        "medio": "Telemetro",
        "titulo": titulo.text.strip() if titulo else "",
        "fecha": parse_telemetro_date(fecha.text.strip()) if fecha else "",
        "categoria_original": categoria_original,
        "texto": texto,
        "url": url
    }


def scrap_telemetro_news_section(url: str, pages: int = 1) -> list[dict]:
    urls = obtener_links_pagina(url)
    for page in range(pages):
        urls.extend(obtener_links_pagina(f"{url}/{page + 2}"))

    return [obtener_datos_noticia(url) for url in urls]


def main():
    FILE_DIR = Path(__file__).parent
    OUTPUT = f"{FILE_DIR}/../data/raw/noticias_telemetro.csv"

    noticias = []
    for categoria in CATEGORIAS:
        print(f"{'='*25} SCRAPING: {categoria} {'='*25}")
        noticias_categoria = scrap_telemetro_news_section(categoria)
        noticias.extend(noticias_categoria)

    save_to_csv(noticias, OUTPUT)


if __name__ == "__main__":
    main()