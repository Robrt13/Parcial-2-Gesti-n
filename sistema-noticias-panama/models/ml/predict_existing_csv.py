from pathlib import Path

import pandas as pd

from .category_classifier import predecir_categorias_ml


# Ruta principal del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# CSV que ya contiene el análisis del LLM
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "noticias_panama_analizadas.csv"
)

# Se crea un archivo nuevo para no modificar el CSV original
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "noticias_panama_analizadas_ml.csv"
)


def main() -> None:
    print("=" * 60)
    print("PREDICCIÓN DE CATEGORÍAS MEDIANTE MACHINE LEARNING")
    print("=" * 60)

    # Verificar que exista el CSV
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo:\n{INPUT_PATH}"
        )

    print(f"Leyendo dataset: {INPUT_PATH.name}")

    # Cargar el CSV que ya fue analizado por el LLM
    df = pd.read_csv(INPUT_PATH)

    print(f"Noticias encontradas: {len(df)}")

    # Ejecutar solamente el modelo de Machine Learning
    result = predecir_categorias_ml(df)

    # Guardar el resultado
    result.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nPredicción finalizada correctamente.")
    print("Nueva columna generada: categoria_ml")
    print(f"Archivo guardado en:\n{OUTPUT_PATH}")

    print("\nDistribución de las predicciones:")

    print(
        result["categoria_ml"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()