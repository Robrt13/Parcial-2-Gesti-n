import re
import unicodedata
import pandas as pd
from pathlib import Path


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^a-zA-Z0-9\s.,;:!?\"'()\-]", "", text)
    return text

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df.dropna(subset=["titulo", "texto"], inplace=True)

    df["titulo"] = df["titulo"].str.lower().str.strip().apply(normalize_text)
    df["texto"] = df["texto"].str.lower().str.strip().apply(normalize_text)
    df["categoria_original"] = df["categoria_original"].str.lower().str.strip().apply(normalize_text)

    #TODO: Normalización de fechas

    return df

if __name__ == "__main__":
    sources = [
        f"{Path(__file__).parent}/../data/raw/noticias_tvn.csv"
    ]

    processed_data = []
    for source in sources:
        print(f"Processing: {source}")
        processed_data.append(clean_data(pd.read_csv(source)))

    df = pd.concat(processed_data, ignore_index=True)
    df.drop_duplicates(subset=["titulo"], inplace=True)
    df.to_csv(f"{Path(__file__).parent}/../data/processed/noticias_panama_procesadas.csv", index=False)