import requests
import re
from pathlib import Path
from .commons import start_session, create_xml_parser, create_html_parser, save_to_csv

HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0",
    "Referer": "https://www.prensa.com/sociedad/",
}

CATEGORIAS = [
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

'''
La Prensa usa Arc XP (Arc Publishing) como CMS. Esto significa que:
1. Cada sección tiene un feed RSS público en: https://www.prensa.com/arc/outboundfeeds/rss/?section=/<seccion>&outputType=xml
2. Cada artículo individual es una página HTML estándar que podemos parsear con BeautifulSoup para extraer título, fecha, categoría y texto completo.
'''

# Cada sección tiene su propio feed agregando ?section=/nombre
RSS_BASE = "https://www.prensa.com/arc/outboundfeeds/rss/?outputType=xml&section=/"


def parse_laprensa_date(raw_date: str) -> str:
    # Las fechas en los metadatos vienen en formato: "2026-05-30T05:01:00Z"
    match = re.search(r"(\d{4}-\d{2}-\d{2})", raw_date)
    if match:
        return match.group(1)

    return ""


def get_laprensa_category(url: str) -> str:
    # Obtiene la categoría a partir de la URL.
    # https://www.prensa.com/sociedad/noticia/ -> sociedad

    url_parts = url.replace("https://www.prensa.com/", "").split("/")
    if url_parts:
        return url_parts[0]

    return "desconocida"


def scrap_laprensa_new(url: str, session: requests.Session) -> dict:
    response = session.get(url)
    if response.status_code != 200:
        return {
            "medio": "La Prensa",
            "titulo": "",
            "fecha": "",
            "categoria_original": "",
            "texto": "",
            "url": url
        }

    html = create_html_parser(response.text)

    title_tag = html.find("meta", {"property": "og:title"}) or html.find("meta", {"name": "dcterms.title"})
    date_tag = html.find("meta", {"property": "article:published_time"}) or html.find("meta", {"name": "dcterms.date"})
    desc_tag = html.find("meta", {"name": "description"}) or html.find("meta", {"property": "og:description"})

    return {
        "medio": "La Prensa",
        "titulo": title_tag.get("content", "").strip() if title_tag else "",
        "fecha": parse_laprensa_date(date_tag.get("content", "")) if date_tag else "",
        "categoria_original": get_laprensa_category(url),
        "texto": desc_tag.get("content", "").strip() if desc_tag else "",
        "url": url
    }


def get_laprensa_urls_from_section(section: str, session: requests.Session) -> list[str]:
    url = RSS_BASE + section
    response = session.get(url)
    if response.status_code != 200:
        return []

    soup = create_xml_parser(response.text)

    # Cada noticia está en una etiqueta <item>, con su URL en <link>
    urls = []
    for item in soup.find_all("item"):
        link = item.find("link")
        if link and link.text.strip():
            urls.append(link.text.strip())

    return urls


def scrap_laprensa_news_section(section_url: str, pages: int = 1) -> list[dict]:
    session = start_session(HEADERS)
    section = section_url.replace("https://www.prensa.com/", "").strip("/")
    urls = get_laprensa_urls_from_section(section, session)
    return [scrap_laprensa_new(url, session) for url in urls]


def main():
    FILE_DIR = Path(__file__).parent
    OUTPUT = f"{FILE_DIR}/../data/raw/noticias_laprensa.csv"

    news = []
    for categoria in CATEGORIAS:
        print(f"{'='*25} SCRAPING: {categoria} {'='*25}")
        section_news = scrap_laprensa_news_section(categoria)
        news.extend(section_news)

    save_to_csv(news, OUTPUT)


if __name__ == "__main__":
    main()