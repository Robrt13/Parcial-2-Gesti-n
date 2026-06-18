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

INPUT_ANALIZADO = (
    Path(__file__).resolve().parent.parent
    / "data/processed/noticias_panama_analizadas.csv"
)

df = pd.read_csv(INPUT_ANALIZADO)

# Conversion de fechas
df["fecha"] = pd.to_datetime(df["fecha"])

# ============================================================
# TITULO PRINCIPAL
# ============================================================

st.title("Dashboard de Análisis de Noticias")

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
    "Categoría",
    options=sorted(df["categoria_original"].unique()),
    default=sorted(df["categoria_original"].unique())
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

# ============================================================
# APLICACION DE FILTROS
# ============================================================

df_filtrado = df[
    (df["categoria_original"].isin(categorias))
    & (df["medio"].isin(medios))
    & (df["sentimiento"].isin(sentimientos))
]

# ============================================================
# PESTAÑAS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
    [
        "Medios",
        "Categorías",
        "Sentimientos",
        "Fechas",
        "Aciertos de categoría",
        "Noticias",
        "Alertas",
        "Palabras críticas",
        "Precisión por medio",
        "Alertas por fuente"
    ]
)

# ============================================================
# TAB 1 - MEDIOS
# ============================================================

with tab1:

    st.subheader("Noticias por medio")

    medio_count = (
        df_filtrado["medio"]
        .value_counts()
        .reset_index()
    )

    medio_count.columns = [
        "medio",
        "cantidad"
    ]

    fig = px.bar(
        medio_count,
        x="medio",
        y="cantidad",
        color="medio",
        title="Cantidad de noticias por medio"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 2 - CATEGORIAS
# ============================================================

with tab2:

    st.subheader(
        "Comparación de categorías por medio"
    )

    categoria_medio = (
        df_filtrado
        .groupby(
            ["medio", "categoria_original"]
        )
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.bar(
        categoria_medio,
        x="categoria_original",
        y="cantidad",
        color="medio",
        barmode="stack",
        title="Categorías por medio"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 3 - SENTIMIENTOS
# ============================================================

with tab3:

    st.subheader(
        "Comparación de sentimientos por medio"
    )

    sentimiento_medio = (
        df_filtrado
        .groupby(
            ["medio", "sentimiento"]
        )
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.bar(
        sentimiento_medio,
        x="sentimiento",
        y="cantidad",
        color="medio",
        barmode="stack",
        title="Sentimientos por medio"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    st.subheader(
        "Sentimientos por categoría"
    )

    categoria_sentimiento = (
        df_filtrado
        .groupby(
            [
                "categoria_original",
                "sentimiento"
            ]
        )
        .size()
        .reset_index(name="cantidad")
    )

    fig2 = px.bar(
        categoria_sentimiento,
        x="categoria_original",
        y="cantidad",
        color="sentimiento",
        barmode="stack",
        title="Distribución de sentimientos por categoría"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )


# ============================================================
# TAB 4 - FECHAS
# ============================================================

with tab4:

    st.subheader("Noticias por fecha")

    fecha_count = (
        df_filtrado
        .groupby("fecha")
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.line(
        fecha_count,
        x="fecha",
        y="cantidad",
        markers=True,
        title="Evolución temporal"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 5 - ACIERTOS DE CATEGORÍA
# ============================================================

with tab5:

    st.subheader("Acierto de clasificación")

    df_acierto = df_filtrado.copy()

    df_acierto["resultado"] = (
        df_acierto["categoria_original"]
        == df_acierto["categoria_predicha"]
    )

    df_acierto["resultado"] = df_acierto["resultado"].map(
        {
            True: "Correcta",
            False: "Incorrecta"
        }
    )

    conteo = (
        df_acierto["resultado"]
        .value_counts()
        .reset_index()
    )

    conteo.columns = [
        "resultado",
        "cantidad"
    ]

    fig = px.pie(
        conteo,
        names="resultado",
        values="cantidad",
        title="Categoría original vs categoría predicha"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    precision = (
        (
            df_acierto["categoria_original"]
            == df_acierto["categoria_predicha"]
        ).mean()
        * 100
    )

    st.metric(
        "Precisión",
        f"{precision:.2f}%"
    )

# ============================================================
# TAB 6 - NOTICIAS
# ============================================================

with tab6:

    st.subheader("Noticias")

    orden_alerta = {
        "alta": 3,
        "media": 2,
        "baja": 1,
        "sin alerta": 0
    }

    noticias = df_filtrado.copy()

    noticias["prioridad"] = (
        noticias["nivel_alerta"]
        .str.lower()
        .map(orden_alerta)
    )

    noticias = noticias.sort_values(
        ["prioridad", "palabras_criticas"],
        ascending=[False, False]
    )

    for _, fila in noticias.iterrows():

        titulo = (
            f"{fila['nivel_alerta'].upper()} | "
            f"{fila['medio']} | "
            f"{fila['titulo']}"
        )

        with st.expander(titulo):

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Categoría",
                    fila["categoria_original"]
                )

            with c2:
                st.metric(
                    "Categoría predicha",
                    fila["categoria_predicha"]
                )

            with c3:
                st.metric(
                    "Palabras críticas",
                    fila["palabras_criticas"]
                )

            st.write("### Sentimiento")
            st.write(
                fila["sentimiento"]
            )

            st.write("### Texto")

            st.write(
                fila["texto"]
            )

            st.link_button(
                "Ver noticia",
                fila["url"]
            )

# ============================================================
# TAB 7 - ALERTAS
# ============================================================

with tab7:

    st.subheader(
        "Noticias con alertas"
    )

    orden_alerta = {
        "alta": 3,
        "media": 2,
        "baja": 1,
        "sin alerta": 0
    }

    alertas = df_filtrado.copy()

    alertas["prioridad_alerta"] = (
        alertas["nivel_alerta"]
        .str.lower()
        .map(orden_alerta)
    )

    alertas = alertas.sort_values(
        by=[
            "prioridad_alerta",
            "palabras_criticas"
        ],
        ascending=[
            False,
            False
        ]
    )

    st.dataframe(

        alertas[
            [
                "fecha",
                "medio",
                "titulo",
                "nivel_alerta",
                "palabras_criticas",
                "sentimiento"
            ]
        ],

        width="stretch"
    )

# ============================================================
# TAB 8 - PALABRAS CRÍTICAS
# ============================================================

with tab8:

    st.subheader(
        "Palabras críticas por medio"
    )

    palabras_medio = (
        df_filtrado
        .groupby(
            [
                "medio",
                "palabras_criticas"
            ]
        )
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.bar(
        palabras_medio,
        x="palabras_criticas",
        y="cantidad",
        color="medio",
        barmode="group",
        title="Cantidad de palabras críticas por medio"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 9 - PRECISIÓN POR MEDIO
# ============================================================

with tab9:

    st.subheader(
        "Precisión del clasificador por medio"
    )

    precision_medio = (
        df_filtrado
        .assign(
            acierto=(
                df_filtrado["categoria_original"]
                == df_filtrado["categoria_predicha"]
            )
        )
        .groupby(
            "medio"
        )["acierto"]
        .mean()
        .reset_index()
    )

    precision_medio["acierto"] *= 100

    fig = px.bar(
        precision_medio,
        x="medio",
        y="acierto",
        color="medio",
        text_auto=".1f",
        title="Precisión por medio (%)"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 10 - ALERTAS POR FUENTE
# ============================================================

with tab10:

    st.subheader(
        "Comparación de alertas entre medios"
    )

    orden = [
        "alta",
        "media",
        "baja",
        "sin alerta"
    ]

    alertas_fuente = (
        df_filtrado
        .groupby(
            [
                "medio",
                "nivel_alerta"
            ]
        )
        .size()
        .reset_index(name="cantidad")
    )

    fig = px.bar(
        alertas_fuente,
        x="nivel_alerta",
        y="cantidad",
        color="medio",
        barmode="group",
        category_orders={
            "nivel_alerta": orden
        },
        title="Distribución de alertas por medio"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.divider()

    st.subheader(
        "Composición de alertas por medio"
    )

    fig2 = px.bar(
        alertas_fuente,
        x="medio",
        y="cantidad",
        color="nivel_alerta",
        barmode="stack",
        category_orders={
            "nivel_alerta": orden
        },
        title="Alertas apiladas por medio"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

