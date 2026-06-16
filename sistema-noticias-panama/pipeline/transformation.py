import pandas as pd, spacy
from pathlib import Path
from .commons import save_to_csv

LEMMATIZABLE = ["texto"]

COLUMNS = [
    {"name": "categoria_predicha",  "value": ""},
    {"name": "palabras_criticas",   "value": 0},
    {"name": "sentimiento",         "value": ""},
    {"name": "es_alerta",           "value": False},
    {"name": "nivel_alerta",        "value": ""},
]

CRITICAL_WORDS = [
    "protesta", "cierre de via", "homicidio",
    "dengue", "accidente", "corrupcion", "emergencia",
    "crisis", "inundacion", "violencia"
]


def initialize_columns(df: pd.DataFrame, columns: list[dict]) -> pd.DataFrame:
    transformed_df = df.copy()
    for column in columns:
        transformed_df[column["name"]] = column["value"]
    return transformed_df


def count_words(df: pd.DataFrame, words: list[str]) -> pd.DataFrame:
    transformed_df = df.copy()
    transformed_df["palabras_criticas"] = transformed_df["texto"].apply(lambda x: sum([1 for word in x.split() if word in words]))
    return transformed_df


def lemmatize_text(df: pd.DataFrame, nlp, columns: list[str]) -> pd.DataFrame:
    transformed_df = df.copy()
    for column in columns:
        transformed_df[column] = transformed_df[column].apply(lambda x: " ".join([token.lemma_ for token in nlp(x)]))
    return transformed_df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(f"{'='*25}TRANSFORMATION PROCESS {'='*25}")
    nlp = spacy.load("es_core_news_sm")
    transformed_df = (
        df.copy()
        .pipe(initialize_columns, columns=COLUMNS)
        .pipe(lemmatize_text, nlp=nlp, columns=LEMMATIZABLE)
        .pipe(count_words, words=CRITICAL_WORDS)
    )

    return transformed_df


def main():
    FILE_DIR = Path(__file__).parent
    SOURCE = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"

    transformed_df = transform_data(pd.read_csv(SOURCE))
    save_to_csv(transformed_df, OUTPUT)


if __name__ == "__main__":
    main()