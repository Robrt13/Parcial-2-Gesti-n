from . import pd, Path
from scrapers import save_to_csv
from scrapers import scrap_tvn_news_section, CATEGORIAS_tvn
from scrapers import scrap_telemetro_news_section, CATEGORIAS_tlm
from scrapers import scrap_laprensa_news_section, CATEGORIAS_lp


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
            save_to_csv(data, scraping["output"])
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
                "sources": [{"url": categoria, "pages": 1} for categoria in CATEGORIAS_tvn]
            }
        },
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_telemetro_news_section,
                "output": f"{FILE_DIR}/../data/raw/noticias_telemetro.csv",
                "sources": [{"url": categoria, "pages": 1} for categoria in CATEGORIAS_tlm]
            }
        },
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_laprensa_news_section,
                "output": f"{FILE_DIR}/../data/raw/noticias_laprensa.csv",
                "sources": [{"url": categoria, "pages": 1} for categoria in CATEGORIAS_lp]
            }
        }
    ]
    
    ingest_data(INGESTION_CONFIGS)

if __name__ == "__main__":
    main()