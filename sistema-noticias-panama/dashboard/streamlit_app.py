import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# CONFIGURACION DE LA PAGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard de Noticias",
    layout="wide"
)

# ============================================================
# CARGA DE DATOS
# ============================================================

# Archivo con las noticias analizadas
INPUT_ANALIZADO = Path(__file__).resolve().parent.parent / "data/processed/noticias_panama_analizadas.csv"

# Lectura del dataset
df = pd.read_csv(INPUT_ANALIZADO)

# Conversion de fechas
df["fecha"] = pd.to_datetime(df["fecha"])

# ============================================================
# TITULO PRINCIPAL
# ============================================================

st.title("Dashboard de Analisis de Noticias")

# ============================================================
# METRICA GENERAL
# ============================================================

st.metric(
    "Total de noticias analizadas",
    len(df)
)

# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("Filtros")

categorias = st.sidebar.multiselect(
    "Categoria",
    options=df["categoria_predicha"].unique(),
    default=df["categoria_predicha"].unique()
)

medios = st.sidebar.multiselect(
    "Medio",
    options=df["medio"].unique(),
    default=df["medio"].unique()
)

sentimientos = st.sidebar.multiselect(
    "Sentimiento",
    options=df["sentimiento"].unique(),
    default=df["sentimiento"].unique()
)

# Aplicacion de filtros
df_filtrado = df[
    (df["categoria_predicha"].isin(categorias))
    & (df["medio"].isin(medios))
    & (df["sentimiento"].isin(sentimientos))
]

# ============================================================
# NOTICIAS POR MEDIO DE COMUNICACION
# ============================================================

st.subheader("Noticias por medio")

medio_count = (
    df_filtrado["medio"]
    .value_counts()
    .reset_index()
)

medio_count.columns = ["medio", "cantidad"]

fig = px.bar(
    medio_count,
    x="medio",
    y="cantidad"
)

st.plotly_chart(fig, width="stretch")

# ============================================================
# NOTICIAS POR CATEGORIA
# ============================================================

st.subheader("Noticias por categoría")

categoria_count = (
    df_filtrado["categoria_predicha"]
    .value_counts()
    .reset_index()
)

categoria_count.columns = ["categoria", "cantidad"]

fig = px.pie(
    categoria_count,
    names="categoria",
    values="cantidad"
)

st.plotly_chart(fig, width="stretch")

# ============================================================
# DISTRIBUCION DE SENTIMIENTO
# ============================================================

st.subheader("Distribución de sentimiento")

sentimiento_count = (
    df_filtrado["sentimiento"]
    .value_counts()
    .reset_index()
)

sentimiento_count.columns = ["sentimiento", "cantidad"]

fig = px.bar(
    sentimiento_count,
    x="sentimiento",
    y="cantidad",
    color="sentimiento"
)

st.plotly_chart(fig, width="stretch")

# ============================================================
# NOTICIAS POR FECHA
# ============================================================

st.subheader("Noticias por fecha")

fecha_count = (
    df_filtrado.groupby("fecha")
    .size()
    .reset_index(name="cantidad")
)

fig = px.line(
    fecha_count,
    x="fecha",
    y="cantidad"
)

st.plotly_chart(fig, width="stretch")

# ============================================================
# TABLA DE NOTICIAS
# ============================================================

st.subheader("Noticias recolectadas")

st.dataframe(
    df_filtrado[
        [
            "fecha",
            "medio",
            "titulo",
            "categoria_predicha",
            "sentimiento",
            "nivel_alerta"
        ]
    ],
    width="stretch"
)

# ============================================================
# SECCION DE ALERTAS CRITICAS
# ============================================================

st.subheader("Alertas criticas")

alertas = df_filtrado[
    df_filtrado["es_alerta"] == True
]

if len(alertas) > 0:
    st.error(
        f"Se detectaron {len(alertas)} noticias de alerta"
    )

    st.dataframe(
        alertas[
            [
                "fecha",
                "medio",
                "titulo",
                "nivel_alerta",
                "sentimiento"
            ]
        ],
        width="stretch"
    )
else:
    st.success(
        "No se detectaron alertas criticas"
    )