"""
models/alert_logic.py

Este archivo NO llama a ningun LLM.
Solo usa Python para calcular si una noticia es alerta y su nivel,
usando el sentimiento generado por el LLM y la cantidad de palabras criticas
que ya vienen en el CSV desde el pipeline.
"""

from __future__ import annotations

import pandas as pd


NIVELES_VALIDOS = {"sin alerta", "baja", "media", "alta"}
SENTIMIENTOS_VALIDOS = {"positivo", "negativo", "neutral"}


def normalizar_sentimiento(sentimiento: str | None) -> str:
    """
    Normaliza el sentimiento para evitar errores por mayusculas,
    espacios o valores vacios.
    """
    if sentimiento is None or pd.isna(sentimiento):
        return "neutral"

    sentimiento = str(sentimiento).strip().lower()

    if sentimiento not in SENTIMIENTOS_VALIDOS:
        return "neutral"

    return sentimiento


def calcular_alerta(palabras_criticas: int | float | str, sentimiento: str | None) -> tuple[bool, str]:
    """
    Calcula si una noticia es alerta y el nivel de alerta.

    Reglas propuestas:
    - 0 palabras criticas: sin alerta
    - 1 palabra critica + sentimiento negativo: alerta baja
    - 1 palabra critica + sentimiento positivo/neutral: sin alerta
    - 2 palabras criticas + sentimiento negativo: alerta media
    - 2 palabras criticas + sentimiento positivo/neutral: alerta baja
    - 3 o mas palabras criticas + sentimiento negativo: alerta alta
    - 3 o mas palabras criticas + sentimiento positivo/neutral: alerta media
    """
    sentimiento = normalizar_sentimiento(sentimiento)

    try:
        cantidad = int(palabras_criticas)
    except (ValueError, TypeError):
        cantidad = 0

    if cantidad <= 0:
        return False, "sin alerta"

    if cantidad == 1:
        if sentimiento == "negativo":
            return True, "baja"
        return False, "sin alerta"

    if cantidad == 2:
        if sentimiento == "negativo":
            return True, "media"
        return True, "baja"

    if cantidad >= 3:
        if sentimiento == "negativo":
            return True, "alta"
        return True, "media"

    return False, "sin alerta"


def aplicar_alertas_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica la logica de alerta a todo el DataFrame.

    El DataFrame debe tener estas columnas:
    - palabras_criticas
    - sentimiento
    """
    df = df.copy()

    if "palabras_criticas" not in df.columns:
        raise ValueError("El DataFrame debe tener la columna 'palabras_criticas'.")

    if "sentimiento" not in df.columns:
        raise ValueError("El DataFrame debe tener la columna 'sentimiento'.")

    resultados = df.apply(
        lambda row: calcular_alerta(row["palabras_criticas"], row["sentimiento"]),
        axis=1,
    )

    df["es_alerta"] = resultados.apply(lambda x: x[0])
    df["nivel_alerta"] = resultados.apply(lambda x: x[1])

    return df
