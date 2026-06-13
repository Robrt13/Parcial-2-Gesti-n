from . import save_to_csv
from bs4 import BeautifulSoup
from pathlib import Path
import requests, re, pandas as pd

HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.tvn-2.com/nacionales/",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
}


def start_session(headers: dict) -> requests.Session:
    session = requests.Session()
    session.headers.update(headers)
    return session


def create_html_parser(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def get_tvn_new_url(summary: BeautifulSoup) -> str:
    tag = summary.find("a", class_="title")
    if not tag:
        return ""
    return tag.get("href", "")


def parse_tvn_date(raw_date: str) -> str:
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
    DATE_PATTERN = r"(\d{1,2}) de (\w+) (\d{4})"

    match = re.search(DATE_PATTERN, raw_date)
    if not match:
        return ""
    
    day = match.group(1).zfill(2)
    month = MONTHS.get(match.group(2).lower())
    year = match.group(3)
    return f"{year}-{month}-{day}"


def get_tvn_category(url: str) -> str:
    url_parts = url.split("/")
    if len(url_parts) < 4:
        return "desconocida"
    category = url_parts[3]
    return "deportes" if category == "tvmax" else category


def scrap_tvn_new_summary(url: str, session: requests.Session) -> dict:
    data = {
        "medio": "TVN",
        "titulo": "",
        "fecha": "",
        "categoria_original": "",
        "texto": "",
        "url": url
    }

    response = session.get(url)
    if response.status_code != 200:
        return data

    html = create_html_parser(response.text)

    title = html.find("h1")
    if title:
        data["titulo"] = title.text.strip()
    
    date = html.find("span", class_="published")
    if date:
        data["fecha"] = parse_tvn_date(date.text.strip())

    data["categoria_original"] = get_tvn_category(url)

    content = html.find("div", class_="bbnx-body")
    if not content:
        return data
    
    paragraphs = content.find_all("p")
    data["texto"] = "\n".join([paragraph.text.strip() for paragraph in paragraphs])

    return data


def scrap_tvn_news_chunk(html: BeautifulSoup, session: requests.Session) -> list[dict]:
    urls = [get_tvn_new_url(new) for new in html.find_all("article", class_="content text-side")]
    return [scrap_tvn_new_summary(url, session) for url in urls if url]


def scrap_tvn_feed(url: str, pages: int, session: requests.Session) -> list[dict]:
    processed_news = []
    for page in range(pages):
        response = session.get(url)
        if response.status_code != 200:
            return processed_news
        
        try:
            data = response.json()
        except ValueError:
            return processed_news

        html = create_html_parser(data.get("html"))
        processed_news.extend(scrap_tvn_news_chunk(html, session))

        nextPage = data.get("nextPage")
        if not nextPage:
            return processed_news
        
        url = nextPage

    return processed_news


def scrap_tvn_pagination(url: str, pages: int, session: requests.Session) -> list[dict]:
    processed_news = []
    for page in range(pages):
        nextPage = f"{url}/{page + 2}"
        response = session.get(nextPage)
        if response.status_code == 200:
            html = create_html_parser(response.text)
            processed_news.extend(scrap_tvn_news_chunk(html, session))

    return processed_news


def scrap_tvn_news_section(url: str, pages: int = 1) -> list[dict]:
    session = start_session(HEADERS)
    response = session.get(url)
    if response.status_code != 200:
        return []

    html = create_html_parser(response.text)
    news = scrap_tvn_news_chunk(html, session)

    isFeed = html.find("bbnx-load-more") is not None
    if isFeed:
        nextPage = html.find("bbnx-load-more").get("url")
        scraping_function = scrap_tvn_feed
    else:
        nextPage = url
        scraping_function = scrap_tvn_pagination
    news.extend(scraping_function(nextPage, pages, session))

    return news


def main():
    SOURCES = [
        "https://www.tvn-2.com/nacionales/",
        "https://www.tvn-2.com/mundo/",
        "https://www.tvn-2.com/contenido-exclusivo/",
        "https://www.tvn-2.com/entretenimiento/",
        "https://www.tvn-2.com/tvmax/lpf/",
        "https://www.tvn-2.com/tvmax/futbol-internacional/",
        "https://www.tvn-2.com/tvmax/beisbol-nacional/",
        "https://www.tvn-2.com/tvmax/beisbol/",
        "https://www.tvn-2.com/tvmax/mas-deportes/"
    ]
    FILE_DIR = Path(__file__).parent
    OUTPUT = f"{FILE_DIR}/../data/raw/noticias_tvn.csv"

    total_news = []
    for source in SOURCES:
        print(f"{'='*25} SCRAPING: {source} {'='*25}")
        processed_news = scrap_tvn_news_section(source)
        total_news.extend(processed_news)
    df = pd.DataFrame(total_news)

    save_to_csv(df, OUTPUT)


if __name__ == "__main__":
    main()