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

# ============================================================
# APLICACION DE FILTROS
# ============================================================

df_filtrado = df[
    (df["categoria_predicha"].isin(categorias))
    & (df["medio"].isin(medios))
    & (df["sentimiento"].isin(sentimientos))
]

# ============================================================
# PESTAÑAS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Medios",
        "Categorías",
        "Sentimientos",
        "Fechas",
        "Noticias",
        "Alertas"
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

    medio_count.columns = ["medio", "cantidad"]

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
        values="cantidad",
        title="Distribución por categoría"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ============================================================
# TAB 3 - SENTIMIENTOS
# ============================================================

with tab3:

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
        color="sentimiento",
        title="Distribución de sentimientos"
    )

    st.plotly_chart(
        fig,
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
# TAB 5 - NOTICIAS DETALLADAS
# ============================================================

with tab5:

    st.subheader("Noticias detalladas")

    if len(df_filtrado) == 0:

        st.warning(
            "No hay noticias para mostrar."
        )

    else:

        for _, fila in (
            df_filtrado
            .sort_values(
                "fecha",
                ascending=False
            )
            .iterrows()
        ):

            titulo_ventana = (
                f"{fila['fecha'].date()} | "
                f"{fila['medio']} | "
                f"{fila['titulo']}"
            )

            with st.expander(titulo_ventana):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Categoría",
                        fila["categoria_predicha"]
                    )

                with col2:
                    st.metric(
                        "Sentimiento",
                        fila["sentimiento"]
                    )

                with col3:
                    st.metric(
                        "Nivel alerta",
                        fila["nivel_alerta"]
                    )

                st.markdown("### Resumen generado por LLM")
                st.info(
                    fila["resumen_llm"]
                )

                st.markdown(
                    "### Justificación del sentimiento"
                )
                st.write(
                    fila["justificacion_sentimiento"]
                )

                st.markdown(
                    "### Texto completo"
                )
                st.write(
                    fila["texto"]
                )

                st.link_button(
                    "Abrir noticia original",
                    fila["url"]
                )

# ============================================================
# TAB 6 - ALERTAS
# ============================================================

with tab6:

    st.subheader("Alertas críticas")

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
            "No se detectaron alertas críticas"
        )
