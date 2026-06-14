from . import save_to_csv
from bs4 import BeautifulSoup
from pathlib import Path
import requests, re, pandas as pd

# Congfiguración de la sesión
HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0",
    "Referer": "https://www.prensa.com/sociedad/",
}

'''
La Prensa usa Arc XP (Arc Publishing) como CMS. Esto significa que:
1. Cada sección tiene un feed RSS público en: https://www.prensa.com/arc/outboundfeeds/rss/?section=/<seccion>&outputType=xml
2. Cada artículo individual es una página HTML estándar que podemos parsear con BeautifulSoup para extraer título, fecha, categoría y texto completo.
'''

# URL base del feed RSS de La Prensa (Arc Publishing)
# Cada sección tiene su propio feed agregando ?section=/nombre
RSS_BASE = "https://www.prensa.com/arc/outboundfeeds/rss/?outputType=xml&section=/"

def start_session(headers: dict) -> requests.Session:
    # Crea una sesión HTTP reutilizable con los headers definidos
    session = requests.Session()
    session.headers.update(headers)
    return session

def create_html_parser(html: str) -> BeautifulSoup:
    # Convierte el HTML en un objeto BeautifulSoup
    return BeautifulSoup(html, "html.parser")

# Extracción de URLs de noticias desde el feed RSS
def get_laprensa_urls_from_rss(section_name: str, session: requests.Session) -> list[str]:
    # La Prensa usa Arc Publishing, un CMS que genera feeds RSS por sección.
    # El feed devuelve XML con la lista de noticias recientes de esa sección.
    # Ejemplo de URL: .../rss/?outputType=xml&section=/sociedad
 
    url = RSS_BASE + section_name
    response = session.get(url)
 
    if response.status_code != 200:
        print(f"  [WARN] No se pudo obtener el RSS de /{section_name}")
        return []
 
    # Parseamos el XML con BeautifulSoup en modo xml
    soup = BeautifulSoup(response.text, "xml")
 
    # Cada noticia está en una etiqueta <item>, con su URL en <link>
    urls = []
    for item in soup.find_all("item"):
        link = item.find("link")
        if link and link.text.strip():
            urls.append(link.text.strip())
 
    return urls

# Procesamiento de fechas
def parse_laprensa_date(raw_date: str) -> str:
    # Las fechas en los metadatos vienen en formato: "2026-05-30T05:01:00Z"
    # tomamos los primeros 10 caracteres
 
    if not raw_date:
        return ""
 
    # Formato: YYYY-MM-DDTHH:MM:SSZ
    match = re.search(r"(\d{4}-\d{2}-\d{2})", raw_date)
    if match:
        return match.group(1)
 
    return ""

# Procesamiento de categorías
def get_laprensa_category(url: str) -> str:

# Obtiene la categoría a partir de la URL.
# https://www.prensa.com/sociedad/noticia/ -> sociedad

    url_parts = url.replace("https://www.prensa.com/", "").split("/")
 
    if url_parts:
        return url_parts[0]
 
    return "desconocida"

# Scraping de una noticia individual
def scrap_laprensa_new_summary(url: str, session: requests.Session) -> dict:
    # Información básica de la noticia
    data = {
        "medio": "La Prensa",
        "titulo": "",
        "fecha": "",
        "categoria_original": get_laprensa_category(url),
        "texto": "",
        "url": url
    }

    response = session.get(url)

    if response.status_code != 200:
        return data

    html = create_html_parser(response.text)

    # Título: meta og:title o meta dcterms.title
    title_tag = html.find("meta", {"property": "og:title"}) or \
                html.find("meta", {"name": "dcterms.title"})
    if title_tag:
            data["titulo"] = title_tag.get("content", "").strip()
    
    # Fecha: meta article:published_time  (formato: 2026-05-30T05:01:00Z)
    date_tag = html.find("meta", {"property": "article:published_time"}) or \
               html.find("meta", {"name": "dcterms.date"})
    if date_tag:
        data["fecha"] = parse_laprensa_date(date_tag.get("content", ""))

    # Texto: meta description  (es un resumen del artículo)
    # Nota: el texto completo requiere JS; usamos el resumen como alternativa
    desc_tag = html.find("meta", {"name": "description"}) or \
               html.find("meta", {"property": "og:description"})
    if desc_tag:
        data["texto"] = desc_tag.get("content", "").strip()
 
    return data

# Scraping de una página de noticias (una categoría)
def scrap_laprensa_news_chunk(html: BeautifulSoup, session: requests.Session) -> list[dict]:
    # Busca todos los bloques story-box-right
    # Obtiene la información completa de cada noticia enlistada en la página

    urls = [
        get_laprensa_new_url(news)
        for news in html.find_all(
            "div",
            class_="story-box-right"
        )
    ]

    return [
        scrap_laprensa_new_summary(url, session)
        for url in urls
        if url
    ]

# Scraping de una sección completa
def scrap_laprensa_news_section(url: str, pages: int = 1) -> list[dict]:
    # Obtiene todas las noticias de una sección de La Prensa:
    # 1. Extrae el nombre de la sección de la URL
    # 2. Obtiene las URLs de noticias desde el feed RSS de esa sección
    # 3. Visita cada noticia y extrae sus datos
 
    session = start_session(HEADERS)
 
    # Extraer el nombre de la sección desde la URL
    # Ejemplo: "https://www.prensa.com/sociedad/" -> "sociedad"
    section_name = url.replace("https://www.prensa.com/", "").strip("/")
 
    print(f"  Obteniendo RSS de: /{section_name}")
    urls = get_laprensa_urls_from_rss(section_name, session)
    print(f"  Noticias encontradas: {len(urls)}")
 
    news = []
    for article_url in urls:
        print(f"    Scraping: {article_url}")
        article_data = scrap_laprensa_new_summary(article_url, session)
        news.append(article_data)
 
    return news

# Exportar a CSV
def main():

    SOURCES = [
        "https://www.prensa.com/sociedad/",
        "https://www.prensa.com/comunicados/",
        "https://www.prensa.com/judiciales/",
        "https://www.prensa.com/politica/",
        "https://www.prensa.com/economia/",
        "https://www.prensa.com/mundo/",
        "https://www.prensa.com/deportes/",
        "https://www.prensa.com/unidad-investigativa/",
        "https://www.prensa.com/vivir/"
    ]

    FILE_DIR = Path(__file__).parent

    OUTPUT = f"{FILE_DIR}/../data/raw/noticias_laprensa.csv"

    total_news = []

    for source in SOURCES:
        print(f"{'='*25} SCRAPING: {source} {'='*25}")
        processed_news = scrap_laprensa_news_section(source)
        total_news.extend(processed_news)

    df = pd.DataFrame(total_news)
    save_to_csv(df, OUTPUT)


if __name__ == "__main__":
    main()
