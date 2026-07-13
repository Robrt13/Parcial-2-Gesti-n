from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


ML_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_DIR.parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "noticias_panama_analizadas.csv"
ARTIFACTS_DIR = ML_DIR / "artifacts"
METRICS_DIR = ML_DIR / "metrics"
MODEL_PATH = ARTIFACTS_DIR / "category_classifier.joblib"

TARGET_COLUMN = "categoria_original"
REQUIRED_COLUMNS = ["titulo", "texto", TARGET_COLUMN]
MIN_SAMPLES_PER_CATEGORY = 30
TEST_SIZE = 0.20
RANDOM_STATE = 42


def validate_dataset(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "El dataset no contiene las columnas requeridas: "
            + ", ".join(missing_columns)
        )


def build_model_text(df: pd.DataFrame) -> pd.Series:
    """Combina el título y el cuerpo de la noticia para la clasificación.

    El título se repite una vez para darle un poco más de peso temático sin
    alterar el texto original almacenado en el DataFrame.
    """
    title = df["titulo"].fillna("").astype(str).str.strip()
    body = df["texto"].fillna("").astype(str).str.strip()
    return (title + " " + title + " " + body).str.strip()


def filter_categories(
    df: pd.DataFrame,
    min_samples: int,
) -> tuple[pd.DataFrame, dict[str, int], dict[str, int]]:
    category_counts = df[TARGET_COLUMN].value_counts().sort_index()
    included = category_counts[category_counts >= min_samples]
    excluded = category_counts[category_counts < min_samples]

    filtered_df = df[df[TARGET_COLUMN].isin(included.index)].copy()

    if filtered_df[TARGET_COLUMN].nunique() < 2:
        raise ValueError(
            "Después de filtrar las categorías no quedan al menos dos clases "
            "para entrenar el modelo."
        )

    return filtered_df, included.to_dict(), excluded.to_dict()


def build_tfidf() -> TfidfVectorizer:
    return TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        max_features=50_000,
        sublinear_tf=True,
    )


def candidate_models() -> dict[str, Callable[[], object]]:
    return {
        "LinearSVC": lambda: LinearSVC(C=1.5, random_state=RANDOM_STATE),
        "LogisticRegression": lambda: LogisticRegression(
            max_iter=3_000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "ComplementNB": lambda: ComplementNB(),
    }


def build_pipeline(model: object) -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", build_tfidf()),
            ("classifier", model),
        ]
    )


def evaluate_candidates(
    x_train: pd.Series,
    x_test: pd.Series,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[pd.DataFrame, dict[str, Pipeline], dict[str, pd.Series]]:
    rows: list[dict] = []
    trained_models: dict[str, Pipeline] = {}
    predictions: dict[str, pd.Series] = {}

    for model_name, model_factory in candidate_models().items():
        pipeline = build_pipeline(model_factory())
        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)

        trained_models[model_name] = pipeline
        predictions[model_name] = pd.Series(y_pred, index=y_test.index)
        rows.append(
            {
                "modelo": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "f1_macro": f1_score(y_test, y_pred, average="macro"),
                "f1_weighted": f1_score(y_test, y_pred, average="weighted"),
            }
        )

    comparison = (
        pd.DataFrame(rows)
        .sort_values(by=["f1_macro", "accuracy"], ascending=False)
        .reset_index(drop=True)
    )
    return comparison, trained_models, predictions


def save_evaluation_outputs(
    comparison: pd.DataFrame,
    selected_model_name: str,
    y_test: pd.Series,
    y_pred: pd.Series,
    metadata: dict,
) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(METRICS_DIR / "model_comparison.csv", index=False)

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        zero_division=0,
    )
    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(METRICS_DIR / "classification_report.csv", index=True)

    labels = sorted(y_test.unique())
    matrix = confusion_matrix(y_test, y_pred, labels=labels)
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)
    matrix_df.index.name = "categoria_real"
    matrix_df.to_csv(METRICS_DIR / "confusion_matrix.csv", index=True)

    selected_row = comparison.loc[
        comparison["modelo"] == selected_model_name
    ].iloc[0]
    metrics_payload = {
        **metadata,
        "modelo_seleccionado": selected_model_name,
        "criterio_seleccion": "f1_macro",
        "metricas_holdout": {
            "accuracy": float(selected_row["accuracy"]),
            "f1_macro": float(selected_row["f1_macro"]),
            "f1_weighted": float(selected_row["f1_weighted"]),
        },
    }

    with open(METRICS_DIR / "model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, ensure_ascii=False, indent=4)


def train_and_save_model(
    input_path: Path,
    min_samples: int = MIN_SAMPLES_PER_CATEGORY,
) -> None:
    print(f"Leyendo dataset: {input_path}")
    df = pd.read_csv(input_path)
    validate_dataset(df)

    filtered_df, included_categories, excluded_categories = filter_categories(
        df,
        min_samples=min_samples,
    )

    x = build_model_text(filtered_df)
    y = filtered_df[TARGET_COLUMN].astype(str)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    comparison, trained_models, predictions = evaluate_candidates(
        x_train,
        x_test,
        y_train,
        y_test,
    )

    selected_model_name = comparison.iloc[0]["modelo"]
    selected_prediction = predictions[selected_model_name]

    metadata = {
        "fecha_entrenamiento_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": str(input_path),
        "registros_dataset_original": int(len(df)),
        "registros_utilizados": int(len(filtered_df)),
        "registros_entrenamiento": int(len(x_train)),
        "registros_prueba": int(len(x_test)),
        "porcentaje_prueba": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "minimo_registros_por_categoria": min_samples,
        "categorias_incluidas": included_categories,
        "categorias_excluidas": excluded_categories,
        "version_python": platform.python_version(),
        "version_sklearn": sklearn.__version__,
        "version_joblib": joblib.__version__,
    }

    save_evaluation_outputs(
        comparison=comparison,
        selected_model_name=selected_model_name,
        y_test=y_test,
        y_pred=selected_prediction,
        metadata=metadata,
    )

    # Se reentrena el mejor algoritmo con todos los registros elegibles para
    # que el artefacto final aproveche la mayor cantidad de información.
    final_pipeline = build_pipeline(candidate_models()[selected_model_name]())
    final_pipeline.fit(x, y)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "pipeline": final_pipeline,
        "metadata": {
            **metadata,
            "modelo_seleccionado": selected_model_name,
            "columnas_entrada": ["titulo", "texto"],
            "columna_salida": "categoria_ml",
        },
    }
    joblib.dump(artifact, MODEL_PATH)

    print("\nComparación de modelos:")
    print(comparison.to_string(index=False))
    print(f"\nModelo seleccionado: {selected_model_name}")
    print(f"Categorías incluidas: {list(included_categories)}")
    print(f"Categorías excluidas: {excluded_categories}")
    print(f"Modelo guardado en: {MODEL_PATH}")
    print(f"Métricas guardadas en: {METRICS_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entrena y evalúa el clasificador de categorías de noticias."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Ruta del CSV utilizado para entrenar el modelo.",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=MIN_SAMPLES_PER_CATEGORY,
        help="Cantidad mínima de noticias requerida para conservar una categoría.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {args.input}")
    if args.min_samples < 2:
        raise ValueError("--min-samples debe ser mayor o igual a 2.")

    train_and_save_model(
        input_path=args.input,
        min_samples=args.min_samples,
    )


if __name__ == "__main__":
    main()
