# Sistema Inteligente de Análisis de Noticias de Panamá

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un sistema inteligente para recopilar, procesar, analizar y visualizar noticias publicadas por medios digitales de Panamá. El sistema utiliza técnicas de web scraping, procesamiento de datos, machine learning e inteligencia artificial para clasificar noticias por categoría, analizar su sentimiento y detectar temas críticos que puedan requerir atención.

El objetivo principal es facilitar el análisis de grandes cantidades de información periodística, permitiendo identificar tendencias, temas más mencionados, comportamiento de los medios y noticias con posible impacto social, económico o político.

## Problemática

En Panamá se publican diariamente noticias en diferentes medios digitales. Sin embargo, revisar manualmente cada medio puede ser un proceso lento y poco eficiente. Además, no siempre es fácil identificar rápidamente cuáles son los temas más frecuentes, qué sentimiento predomina en las noticias o cuáles publicaciones pueden representar una alerta por tratar temas críticos como protestas, accidentes, salud pública, seguridad, economía o emergencias.

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
* Scikit-learn
* Streamlit
* Plotly
* NLTK o spaCy
* GitHub

## Estructura del proyecto

```text
sistema-noticias-panama/
│
├── app.py
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
│       └── noticias_panama_procesadas.csv
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
│   ├── category_classifier.py
│   └── sentiment_analysis.py
│
├── dashboard/
│   └── streamlit_app.py
│
└── docs/
    └── documentacion_parcial.md
```

## Funcionamiento del sistema

El sistema funciona mediante un pipeline de datos dividido en varias etapas:

### 1. Ingesta de datos

En esta etapa se recopilan noticias desde diferentes medios digitales panameños utilizando web scraping. Cada scraper extrae información básica de las noticias y la almacena en archivos CSV dentro de la carpeta `data/raw`.

### 2. Limpieza de datos

Después de recopilar las noticias, se realiza un proceso de limpieza para mejorar la calidad del dataset. Este proceso incluye:

* Eliminación de registros incompletos.
* Normalización de fechas.
* Limpieza de caracteres especiales.
* Conversión de texto a minúsculas.
* Organización de columnas.

### 3. Transformación de datos

En esta etapa se generan nuevas columnas útiles para el análisis, como:

* Longitud del texto.
* Categoría predicha.
* Sentimiento.
* Palabras clave.
* Nivel de alerta.
* Estado de alerta.

El resultado final se guarda en la carpeta `data/processed`.

### 4. Análisis con Machine Learning

El proyecto aplica una técnica de clasificación para organizar las noticias en diferentes categorías, tales como:

* Política
* Economía
* Seguridad
* Salud
* Educación
* Deportes
* Ambiente
* Tecnología

Para esta clasificación se puede utilizar un modelo basado en TF-IDF junto con algoritmos como Logistic Regression o Naive Bayes.

### 5. Análisis de sentimiento

El sistema clasifica cada noticia según su sentimiento general:

* Positivo
* Negativo
* Neutral

Este análisis permite identificar el tono predominante de las noticias y relacionarlo con los temas más mencionados.

### 6. Sistema de alertas

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

### 7. Dashboard interactivo

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
| fecha              | Fecha de publicación de la noticia                  |
| medio              | Medio de comunicación de origen                     |
| titulo             | Título de la noticia                                |
| categoria_original | Categoría indicada por el medio, si está disponible |
| texto              | Resumen o contenido de la noticia                   |
| url                | Enlace de la noticia                                |
| categoria_predicha | Categoría asignada por el modelo                    |
| sentimiento        | Sentimiento de la noticia                           |
| palabras_clave     | Términos relevantes encontrados                     |
| nivel_alerta       | Nivel de alerta asignado                            |
| es_alerta          | Indica si la noticia representa una alerta          |

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

## Ejecución del pipeline

Para ejecutar el pipeline completo de datos:

```bash
python pipeline/pipeline_main.py
```

Este comando realiza los siguientes pasos:

1. Ejecuta la ingesta de noticias.
2. Limpia los datos recopilados.
3. Transforma el dataset.
4. Aplica clasificación y análisis de sentimiento.
5. Genera el archivo final procesado.

## Ejecución del dashboard

Para iniciar el dashboard en Streamlit:

```bash
streamlit run app.py
```

Luego, el sistema abrirá una interfaz web donde se podrán visualizar las noticias analizadas, los gráficos, filtros y alertas generadas.

## Resultados esperados

Al finalizar la ejecución del sistema, se espera obtener:

* Un dataset consolidado de noticias panameñas.
* Noticias clasificadas automáticamente por categoría.
* Análisis de sentimiento para cada noticia.
* Identificación de temas críticos.
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
