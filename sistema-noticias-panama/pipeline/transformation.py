import pandas as pd, spacy, json
from pathlib import Path
from .commons import save_to_csv

LEMMATIZABLE = ["texto"]

COLUMNS = [
    {"name": "cantidad_palabras",   "value": 0},
    {"name": "categoria_predicha",  "value": ""},
    {"name": "criticidad",          "value": 0},
    {"name": "sentimiento",         "value": 0.0},
    {"name": "es_alerta",           "value": False},
    {"name": "nivel_alerta",        "value": 0},
]

CRITICAL_WORDS_FILE = f"{Path(__file__).parent}/critical_words.json"


def initialize_columns(df: pd.DataFrame, columns: list[dict]) -> pd.DataFrame:
    transformed_df = df.copy()
    for column in columns:
        transformed_df[column["name"]] = column["value"]
    return transformed_df


def lemmatize_text(df: pd.DataFrame, nlp, columns: list[str], batch_size: int = 64, n_process: int = 1) -> pd.DataFrame:
    transformed_df = df.copy()

    for column in columns:
        docs = nlp.pipe(transformed_df[column], batch_size=batch_size, n_process=n_process)
        transformed_df[f"{column}_lematizado"] = [" ".join(tok.lemma_ for tok in doc) for doc in docs]

    return transformed_df


def build_criticality_index(critical_words: list[dict]) -> list[tuple[set, int]]:
    index = []
    for concept in critical_words:
        concept_data = next(iter(concept.values()))
        index.append((set(concept_data["lemmas"]), concept_data["weight"]))
    return index


def calculate_criticality(text_lemmas: set, criticality_index: list[tuple[set, int]]) -> int:
    return sum(weight for lemmas, weight in criticality_index if text_lemmas & lemmas)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(f"{'='*25} TRANSFORMATION PROCESS {'='*25}")
    nlp = spacy.load("es_core_news_sm")
    
    with open(CRITICAL_WORDS_FILE, "r", encoding="utf-8") as file:
        critical_words = json.load(file)

    transformed_df = (
        df.copy()
        .pipe(initialize_columns, columns=COLUMNS)
        .pipe(lemmatize_text, nlp=nlp, columns=LEMMATIZABLE)
    )

    criticality_index = build_criticality_index(critical_words)
    transformed_df["criticidad"] = (
        transformed_df["texto_lematizado"].str.split()
        .apply(lambda lemmas: calculate_criticality(set(lemmas), criticality_index))
    )

    transformed_df["cantidad_palabras"] = transformed_df["texto"].str.split().str.len()

    return transformed_df


def main():
    FILE_DIR = Path(__file__).parent
    SOURCE = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"

    transformed_df = transform_data(pd.read_csv(SOURCE))
    save_to_csv(transformed_df, OUTPUT)


if __name__ == "__main__":
    main()