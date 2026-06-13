from . import Path
from scrapers import scrap_tvn_news_section
from ingestion import ingest_data
from cleaning import merge_csv_data, clean_data
from transformation import transform_data
from commons import save_to_csv


def run_pipeline(ingestion_configs: list[dict], output: str):
    outputs = ingest_data(ingestion_configs)
    merged_data = merge_csv_data(outputs)
    cleaned_data = clean_data(merged_data)
    transformed_data = transform_data(cleaned_data)
    save_to_csv(transformed_data, output)


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
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"

    run_pipeline(INGESTION_CONFIGS, OUTPUT)


if __name__ == "__main__":
    main()