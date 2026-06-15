from pathlib import Path

from scrapers import scrap_tvn_news_section
from scrapers import scrap_laprensa_news_section
from ingestion import ingest_data
from cleaning import merge_csv_data, clean_data
from transformation import transform_data
from commons import save_to_csv
from pipeline.ingestion import ingest_data
from pipeline.cleaning import merge_csv_data, clean_data
from pipeline.transformation import transform_data
from pipeline.commons import save_to_csv
from models.llm_news_analysis import analizar_csv


# ============================================================
# CONFIGURACION GENERAL DEL PIPELINE
# ============================================================

FILE_DIR = Path(__file__).parent

# Archivo que sale despues de scraping + limpieza + transformacion
OUTPUT_PROCESADO = FILE_DIR / "../data/processed/noticias_panama_procesadas.csv"

# Archivo final que sale despues del analisis con LLM
OUTPUT_ANALIZADO = FILE_DIR / "../data/processed/noticias_panama_analizadas.csv"

# ============================================================
# CAMBIA ESTA VARIABLE SI QUIERES ANALIZAR MAS O MENOS NOTICIAS
# POR CATEGORIA CON EL LLM.
# En este caso queda en 4, como pidio el proyecto.
# ============================================================
NOTICIAS_POR_CATEGORIA = 4

# Modelo Gemini que se va a usar para resumen y sentimiento
MODELO_LLM = "gemini-2.5-flash"


# ============================================================
# CONFIGURACION DE INGESTA
# ============================================================

INGESTION_CONFIGS = [
    {
        "type": "web_scraping",
        "config": {
            "scraper": scrap_tvn_news_section,
            "output": str(FILE_DIR / "../data/raw/noticias_tvn.csv"),
            "sources": [
                {"url": "https://www.tvn-2.com/nacionales/", "pages": 1},
                {"url": "https://www.tvn-2.com/mundo/", "pages": 1},
                {"url": "https://www.tvn-2.com/contenido-exclusivo/", "pages": 1},
                {"url": "https://www.tvn-2.com/entretenimiento/", "pages": 1},
                {"url": "https://www.tvn-2.com/tvmax/lpf/", "pages": 1},
                {"url": "https://www.tvn-2.com/tvmax/futbol-internacional/", "pages": 1},
                {"url": "https://www.tvn-2.com/tvmax/beisbol-nacional/", "pages": 1},
                {"url": "https://www.tvn-2.com/tvmax/beisbol/", "pages": 1},
                {"url": "https://www.tvn-2.com/tvmax/mas-deportes/", "pages": 1},
            ],
        },
    }
]


def run_pipeline(
    ingestion_configs: list[dict],
    output_procesado: str | Path,
    output_analizado: str | Path,
    noticias_por_categoria: int = 5,
    modelo_llm: str = "gemini-2.5-flash",
):
    """
    Ejecuta el pipeline completo del proyecto.

    Flujo:
    1. Ingesta de noticias por web scraping.
    2. Union de archivos CSV.
    3. Limpieza de datos.
    4. Transformacion de datos.
    5. Guardado de noticias procesadas.
    6. Analisis con LLM:
       - resumen_llm
       - sentimiento
    7. Logica de alerta con Python:
       - usa sentimiento + palabras_criticas
       - genera es_alerta y nivel_alerta
    8. Guardado de noticias analizadas.
    """

    output_procesado = Path(output_procesado)
    output_analizado = Path(output_analizado)

    output_procesado.parent.mkdir(parents=True, exist_ok=True)
    output_analizado.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("INICIANDO PIPELINE DE NOTICIAS DE PANAMA")
    print("=" * 70)

    print("\n[1/6] Ejecutando ingesta de datos...")
    outputs = ingest_data(ingestion_configs)

    print("\n[2/6] Uniendo archivos CSV...")
    merged_data = merge_csv_data(outputs)

    print("\n[3/6] Limpiando datos...")
    cleaned_data = clean_data(merged_data)

    print("\n[4/6] Transformando datos...")
    transformed_data = transform_data(cleaned_data)

    print("\n[5/6] Guardando CSV procesado...")
    save_to_csv(transformed_data, str(output_procesado))
    print(f"CSV procesado guardado en: {output_procesado}")

    print("\n[6/6] Analizando muestra con LLM...")
    print(f"Noticias por categoria: {noticias_por_categoria}")
    print(f"Modelo LLM: {modelo_llm}")

    analizar_csv(
        input_path=str(output_procesado),
        output_path=str(output_analizado),
        cantidad_por_categoria=noticias_por_categoria,
        modelo=modelo_llm,
    )

    print("\n" + "=" * 70)
    print("PIPELINE FINALIZADO CORRECTAMENTE")
    print("=" * 70)
    print(f"Archivo procesado: {output_procesado}")
    print(f"Archivo analizado: {output_analizado}")


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
        },

        {
            "type": "web_scraping",
            "config": {
                "scraper": scrap_laprensa_news_section,
                "output": f"{FILE_DIR}/../data/raw/noticias_laprensa.csv",
                "sources": [
                    {"url": "https://www.prensa.com/sociedad/",                   "pages": 1},
                    {"url": "https://www.prensa.com/comunicados/",                "pages": 1},
                    {"url": "https://www.prensa.com/judiciales/",                 "pages": 1},
                    {"url": "https://www.prensa.com/politica/",                   "pages": 1},
                    {"url": "https://www.prensa.com/economia/",                   "pages": 1},
                    {"url": "https://www.prensa.com/mundo/",                      "pages": 1},
                    {"url": "https://www.prensa.com/deportes/",                   "pages": 1},
                    {"url": "https://www.prensa.com/unidad-investigativa/",       "pages": 1},
                    {"url": "https://www.prensa.com/vivir/",                      "pages": 1}
                ]
            }
        }
    ]
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"

    run_pipeline(INGESTION_CONFIGS, OUTPUT)
    run_pipeline(
        ingestion_configs=INGESTION_CONFIGS,
        output_procesado=OUTPUT_PROCESADO,
        output_analizado=OUTPUT_ANALIZADO,
        noticias_por_categoria=NOTICIAS_POR_CATEGORIA,
        modelo_llm=MODELO_LLM,
    )


if __name__ == "__main__":
    main()
