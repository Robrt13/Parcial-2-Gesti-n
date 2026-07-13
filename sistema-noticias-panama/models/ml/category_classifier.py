from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


ML_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = ML_DIR / "artifacts" / "category_classifier.joblib"
REQUIRED_COLUMNS = ["titulo", "texto"]


def build_model_text(df: pd.DataFrame) -> pd.Series:
    title = df["titulo"].fillna("").astype(str).str.strip()
    body = df["texto"].fillna("").astype(str).str.strip()
    return (title + " " + title + " " + body).str.strip()


def load_category_model(model_path: Path = DEFAULT_MODEL_PATH) -> dict:
    if not model_path.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo entrenado en {model_path}. "
            "Ejecuta primero: python -m models.ml.train_category_model"
        )

    artifact = joblib.load(model_path)
    if not isinstance(artifact, dict) or "pipeline" not in artifact:
        raise ValueError(
            "El archivo del modelo no tiene la estructura esperada. "
            "Vuelve a entrenarlo con train_category_model.py."
        )
    return artifact


def predecir_categorias_ml(
    df: pd.DataFrame,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> pd.DataFrame:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "No se puede ejecutar la predicción de ML. Faltan las columnas: "
            + ", ".join(missing_columns)
        )

    result = df.copy()
    artifact = load_category_model(model_path)
    pipeline = artifact["pipeline"]

    model_text = build_model_text(result)
    result["categoria_ml"] = pipeline.predict(model_text)
    return result
