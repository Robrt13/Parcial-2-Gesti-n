import pandas as pd, unicodedata, re
from pathlib import Path
from .commons import save_to_csv

REPLACEMENTS = {
    "nacional": "nacionales",
    "internacional": "mundo",
    "internacionales": "mundo",
    "deporte": "deportes",
    "contenido exclusivo": "contenido-exclusivo",
    "contenido_exclusivo": "contenido-exclusivo"
}

CATEGORIAS_PERMITIDAS = [
    "nacionales",
    "mundo",
    "deportes",
    "entretenimiento",
    "contenido-exclusivo",
    "politica",
    "economia",
    "seguridad",
    "salud",
    "educacion",
    "ambiente",
    "tecnologia",
    "otro",
]


def merge_csv_data(sources: list[str]) -> pd.DataFrame:
    return pd.concat([pd.read_csv(source) for source in sources])


def remove_accents(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")


def remove_special_characters(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s.,;:!?\"'()\-]", "", text)


def normalize_text(text: str) -> str:
    normalized_text = text.lower()
    normalized_text = normalized_text.strip()
    normalized_text = remove_accents(normalized_text)
    normalized_text = remove_special_characters(normalized_text)
    return normalized_text


def normalize_category(category: str, allowed_categories: list[str]) -> str:
    normalized_category = normalize_text(category)
    normalized_category = REPLACEMENTS.get(normalized_category, normalized_category)
    return normalized_category if normalized_category in allowed_categories else "otro"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_data = df.copy()
    print(f"{'='*25} CLEANING PROCESS {'='*25}")

    cleaned_data = cleaned_data.dropna(subset=["titulo", "texto"])
    cleaned_data = cleaned_data.drop_duplicates(subset=["titulo"])
    cleaned_data["categoria_original"] = cleaned_data["categoria_original"].apply(lambda x: normalize_category(x, CATEGORIAS_PERMITIDAS))
    
    return cleaned_data


def main():
    FILE_DIR = Path(__file__).parent
    SOURCES = [
        f"{FILE_DIR}/../data/raw/noticias_tvn.csv",
        f"{FILE_DIR}/../data/raw/noticias_telemetro.csv",
        f"{FILE_DIR}/../data/raw/noticias_laprensa.csv"
    ]
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"
    
    merged_data = merge_csv_data(SOURCES)
    cleaned_data = clean_data(merged_data)
    save_to_csv(cleaned_data, OUTPUT)


if __name__ == "__main__":
    main()