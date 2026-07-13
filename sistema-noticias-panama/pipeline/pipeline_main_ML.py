from pathlib import Path

from scrapers import scrap_laprensa_news_section, CATEGORIAS_lp
from scrapers import scrap_telemetro_news_section, CATEGORIAS_tlm
from scrapers import scrap_tvn_news_section, CATEGORIAS_tvn

from models.llm import analizar_noticias
from models.ml import predecir_categorias_ml

from .cleaning import clean_data, merge_csv_data
from .commons import save_to_csv
from .ingestion import ingest_data
from .transformation import transform_data


def run_pipeline(
    ingestion_configs: list[dict],
    processed_output: str,
    cantidad_noticias_por_categoria_por_medio: int,
    modelo: str,
    analyzed_output: str,
):
    print(f"{'=' * 25} PIPELINE START {'=' * 25}")

    outputs = [
        f"{Path(__file__).parent}/../data/raw/noticias_tvn.csv",
        f"{Path(__file__).parent}/../data/raw/noticias_telemetro.csv",
        f"{Path(__file__).parent}/../data/raw/noticias_laprensa.csv",
    ]
    # outputs = ingest_data(ingestion_configs)
    merged_data = merge_csv_data(outputs)
    cleaned_data = clean_data(merged_data)
    transformed_data = transform_data(cleaned_data)

    # Etapa de Machine Learning: agrega la columna categoria_ml sin
    # reemplazar categoria_original ni categoria_predicha.
    ml_data = predecir_categorias_ml(transformed_data)
    save_to_csv(ml_data, processed_output)

    # Etapa LLM: conserva el análisis de sentimiento y categoria_predicha.
    analyzed_data = analizar_noticias(
        ml_data,
        cantidad_noticias_por_categoria_por_medio,
        modelo,
    )
    save_to_csv(analyzed_data, analyzed_output)

    print(f"{'=' * 25} PIPELINE END {'=' * 25}")


def main():
    file_dir = Path(__file__).parent
    ingestion_configs = [
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_tvn_news_section,
                "output": f"{file_dir}/../data/raw/noticias_tvn.csv",
                "sources": [
                    {"url": categoria, "pages": 1}
                    for categoria in CATEGORIAS_tvn
                ],
            },
        },
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_telemetro_news_section,
                "output": f"{file_dir}/../data/raw/noticias_telemetro.csv",
                "sources": [
                    {"url": categoria, "pages": 1}
                    for categoria in CATEGORIAS_tlm
                ],
            },
        },
        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_laprensa_news_section,
                "output": f"{file_dir}/../data/raw/noticias_laprensa.csv",
                "sources": [
                    {"url": categoria, "pages": 1}
                    for categoria in CATEGORIAS_lp
                ],
            },
        },
    ]

    processed_output = (
        f"{file_dir}/../data/processed/noticias_panama_procesadas.csv"
    )
    cantidad_noticias_por_categoria_por_medio = 25
    modelo = "qwen3.5:4b"
    analyzed_output = (
        f"{file_dir}/../data/processed/noticias_panama_analizadas.csv"
    )

    run_pipeline(
        ingestion_configs,
        processed_output,
        cantidad_noticias_por_categoria_por_medio,
        modelo,
        analyzed_output,
    )


if __name__ == "__main__":
    main()