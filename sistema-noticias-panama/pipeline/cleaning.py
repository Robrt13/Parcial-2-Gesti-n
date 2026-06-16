import pandas as pd, unicodedata, re
from pathlib import Path
from .commons import save_to_csv


def merge_csv_data(sources: list[str]) -> pd.DataFrame:
    return pd.concat([pd.read_csv(source) for source in sources])


def remove_accents(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")


def remove_special_characters(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s.,;:!?\"'()\-]", "", text)


def normalize_text(text: str) -> str:
    text = remove_accents(text)
    text = remove_special_characters(text)
    return text


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_data = df.copy()
    print(f"{'='*25}CLEANING PROCESS {'='*25}")

    cleaned_data = cleaned_data.dropna(subset=["titulo", "texto"])
    cleaned_data = cleaned_data.drop_duplicates(subset=["titulo"])
    cleaned_data["titulo"] = cleaned_data["titulo"].str.lower().str.strip().apply(normalize_text)
    cleaned_data["texto"] = cleaned_data["texto"].str.lower().str.strip().apply(normalize_text)
    cleaned_data["categoria_original"] = cleaned_data["categoria_original"].str.lower().str.strip().apply(normalize_text)
    #TODO: Normalización de fechas

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