from scrapers import scrap_tvn_news_section, CATEGORIAS_tvn
from scrapers import scrap_telemetro_news_section, CATEGORIAS_tlm
from scrapers import scrap_laprensa_news_section, CATEGORIAS_lp
from .ingestion import ingest_data
from .cleaning import merge_csv_data, clean_data
from .transformation import transform_data
from models import analizar_noticias
from .commons import save_to_csv
from pathlib import Path


def run_pipeline(
        ingestion_configs: list[dict],
        processed_output: str,
        cantidad_noticias_por_categoria_por_medio: int,
        modelo: str,
        analyzed_output: str
    ):
    print(f"{'='*25} PIPELINE START {'='*25}")
    outputs = ingest_data(ingestion_configs)
    merged_data = merge_csv_data(outputs)
    cleaned_data = clean_data(merged_data)
    transformed_data = transform_data(cleaned_data)
    save_to_csv(transformed_data, processed_output)
    analyzed_data = analizar_noticias(transformed_data, cantidad_noticias_por_categoria_por_medio, modelo)
    save_to_csv(analyzed_data, analyzed_output)
    print(f"{'='*25} PIPELINE END {'='*25}")


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
    PROCESSED_OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"
    CANTIDAD_NOTICIAS_POR_CATEGORIA_POR_MEDIO = 10
    MODELO = "qwen3.5:0.8b"
    ANALYZED_OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_analizadas.csv"
    run_pipeline(
        INGESTION_CONFIGS,
        PROCESSED_OUTPUT,
        CANTIDAD_NOTICIAS_POR_CATEGORIA_POR_MEDIO,
        MODELO,
        ANALYZED_OUTPUT
    )


if __name__ == "__main__":
    main()