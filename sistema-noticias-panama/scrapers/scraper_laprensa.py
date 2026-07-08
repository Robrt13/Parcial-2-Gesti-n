import requests, re, json
from pathlib import Path
from .commons import create_html_parser, save_to_csv

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


def parse_laprensa_date(raw_date: str) -> str:
    return raw_date.split("T")[0]


def parse_laprensa_content_elements(content_elements: list[dict]) -> str:
    TAG_MAP = {
        "text": "p",
        "header": "h2",
    }

    parts = []
    for element in content_elements:
        element_type = element.get("type")
        content = element.get("content", "").strip() if element.get("content") else ""

        if element_type in TAG_MAP:
            if content:
                tag = TAG_MAP[element_type]
                parts.append(f"<{tag}>{content}</{tag}>")
        elif element_type == "raw_html":
            parts.append(content)

    html = create_html_parser("<article>\n" + "\n".join(parts) + "\n</article>")
    return "\n".join(paragraph.get_text(strip=True) for paragraph in html.find_all("p"))


def scrap_laprensa_new(new_data: dict, section_url: str) -> dict:
    return {
        "medio": "La Prensa",
        "titulo": new_data["headlines"]["basic"],
        "fecha": parse_laprensa_date(new_data["publish_date"]),
        "categoria_original": new_data["canonical_url"].split("/")[1],
        "texto": parse_laprensa_content_elements(new_data["content_elements"]),
        "url": f"{section_url[:-1]}{new_data["canonical_url"]}"
    }


def scrap_laprensa_section_page(url: str) -> list[dict]:
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    html = create_html_parser(response.text)
    script = html.find("script", id="fusion-metadata").string
    match = re.search(r"Fusion\.contentCache\s*=\s*(\{.*?\});Fusion\.layout", script, re.S)
    json_data = json.loads(match.group(1))

    news_data = []
    for key in json_data["newsfeed-fetch"].keys():
        news = json_data["newsfeed-fetch"][key]["data"]["content_elements"]
        for new in news:
            news_data.append(scrap_laprensa_new(new, url))
        
    return news_data


def scrap_laprensa_news_section(section_url: str, pages: int = 1) -> list[dict]:
    news_data = scrap_laprensa_section_page(section_url)
    for page in range(pages):
        news_data.extend(scrap_laprensa_section_page(f"{section_url}{page + 2}"))
    return news_data


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