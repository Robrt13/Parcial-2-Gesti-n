from . import pd, Path
from .commons import save_to_csv
from scrapers import scrap_tvn_news_section


def scrape_sources(sources: list[dict], scraper: function) -> list[dict]:
    scraped_data = []
    for source in sources:
        print(f"Scraping: {source['url']}")
        source_data = scraper(source["url"], source["pages"])
        scraped_data.extend(source_data)
    return scraped_data


def ingest_data(ingestion_configs: list[dict]) -> list[str]:
    outputs: list[str] = []
    for ingestion in ingestion_configs:
        if ingestion["type"] == "web_scraping":
            print(f"{'='*25} WEB SCRAPING PROCESS {'='*25}")
            scraping = ingestion["config"]

            data = scrape_sources(scraping["sources"], scraping["scraper"])
            df = pd.DataFrame(data)
            save_to_csv(df, scraping["output"])
            outputs.append(scraping["output"])
    
    return outputs


def main():
    FILE_DIR = Path(__file__).parent
    INGESTION_CONFIGS = [
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_tvn_news_section,
                "output": f"{FILE_DIR}/../data/raw/noticias_tvn.csv",
                "sources": [
                    {"url": "https://www.tvn-2.com/nacionales/",                 "pages": 1},
                    {"url": "https://www.tvn-2.com/mundo/",                      "pages": 1},
                    {"url": "https://www.tvn-2.com/contenido-exclusivo/",        "pages": 1},
                    {"url": "https://www.tvn-2.com/entretenimiento/",            "pages": 1},
                    {"url": "https://www.tvn-2.com/tvmax/lpf/",                  "pages": 1},
                    {"url": "https://www.tvn-2.com/tvmax/futbol-internacional/", "pages": 1},
                    {"url": "https://www.tvn-2.com/tvmax/beisbol-nacional/",     "pages": 1},
                    {"url": "https://www.tvn-2.com/tvmax/beisbol/",              "pages": 1},
                    {"url": "https://www.tvn-2.com/tvmax/mas-deportes/",         "pages": 1}
                ]
            }
        }
    ]
    
    ingest_data(INGESTION_CONFIGS)

if __name__ == "__main__":
    main()