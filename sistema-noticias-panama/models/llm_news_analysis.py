import ollama, requests, re, json, pandas as pd
from pathlib import Path
from .alert_logic import calcular_alerta
from .commons import save_to_csv

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


def normalizar_sentimiento(sentimiento: str) -> str:
    sentimiento = sentimiento.lower().strip()

    if "positivo" in sentimiento:
        return "positivo"

    if "negativo" in sentimiento:
        return "negativo"

    return "neutral"


def normalizar_categoria(categoria: str, categorias_permitidas: list[str]) -> str:
    REEMPLAZOS = {
        "nacional": "nacionales",
        "internacional": "mundo",
        "internacionales": "mundo",
        "deporte": "deportes",
        "contenido exclusivo": "contenido-exclusivo",
        "contenido_exclusivo": "contenido-exclusivo",
        "tecnología": "tecnologia",
        "educación": "educacion",
        "economía": "economia",
        "política": "politica",
    }

    categoria = categoria.lower().strip()
    categoria = REEMPLAZOS.get(categoria, categoria)

    return categoria if categoria in categorias_permitidas else "otro"


def extraer_json(texto: str) -> dict:
    texto = texto.strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    texto = re.sub(r"```json", "", texto, flags=re.IGNORECASE)
    texto = texto.replace("```", "").strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    inicio = texto.find("{")
    fin = texto.rfind("}")

    if inicio != -1 and fin != -1 and fin > inicio:
        posible_json = texto[inicio:fin + 1]
        return json.loads(posible_json)


def verificar_modelo_instalado(modelo: str) -> None:
    if modelo.split(':')[0] not in [m.model.split(':')[0] for m in ollama.list().models]:
        print(f"{'='*25} INSTALLING: {modelo} {'='*25}")
        ollama.pull(modelo)


def llamar_ollama(prompt: str, modelo: str) -> str:
    response = ollama.generate(
        model=modelo,
        prompt=prompt,
        stream=False,
        format="json",
        think=False,
        options={
            "temperature": 0,
            "num_predict": 300,
        }
    )
    return response["response"]


def analizar_noticia_con_llm(titulo: str, texto: str, modelo: str) -> dict:
    prompt = f"""
Eres un sistema de analisis de noticias de Panama.
Responde unicamente con JSON valido. No escribas explicaciones fuera del JSON.

Devuelve exactamente esta estructura:
{{
  "sentimiento": "positivo, negativo o neutral",
  "categoria_predicha": "{", ".join(CATEGORIAS_PERMITIDAS[:-1])} o {CATEGORIAS_PERMITIDAS[-1]}"
}}

Reglas:
- El sentimiento solo puede ser: positivo, negativo o neutral.
- La categoria_predicha debe ser una de estas: {", ".join(CATEGORIAS_PERMITIDAS[:-1])} o {CATEGORIAS_PERMITIDAS[-1]}

Titulo:
{titulo}

Texto:
{texto}
"""
    respuesta = llamar_ollama(prompt=prompt, modelo=modelo)
    data = extraer_json(respuesta)

    return {
        "sentimiento": normalizar_sentimiento(data.get("sentimiento", "neutral")),
        "categoria_predicha": normalizar_categoria(data.get("categoria_predicha", "otro"), CATEGORIAS_PERMITIDAS),
    }


def muestrear(df: pd.DataFrame, cantidad: int, ordenar_por: list[str], agrupar_por: list[str]) -> pd.DataFrame:
    muestra = df.copy()
    muestra = muestra.sort_values(by=ordenar_por, ascending=False, na_position="last")

    muestra = (
        muestra
            .groupby(agrupar_por, group_keys=False)
            .head(cantidad)
            .reset_index(drop=True)
    )

    return muestra


def analizar_noticias(df: pd.DataFrame, cantidad_por_categoria_por_medio: int, modelo: str) -> pd.DataFrame:
    verificar_modelo_instalado(modelo)
    
    print(f"{'='*25} SAMPLING {'='*25}")
    muestra = muestrear(df, cantidad_por_categoria_por_medio, ["fecha"], ["medio", "categoria_original"]).copy()
    print(f"{'='*25} NEWS TO ANALYZE: {len(muestra)} {'='*25}")

    print(f"{'='*25} ANALYSIS PROCESS {'='*25}")
    muestra["analisis"] = muestra.apply(
        lambda x: analizar_noticia_con_llm(x["titulo"], x["texto"], modelo),
        axis=1
    )
    muestra["sentimiento"] = muestra["analisis"].apply(lambda x: x["sentimiento"])
    muestra["categoria_predicha"] = muestra["analisis"].apply(lambda x: x["categoria_predicha"])
    muestra = muestra.drop(columns=["analisis"])

    muestra["alerta"] = muestra.apply(
        lambda x: calcular_alerta(x["palabras_criticas"], x["sentimiento"]),
        axis=1
    )
    muestra["es_alerta"] = muestra["alerta"].apply(lambda x: x[0])
    muestra["nivel_alerta"] = muestra["alerta"].apply(lambda x: x[1])
    muestra = muestra.drop(columns=["alerta"])

    return muestra


def main():
    FILE_DIR = Path(__file__).parent
    INPUT = f"{FILE_DIR}/../data/processed/noticias_panama_procesadas.csv"
    NOTICIAS_POR_CATEGORIA_POR_MEDIO = 4
    MODELO = "qwen3.5:0.8b" # Otros: qwen3.5:0.8b qwen3.5:2b qwen3.5:4b
    OUTPUT = f"{FILE_DIR}/../data/processed/noticias_panama_analizadas.csv"

    analyzed_df = analizar_noticias(pd.read_csv(INPUT), cantidad_por_categoria_por_medio=NOTICIAS_POR_CATEGORIA_POR_MEDIO, modelo=MODELO)
    save_to_csv(analyzed_df, OUTPUT)


if __name__ == "__main__":
    main()