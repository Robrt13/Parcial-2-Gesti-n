import pandas as pd


def calcular_alerta(palabras_criticas: int, sentimiento: str) -> tuple[bool, str]:
    ALERTAS = {
        True: {
            0: "sin alerta",
            1: "baja",
            2: "media",
            3: "alta"
        },
        False: {
            0: "sin alerta",
            1: "sin alerta",
            2: "baja",
            3: "media"
        }
    }
    
    rango_palabras_criticas = palabras_criticas if palabras_criticas < 3 else 3
    sentimiento_negativo = sentimiento.strip().lower() == "negativo"
    nivel_alerta = ALERTAS[sentimiento_negativo][rango_palabras_criticas]
    return nivel_alerta != "sin alerta", nivel_alerta


def aplicar_alertas_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    alertas = df.copy().apply(
        lambda row: calcular_alerta(row["palabras_criticas"], row["sentimiento"]),
        axis=1
    )

    df["es_alerta"] = alertas.apply(lambda x: x[0])
    df["nivel_alerta"] = alertas.apply(lambda x: x[1])
    
    return df