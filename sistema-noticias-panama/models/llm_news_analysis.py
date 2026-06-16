import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests

from models.alert_logic import calcular_alerta


# ============================================================
# CONFIGURACION PRINCIPAL
# ============================================================

# Cambia esta variable si quieres analizar mas o menos noticias por categoria.
# En tu caso lo dejaste en 4 para evitar limites de API.
NOTICIAS_POR_CATEGORIA = 4

# En local no necesitas esperar por cuota como en Gemini.
# Puedes dejarlo en 0. Si tu PC se pone lenta, usa 2 o 3.
TIEMPO_ESPERA_SEGUNDOS = 0

# Modelo local de Ollama.
# Puedes probar:
# - qwen3.5:0.8b  -> mas liviano y rapido
# - qwen3.5:2b    -> mejor calidad, todavia liviano
# - qwen3.5:4b    -> mejor calidad, mas pesado
MODELO_LOCAL = "qwen3.5:0.8b"

# Servidor local de Ollama.
OLLAMA_URL = "http://localhost:11434/api/generate"

# Columna que se usara para agrupar las noticias.
COLUMNA_CATEGORIA = "categoria_original"
COLUMNA_MEDIO = "medio"

# Rutas por defecto.
INPUT_DEFAULT = "data/processed/noticias_panama_procesadas.csv"
OUTPUT_DEFAULT = "data/processed/noticias_panama_analizadas.csv"


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


def limpiar_texto_para_prompt(texto: str, max_caracteres: int = 2500) -> str:
    """
    Recorta el texto para que el modelo local responda mas rapido.
    """
    if pd.isna(texto):
        return ""

    texto = str(texto).strip()
    texto = " ".join(texto.split())

    if len(texto) > max_caracteres:
        texto = texto[:max_caracteres] + "..."

    return texto


def normalizar_sentimiento(sentimiento: str) -> str:
    sentimiento = str(sentimiento).lower().strip()

    if "positivo" in sentimiento:
        return "positivo"

    if "negativo" in sentimiento:
        return "negativo"

    return "neutral"


def normalizar_categoria(categoria: str) -> str:
    categoria = str(categoria).lower().strip()

    reemplazos = {
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

    categoria = reemplazos.get(categoria, categoria)

    if categoria not in CATEGORIAS_PERMITIDAS:
        return "otro"

    return categoria


def extraer_json(texto: str) -> dict:
    """
    Los modelos locales a veces devuelven texto antes o despues del JSON.
    Esta funcion intenta extraer el primer bloque JSON valido.
    """
    if not texto:
        raise ValueError("Respuesta vacia del modelo local.")

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

    raise ValueError("No se pudo extraer JSON valido de la respuesta del modelo local.")


def llamar_ollama(prompt: str, modelo: str = MODELO_LOCAL) -> str:
    """
    Llama al modelo local usando Ollama.

    Requisitos:
    1. Tener Ollama instalado.
    2. Tener el modelo descargado:
       ollama pull qwen3.5:0.8b
    3. Tener Ollama corriendo en localhost:11434.
    """
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 300,
        },
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "")


def analizar_noticia_con_llm(titulo: str, texto: str, modelo: str = MODELO_LOCAL) -> dict:
    """
    Analiza una noticia usando Qwen local mediante Ollama.
    """
    titulo = limpiar_texto_para_prompt(titulo, max_caracteres=300)
    texto = limpiar_texto_para_prompt(texto, max_caracteres=2500)

    prompt = f"""
Eres un sistema de analisis de noticias de Panama.
Responde unicamente con JSON valido. No escribas explicaciones fuera del JSON.

Devuelve exactamente esta estructura:

{{
  "resumen_llm": "resumen breve de maximo 2 oraciones",
  "sentimiento": "positivo, negativo o neutral",
  "justificacion_sentimiento": "explicacion breve del sentimiento",
  "categoria_predicha": "una categoria"
}}

Reglas:
- El resumen debe ser corto y claro.
- El sentimiento solo puede ser: positivo, negativo o neutral.
- La categoria_predicha debe ser una de estas:
  nacionales, mundo, deportes, entretenimiento, contenido-exclusivo,
  politica, economia, seguridad, salud, educacion, ambiente, tecnologia, otro.
- No calcules palabras criticas.
- No calcules si es alerta.

Titulo:
{titulo}

Texto:
{texto}
"""

    respuesta = llamar_ollama(prompt=prompt, modelo=modelo)
    data = extraer_json(respuesta)

    return {
        "resumen_llm": data.get("resumen_llm", ""),
        "sentimiento": normalizar_sentimiento(data.get("sentimiento", "neutral")),
        "justificacion_sentimiento": data.get("justificacion_sentimiento", ""),
        "categoria_predicha": normalizar_categoria(data.get("categoria_predicha", "otro")),
    }


def seleccionar_noticias_por_categoria_por_medio(
    df: pd.DataFrame,
    columna_categoria: str = COLUMNA_CATEGORIA,
    columna_medio: str = COLUMNA_MEDIO,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
) -> pd.DataFrame:
    """
    Selecciona las N noticias mas nuevas por cada categoria.
    """
    if columna_categoria not in df.columns:
        raise ValueError(f"No existe la columna de categoria: {columna_categoria}")

    if "fecha" not in df.columns:
        raise ValueError("No existe la columna 'fecha'. No se pueden seleccionar las noticias mas nuevas.")

    df = df.copy()
    df[columna_categoria] = df[columna_categoria].fillna("sin_categoria")
    df["fecha_orden"] = pd.to_datetime(df["fecha"], errors="coerce")

    df = df.sort_values(
        by=["fecha_orden"],
        ascending=False,
        na_position="last",
    )

    muestra = (
        df.groupby([columna_categoria, columna_medio], group_keys=False)
        .head(cantidad_por_categoria)
        .reset_index(drop=True)
    )

    return muestra.drop(columns=["fecha_orden"])


def obtener_valor_palabras_criticas(row: pd.Series) -> int:
    """
    Usa las palabras criticas ya calculadas por tu pipeline.
    """
    if "cantidad_palabras_criticas" in row and not pd.isna(row["cantidad_palabras_criticas"]):
        try:
            return int(row["cantidad_palabras_criticas"])
        except (ValueError, TypeError):
            pass

    if "palabras_criticas" not in row or pd.isna(row["palabras_criticas"]):
        return 0

    valor = row["palabras_criticas"]

    if isinstance(valor, (int, float)):
        return int(valor)

    valor = str(valor).strip()

    if not valor or valor.lower() in ["nan", "none", "[]"]:
        return 0

    try:
        parsed = json.loads(valor.replace("'", '"'))
        if isinstance(parsed, list):
            return len(parsed)
    except Exception:
        pass

    if "," in valor:
        return len([p.strip() for p in valor.split(",") if p.strip()])

    return 1


def analizar_dataframe(
    df: pd.DataFrame,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
    modelo: str = MODELO_LOCAL,
    tiempo_espera: int = TIEMPO_ESPERA_SEGUNDOS,
) -> pd.DataFrame:
    muestra = seleccionar_noticias_por_categoria_por_medio(
        df=df,
        columna_categoria=COLUMNA_CATEGORIA,
        columna_medio=COLUMNA_MEDIO,
        cantidad_por_categoria=cantidad_por_categoria,
    )

    resultados = []
    total = len(muestra)

    for i, (_, row) in enumerate(muestra.iterrows(), start=1):
        titulo = row.get("titulo", "")
        texto = row.get("texto", "")

        print(f"[{i}/{total}] Analizando localmente con {modelo}: {str(titulo)[:80]}")

        try:
            analisis = analizar_noticia_con_llm(
                titulo=titulo,
                texto=texto,
                modelo=modelo,
            )
        except Exception as error:
            analisis = {
                "resumen_llm": "",
                "sentimiento": "neutral",
                "justificacion_sentimiento": f"Error en modelo local: {error}",
                "categoria_predicha": "otro",
            }

        cantidad_criticas = obtener_valor_palabras_criticas(row)

        es_alerta, nivel_alerta = calcular_alerta(
            palabras_criticas=cantidad_criticas,
            sentimiento=analisis["sentimiento"],
        )

        nueva_fila = row.to_dict()
        nueva_fila["resumen_llm"] = analisis["resumen_llm"]
        nueva_fila["sentimiento"] = analisis["sentimiento"]
        nueva_fila["justificacion_sentimiento"] = analisis["justificacion_sentimiento"]
        nueva_fila["categoria_predicha"] = analisis["categoria_predicha"]
        nueva_fila["cantidad_palabras_criticas"] = cantidad_criticas
        nueva_fila["es_alerta"] = es_alerta
        nueva_fila["nivel_alerta"] = nivel_alerta
        nueva_fila["modelo_llm"] = modelo

        resultados.append(nueva_fila)

        if tiempo_espera > 0 and i < total:
            time.sleep(tiempo_espera)

    return pd.DataFrame(resultados)


def analizar_csv(
    input_path: str | Path = INPUT_DEFAULT,
    output_path: str | Path = OUTPUT_DEFAULT,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
    modelo: str = MODELO_LOCAL,
    tiempo_espera: int = TIEMPO_ESPERA_SEGUNDOS,
) -> pd.DataFrame:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

    print(f"Leyendo archivo: {input_path}")
    df = pd.read_csv(input_path)

    print(f"Analizando {cantidad_por_categoria} noticias por categoria con modelo local: {modelo}")
    df_analizado = analizar_dataframe(
        df=df,
        cantidad_por_categoria=cantidad_por_categoria,
        modelo=modelo,
        tiempo_espera=tiempo_espera,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_analizado.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Archivo analizado guardado en: {output_path}")

    return df_analizado


def main():
    parser = argparse.ArgumentParser(
        description="Analiza noticias con Qwen local mediante Ollama."
    )

    parser.add_argument("--input", default=INPUT_DEFAULT)
    parser.add_argument("--output", default=OUTPUT_DEFAULT)
    parser.add_argument("--per-category", type=int, default=NOTICIAS_POR_CATEGORIA)
    parser.add_argument("--model", default=MODELO_LOCAL)
    parser.add_argument("--sleep", type=int, default=TIEMPO_ESPERA_SEGUNDOS)

    args = parser.parse_args()

    analizar_csv(
        input_path=args.input,
        output_path=args.output,
        cantidad_por_categoria=args.per_category,
        modelo=args.model,
        tiempo_espera=args.sleep,
    )


if __name__ == "__main__":
    main()
