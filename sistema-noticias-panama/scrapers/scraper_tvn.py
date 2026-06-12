# Columnas generadas por el scraper: fecha, medio, titulo, categoria_original, texto
import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
from pathlib import Path

def parse_tvn_date(raw_date: str) -> datetime.date:
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
    DATE_FORMAT = "%Y-%m-%d"

    match = re.search(DATE_PATTERN, raw_date)
    day = match.group(1).zfill(2)
    month = MONTHS.get(match.group(2).lower())
    year = match.group(3)
    parsed_date = datetime.datetime.strptime(f"{year}-{month}-{day}", DATE_FORMAT).date()
    return parsed_date


def get_tvn_category(url: str) -> str:
    url_parts = url.split("/")
    category = url_parts[3]
    if category == "tvmax":
        category = "deportes"
    return category


def scrap_tvn_new_preview(new: BeautifulSoup) -> dict:
    url = new.find("a", class_="title").get("href")
    response = requests.get(url)

    parser = BeautifulSoup(response.text, "html.parser")
    title = parser.find("h1").text.strip()
    date = parse_tvn_date(parser.find("span", class_="published").text.strip())
    media = "TVN"
    content = "\n".join([paragraph.text.strip() for paragraph in parser.find("div", class_="bbnx-body").find_all("p")])
    category = get_tvn_category(url)

    return {
        "fecha": date,
        "medio": media,
        "titulo": title,
        "categoria_original": category,
        "texto": content
    }


def scrap_tvn_feed(url: str, pages: int, session: requests.Session) -> list:
    processed_news = []
    for page in range(pages):
        response = session.get(url)
        data = response.json()
        parser = BeautifulSoup(data.get("html"), "html.parser")

        raw_news = parser.find_all("article", class_="content text-side")
        processed_news.extend([scrap_tvn_new_preview(new) for new in raw_news])

        nextPage = data.get("nextPage")
        if not nextPage:
            break
        url = nextPage

    return processed_news


def scrap_tvn_pagination(url: str, pages: int, session: requests.Session) -> list:
    processed_news = []
    for page in range(pages):
        nextPage = f"{url}/{page + 2}"
        response = session.get(nextPage)

        parser = BeautifulSoup(response.text, "html.parser")
        raw_news = parser.find_all("article", class_="content text-side")
        processed_news.extend([scrap_tvn_new_preview(new) for new in raw_news])

    return processed_news


def scrap_tvn_news_section(url: str, pages: int = 1) -> list:
    SESSION = requests.Session()
    SESSION.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.tvn-2.com/nacionales/",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
    })

    response = SESSION.get(url)
    parser = BeautifulSoup(response.text, "html.parser")

    raw_news = parser.find_all("article", class_="content text-side")
    processed_news = [scrap_tvn_new_preview(new) for new in raw_news]

    isFeed = parser.find("bbnx-load-more") is not None
    if isFeed: processed_news.extend(scrap_tvn_feed(parser.find("bbnx-load-more").get("url"), pages, SESSION))
    else: processed_news.extend(scrap_tvn_pagination(url, pages, SESSION))

    return processed_news

if __name__ == "__main__":
    sections = [
        "https://www.tvn-2.com/nacionales/",
        "https://www.tvn-2.com/mundo/",
        "https://www.tvn-2.com/contenido-exclusivo/",
        "https://www.tvn-2.com/entretenimiento/",
        "https://www.tvn-2.com/tvmax/lpf/",
        "https://www.tvn-2.com/tvmax/futbol-internacional/",
        "https://www.tvn-2.com/tvmax/beisbol-nacional/",
        "https://www.tvn-2.com/tvmax/beisbol/"
        "https://www.tvn-2.com/tvmax/mas-deportes/"
    ]
    total_news = []
    for section in sections:
        print(f"Scraping {section}")
        processed_news = scrap_tvn_news_section(section)
        total_news.extend(processed_news)

    df = pd.DataFrame(total_news)
    df.to_csv(f"{Path(__file__).parent}/../data/raw/noticias_tvn.csv", index=False)