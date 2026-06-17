import pandas as pd

NIVELES_VALIDOS = {"sin alerta", "baja", "media", "alta"}
SENTIMIENTOS_VALIDOS = {"positivo", "negativo", "neutral"}


def normalizar_sentimiento(sentimiento: str) -> str:
    sentimiento = sentimiento.strip().lower()

    if sentimiento not in SENTIMIENTOS_VALIDOS:
        return "neutral"

    return sentimiento


def calcular_alerta(palabras_criticas: int, sentimiento: str) -> tuple[bool, str]:
    ALERTAS = {
        0: {
            True: "sin alerta",
            False: "sin alerta"
        },
        1: {
            True: "baja",
            False: "sin alerta"
        },
        2: {
            True: "media",
            False: "baja"
        },
        3: {
            True: "alta",
            False: "media"
        }
    }
    
    rango_palabras_criticas = palabras_criticas if palabras_criticas < 3 else 3
    sentimiento_negativo = sentimiento.strip().lower() == "negativo"
    nivel_alerta = ALERTAS[palabras_criticas][sentimiento_negativo]
    return nivel_alerta != "sin alerta", nivel_alerta


def aplicar_alertas_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "palabras_criticas" not in df.columns:
        raise ValueError("El DataFrame debe tener la columna 'palabras_criticas'.")

    if "sentimiento" not in df.columns:
        raise ValueError("El DataFrame debe tener la columna 'sentimiento'.")

    resultados = df.apply(
        lambda row: calcular_alerta(row["palabras_criticas"], row["sentimiento"]),
        axis=1
    )

    df["es_alerta"] = resultados.apply(lambda x: x[0])
    df["nivel_alerta"] = resultados.apply(lambda x: x[1])
    
    return df