import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai

from models.alert_logic import calcular_alerta


# ============================================================
# CONFIGURACION PRINCIPAL
# ============================================================

# Cambia esta variable si quieres analizar mas o menos noticias por categoria.
# Para tu caso, debe quedar en 5.
NOTICIAS_POR_CATEGORIA = 5

# Tiempo de espera entre llamadas al LLM.
# Gemini free tier puede limitar las llamadas por minuto.
# Si te vuelve a dar error 429, sube este valor a 25 o 30.
TIEMPO_ESPERA_SEGUNDOS = 25

# Modelo Gemini a utilizar.
MODELO_LLM = "gemini-2.5-flash"

# Columna que se usara para agrupar las noticias.
# En tu CSV normalmente es "categoria_original".
COLUMNA_CATEGORIA = "categoria_original"

# Rutas por defecto.
INPUT_DEFAULT = "data/processed/noticias_panama_procesadas.csv"
OUTPUT_DEFAULT = "data/processed/noticias_panama_analizadas.csv"


# Categorias permitidas para categoria_predicha.
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


def crear_cliente_gemini():
    """
    Crea el cliente de Gemini usando la API Key del archivo .env.

    El archivo .env debe estar en la raiz del proyecto y debe tener:
    GEMINI_API_KEY=tu_api_key
    """
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontro GEMINI_API_KEY. "
            "Verifica que exista un archivo .env en la raiz del proyecto."
        )

    return genai.Client(api_key=api_key)


def limpiar_texto_para_prompt(texto: str, max_caracteres: int = 2500) -> str:
    """
    Recorta el texto para reducir costo y evitar prompts muy largos.
    """
    if pd.isna(texto):
        return ""

    texto = str(texto).strip()
    texto = " ".join(texto.split())

    if len(texto) > max_caracteres:
        texto = texto[:max_caracteres] + "..."

    return texto


def normalizar_sentimiento(sentimiento: str) -> str:
    """
    Normaliza el sentimiento para evitar valores raros.
    """
    sentimiento = str(sentimiento).lower().strip()

    if "positivo" in sentimiento:
        return "positivo"

    if "negativo" in sentimiento:
        return "negativo"

    return "neutral"


def normalizar_categoria(categoria: str) -> str:
    """
    Normaliza la categoria predicha por Gemini.
    """
    categoria = str(categoria).lower().strip()

    reemplazos = {
        "nacional": "nacionales",
        "internacional": "mundo",
        "internacionales": "mundo",
        "deporte": "deportes",
        "entretenimiento y farandula": "entretenimiento",
        "contenido exclusivo": "contenido-exclusivo",
        "contenido_exclusivo": "contenido-exclusivo",
        "tecnologia": "tecnologia",
        "tecnología": "tecnologia",
        "educación": "educacion",
        "economía": "economia",
        "política": "politica",
    }

    categoria = reemplazos.get(categoria, categoria)

    if categoria not in CATEGORIAS_PERMITIDAS:
        return "otro"

    return categoria


def analizar_noticia_con_llm(client, titulo: str, texto: str, modelo: str = MODELO_LLM) -> dict:
    """
    Llama a Gemini para analizar una noticia.

    Gemini debe devolver:
    - resumen_llm
    - sentimiento
    - justificacion_sentimiento
    - categoria_predicha

    Importante:
    - Gemini NO calcula palabras criticas.
    - Gemini NO calcula nivel de alerta.
    Eso lo hace Python con alert_logic.py.
    """
    titulo = limpiar_texto_para_prompt(titulo, max_caracteres=300)
    texto = limpiar_texto_para_prompt(texto, max_caracteres=2500)

    prompt = f"""
Analiza la siguiente noticia de Panama.

Debes devolver UNICAMENTE un JSON valido con esta estructura exacta:

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
- No agregues texto fuera del JSON.

Titulo:
{titulo}

Texto:
{texto}
"""

    response = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
        },
    )

    contenido = response.text

    try:
        data = json.loads(contenido)
    except json.JSONDecodeError:
        return {
            "resumen_llm": "",
            "sentimiento": "neutral",
            "justificacion_sentimiento": "No se pudo interpretar la respuesta JSON del LLM.",
            "categoria_predicha": "otro",
        }

    return {
        "resumen_llm": data.get("resumen_llm", ""),
        "sentimiento": normalizar_sentimiento(data.get("sentimiento", "neutral")),
        "justificacion_sentimiento": data.get("justificacion_sentimiento", ""),
        "categoria_predicha": normalizar_categoria(data.get("categoria_predicha", "otro")),
    }


def seleccionar_noticias_por_categoria(
    df: pd.DataFrame,
    columna_categoria: str = COLUMNA_CATEGORIA,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
) -> pd.DataFrame:
    """
    Selecciona las N noticias mas nuevas por cada categoria.

    Requisito:
    - El CSV debe tener una columna llamada "fecha".
    - La fecha debe estar idealmente en formato YYYY-MM-DD.
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
        df.groupby(columna_categoria, group_keys=False)
        .head(cantidad_por_categoria)
        .reset_index(drop=True)
    )

    muestra = muestra.drop(columns=["fecha_orden"])

    return muestra


def obtener_valor_palabras_criticas(row: pd.Series):
    """
    Toma las palabras criticas ya calculadas por el pipeline.

    Soporta estos casos:
    - Si la columna palabras_criticas es numero: usa ese numero.
    - Si la columna palabras_criticas es texto/lista: cuenta elementos.
    - Si existe cantidad_palabras_criticas: usa esa columna.
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

    # Si viene como lista en texto: "['dengue', 'emergencia']"
    try:
        parsed = json.loads(valor.replace("'", '"'))
        if isinstance(parsed, list):
            return len(parsed)
    except Exception:
        pass

    # Si viene separado por coma: "dengue, emergencia"
    if "," in valor:
        return len([p.strip() for p in valor.split(",") if p.strip()])

    # Si viene una sola palabra critica.
    return 1


def analizar_dataframe(
    df: pd.DataFrame,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
    modelo: str = MODELO_LLM,
    tiempo_espera: int = TIEMPO_ESPERA_SEGUNDOS,
) -> pd.DataFrame:
    """
    Analiza una muestra de noticias usando Gemini.

    Gemini genera:
    - resumen_llm
    - sentimiento
    - justificacion_sentimiento
    - categoria_predicha

    Python genera:
    - cantidad_palabras_criticas
    - es_alerta
    - nivel_alerta
    """
    client = crear_cliente_gemini()

    muestra = seleccionar_noticias_por_categoria(
        df=df,
        columna_categoria=COLUMNA_CATEGORIA,
        cantidad_por_categoria=cantidad_por_categoria,
    )

    resultados = []

    total = len(muestra)

    for i, (_, row) in enumerate(muestra.iterrows(), start=1):
        titulo = row.get("titulo", "")
        texto = row.get("texto", "")

        print(f"[{i}/{total}] Analizando: {str(titulo)[:80]}")

        try:
            analisis = analizar_noticia_con_llm(
                client=client,
                titulo=titulo,
                texto=texto,
                modelo=modelo,
            )
        except Exception as error:
            analisis = {
                "resumen_llm": "",
                "sentimiento": "neutral",
                "justificacion_sentimiento": f"Error en llamada LLM: {error}",
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

        # Espera entre llamadas para evitar error 429 por limite de cuota.
        if i < total:
            print(f"Esperando {tiempo_espera} segundos para evitar limite de API...")
            time.sleep(tiempo_espera)

    return pd.DataFrame(resultados)


def analizar_csv(
    input_path: str | Path = INPUT_DEFAULT,
    output_path: str | Path = OUTPUT_DEFAULT,
    cantidad_por_categoria: int = NOTICIAS_POR_CATEGORIA,
    modelo: str = MODELO_LLM,
    tiempo_espera: int = TIEMPO_ESPERA_SEGUNDOS,
) -> pd.DataFrame:
    """
    Lee el CSV procesado, analiza las noticias con Gemini y guarda un nuevo CSV.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

    print(f"Leyendo archivo: {input_path}")
    df = pd.read_csv(input_path)

    print(f"Analizando {cantidad_por_categoria} noticias por categoria...")
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
        description="Analiza noticias con Gemini y genera resumen, sentimiento y categoria predicha."
    )

    parser.add_argument(
        "--input",
        default=INPUT_DEFAULT,
        help="Ruta del CSV procesado de entrada.",
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_DEFAULT,
        help="Ruta del CSV analizado de salida.",
    )

    parser.add_argument(
        "--per-category",
        type=int,
        default=NOTICIAS_POR_CATEGORIA,
        help="Cantidad de noticias a analizar por categoria.",
    )

    parser.add_argument(
        "--model",
        default=MODELO_LLM,
        help="Modelo Gemini a utilizar.",
    )

    parser.add_argument(
        "--sleep",
        type=int,
        default=TIEMPO_ESPERA_SEGUNDOS,
        help="Segundos de espera entre llamadas al LLM.",
    )

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
