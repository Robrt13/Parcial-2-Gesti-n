# Sistema Inteligente de Análisis de Noticias de Panamá

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un sistema inteligente para recopilar, procesar, analizar y visualizar noticias publicadas por medios digitales de Panamá. El sistema utiliza técnicas de web scraping, procesamiento de datos e inteligencia artificial para clasificar noticias por categoría, analizar su sentimiento y detectar aquellas, críticas, que puedan requerir atención.

El objetivo principal es facilitar el análisis de grandes cantidades de información periodística, permitiendo comparar medios y categorías de noticias según el sentimiento y criticidad del contenido, identificando tendencias, comportamientos y noticias con posible impacto social, económico o político.

## Problemática

En Panamá se publican diariamente noticias en diferentes medios digitales. Sin embargo, revisar manualmente cada medio puede ser un proceso lento y poco eficiente. Además, no siempre es fácil identificar rápidamente qué sentimiento predomina en las noticias o cuáles publicaciones pueden representar una alerta por tratar temas críticos como protestas, accidentes, salud pública, seguridad, economía o emergencias.

Por esta razón, se propone un sistema que automatice la recopilación y análisis de noticias nacionales, permitiendo obtener información organizada y visual mediante un dashboard interactivo.

## Objetivo general

Desarrollar un sistema inteligente de análisis de noticias de Panamá que recopile información desde medios digitales, procese los datos obtenidos, clasifique las noticias por categoría y sentimiento, y presente los resultados en un dashboard interactivo.

## Objetivos específicos

* Recopilar noticias de medios digitales panameños mediante web scraping.
* Integrar datos provenientes de al menos tres fuentes de noticias.
* Limpiar, transformar y estructurar los datos obtenidos.
* Aplicar técnicas de machine learning para clasificar noticias.
* Analizar el sentimiento de las noticias como positivo, negativo o neutral.
* Detectar noticias relacionadas con temas críticos mediante un sistema de alertas.
* Crear un dashboard interactivo utilizando Streamlit.
* Documentar el funcionamiento del proyecto y su estructura técnica.

## Fuentes de datos

El sistema recopila noticias desde medios digitales panameños. Las fuentes propuestas para el proyecto son:

* TVN Noticias
* Telemetro
* La Prensa

Cada fuente permite obtener información como:

* Título de la noticia
* Fecha de publicación
* Medio de comunicación
* Categoría
* Resumen o contenido principal
* URL de la noticia

## Tecnologías utilizadas

El proyecto está desarrollado principalmente en Python y utiliza las siguientes herramientas y librerías:

* Python
* Pandas
* Requests
* BeautifulSoup
* Streamlit
* Plotly
* spaCy
* ollama
* GitHub

## Estructura del proyecto

```text
sistema-noticias-panama/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── noticias_tvn.csv
│   │   ├── noticias_telemetro.csv
│   │   └── noticias_laprensa.csv
│   │
│   └── processed/
│       ├── noticias_panama_procesadas.csv
│       └── noticias_panama_analizadas.csv
│
├── scrapers/
│   ├── scraper_tvn.py
│   ├── scraper_telemetro.py
│   └── scraper_laprensa.py
│
├── pipeline/
│   ├── ingestion.py
│   ├── cleaning.py
│   ├── transformation.py
│   └── pipeline_main.py
│
├── models/
│   ├── alert_logic.py
│   └── llm_news_analysis.py
│
└── dashboard/
    └── streamlit_app.py
```

## Funcionamiento del sistema

El sistema funciona mediante un pipeline de datos dividido en varias etapas:

### 1. Ingesta de datos

En esta etapa se recopilan noticias desde diferentes medios digitales panameños utilizando web scraping. Cada scraper extrae información básica de las noticias y la almacena en archivos CSV, en la carpeta `data/raw/`.

### 2. Limpieza de datos

Después de recopilar las noticias, se realiza un proceso de limpieza para mejorar la calidad del dataset. Este proceso incluye:

* Union de CSV
* Eliminación de registros incompletos.
* Eliminación de noticias duplicadas.
* Normalización de texto y categorías

### 3. Transformación de datos

En esta etapa se generan nuevas columnas útiles para el análisis, como:

* Categoría predicha.
* Cantidad de palabras críticas.
* Sentimiento.
* Estado de alerta.
* Nivel de alerta.

Y se lematiza el contenido de las noticias para facilitar su análisis posterior por el LLM. El resultado se guarda en `data/processed/noticias_panama_procesadas.csv`

### 4. Análisis con Inteligencia Artificial

#### 4.1. Predicción de categorías

El proyecto aplica una técnica de clasificación para organizar las noticias en diferentes categorías, tales como:

* Nacionales
* Mundo
* Deportes
* Entretenimiento
* Contenido exclusivo
* Política
* Economía
* Seguridad
* Salud
* Educación
* Ambiente
* Tecnología
* Otro

#### 4.2.Analisis de sentimiento

El sistema clasifica cada noticia según su sentimiento general:

* Positivo
* Negativo
* Neutral

Este análisis permite identificar el tono predominante de las noticias y relacionarlo con los temas más mencionados.

### 5. Sistema de alertas

El sistema incluye una sección de alertas para detectar noticias relacionadas con temas críticos. Para ello, se utilizan palabras clave como:

* Protesta
* Cierre de vía
* Homicidio
* Dengue
* Accidente
* Corrupción
* Emergencia
* Crisis
* Inundación
* Violencia

Si una noticia contiene palabras críticas y además presenta un sentimiento negativo, el sistema puede marcarla como una alerta de nivel alto.

El resultado de la predicción de categoría, el análisis de sentimiento y el sistema de alertas se almacena en `data/processed/noticias_panama_analizadas.csv`

### 6. Dashboard interactivo

El dashboard desarrollado en Streamlit permite visualizar los resultados del análisis de forma clara e interactiva.

El dashboard incluye:

* Total de noticias analizadas.
* Noticias por medio de comunicación.
* Noticias por categoría.
* Distribución de sentimiento.
* Noticias por fecha.
* Filtros por fecha, categoría, medio y sentimiento.
* Tabla con noticias recolectadas.
* Sección de alertas críticas.

## Variables principales del dataset

| Columna            | Descripción                                         |
| ------------------ | --------------------------------------------------- |
| medio              | Medio de comunicación de origen                     |
| titulo             | Título de la noticia                                |
| fecha              | Fecha de publicación de la noticia                  |
| categoria_original | Categoría indicada por el medio, si está disponible |
| texto              | Resumen o contenido de la noticia                   |
| url                | Enlace de la noticia                                |
| categoria_predicha | Categoría asignada por el modelo                    |
| palabras_criticas  | Cantidad de palabras críticas en el texto           |
| sentimiento        | Sentimiento de la noticia                           |
| es_alerta          | Indica si la noticia representa una alerta          |
| nivel_alerta       | Nivel de alerta asignado                            |

## Instalación del proyecto

Para ejecutar el proyecto, primero se debe clonar el repositorio:

```bash
git clone https://github.com/usuario/sistema-noticias-panama.git
```

Luego se ingresa a la carpeta del proyecto:

```bash
cd sistema-noticias-panama
```

Se recomienda crear un entorno virtual:

```bash
python -m venv venv
```

Activar el entorno virtual en Windows:

```bash
venv\Scripts\activate
```

Activar el entorno virtual en Mac o Linux:

```bash
source venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Instalar Ollama:
[Ollama for Windows](`https://ollama.com/download/windows`)


## Ejecución del pipeline

Para ejecutar el pipeline completo de datos:

```bash
python -m pipeline.pipeline_main
```

## Ejecución del dashboard

Para iniciar el dashboard en Streamlit:

```bash
streamlit run dashboard/streamlit_app.py
```

Luego, el sistema abrirá una interfaz web donde se podrán visualizar las noticias analizadas, los gráficos, filtros y alertas generadas.

## Resultados esperados

Al finalizar la ejecución del sistema, se espera obtener:

* Un dataset consolidado de noticias panameñas.
* Noticias clasificadas automáticamente por categoría.
* Análisis de sentimiento para cada noticia.
* Alertas asignadas a noticias críticas.
* Dashboard interactivo con filtros y visualizaciones.
* Documentación parcial del funcionamiento del proyecto.

## Evaluación del proyecto

El proyecto cumple con los componentes principales del segundo parcial:

| Componente        | Cumplimiento                                                     |
| ----------------- | ---------------------------------------------------------------- |
| Pipeline de datos | Scraping, limpieza, transformación y generación de dataset final |
| Análisis ML       | Clasificación de noticias y análisis de sentimiento              |
| Visualización     | Dashboard interactivo en Streamlit                               |
| Documentación     | README, estructura del proyecto y explicación del pipeline       |

## Posibles mejoras futuras

* Agregar más medios digitales de Panamá.
* Implementar actualización automática diaria.
* Integrar un modelo de lenguaje para generar resúmenes automáticos.
* Añadir un chatbot para consultar noticias por tema.
* Mejorar el análisis de sentimiento con modelos especializados en español.
* Incorporar visualizaciones por provincia o ubicación geográfica.
* Implementar almacenamiento en base de datos.

## Integrantes

* Calderón, Ovidio
* Fu, Winson
* Huertas, José
* Luo, Anie
* Takata, Gabriela

## Curso

Gestión de la Información
Facultad de Ingeniería de Sistemas Computacionales
Universidad Tecnológica de Panamá
I Semestre 2026

## Estado del proyecto

Proyecto en desarrollo para el Segundo Parcial.
