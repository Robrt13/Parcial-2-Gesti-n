# Sistema Inteligente de Análisis de Noticias de Panamá

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un sistema inteligente para recopilar, procesar, analizar y visualizar noticias publicadas por medios digitales de Panamá.

El sistema integra técnicas de web scraping, procesamiento de datos, procesamiento de lenguaje natural, Machine Learning y Modelos de Lenguaje de Gran Escala para clasificar noticias, analizar su sentimiento y detectar publicaciones críticas que puedan requerir atención.

El objetivo principal es facilitar el análisis de grandes cantidades de información periodística, permitiendo comparar medios de comunicación, categorías, sentimientos y niveles de criticidad. Además, el sistema permite identificar tendencias y noticias con posible impacto social, económico, político o nacional.

El proyecto utiliza dos enfoques de inteligencia artificial:

- Machine Learning mediante un modelo de clasificación supervisada basado en TF-IDF y Linear Support Vector Classification.
- Un Modelo de Lenguaje de Gran Escala ejecutado localmente mediante Ollama para analizar el sentimiento y predecir categorías.

Los resultados se almacenan en un dataset consolidado que posteriormente será utilizado para el desarrollo de dashboards y análisis interactivos en Power BI.

---

## Problemática

En Panamá se publican diariamente noticias en diferentes medios digitales. La revisión manual de múltiples plataformas puede convertirse en un proceso lento, repetitivo y poco eficiente.

Además, no siempre es sencillo identificar rápidamente:

- Qué temas predominan en las noticias.
- Qué sentimiento presentan las publicaciones.
- Cuáles noticias pueden representar situaciones críticas.
- Qué categorías tienen una mayor presencia.
- Cuáles medios publican con mayor frecuencia sobre determinados temas.
- Qué noticias pueden estar relacionadas con seguridad, emergencias, economía, política, salud pública o conflictos sociales.

Por esta razón, se propone un sistema inteligente que automatiza la recopilación, limpieza, clasificación y análisis de noticias nacionales.

El sistema permite transformar información periodística no estructurada en datos organizados que puedan ser utilizados para análisis, visualización y apoyo en la toma de decisiones.

---

## Objetivo general

Desarrollar un sistema inteligente de análisis de noticias de Panamá que recopile información desde medios digitales, procese los datos obtenidos, clasifique las noticias mediante Machine Learning y Modelos de Lenguaje de Gran Escala, analice su sentimiento y presente los resultados mediante herramientas de visualización interactiva.

---

## Objetivos específicos

- Recopilar noticias de medios digitales panameños mediante técnicas de web scraping.
- Integrar información proveniente de al menos tres medios de comunicación.
- Limpiar, normalizar y estructurar los datos recopilados.
- Aplicar procesamiento de lenguaje natural al contenido de las noticias.
- Implementar un modelo de Machine Learning para clasificar automáticamente las noticias.
- Comparar diferentes algoritmos de clasificación y seleccionar el modelo con mejor rendimiento.
- Analizar el sentimiento de las noticias mediante un Modelo de Lenguaje de Gran Escala.
- Clasificar las noticias mediante un LLM como apoyo adicional al análisis.
- Detectar noticias relacionadas con temas críticos mediante un sistema de alertas.
- Generar un dataset consolidado para su utilización en Power BI.
- Diseñar un modelo estrella para organizar la información.
- Ampliar los indicadores clave de rendimiento.
- Desarrollar dashboards interactivos para facilitar el análisis de la información.

---

## Fuentes de datos

El sistema recopila noticias desde los siguientes medios digitales panameños:

- TVN Noticias
- Telemetro
- La Prensa

Cada medio permite obtener información como:

- Título de la noticia.
- Fecha de publicación.
- Medio de comunicación.
- Categoría original.
- Resumen o contenido principal.
- URL de la noticia.

---

## Tecnologías utilizadas

El proyecto utiliza las siguientes tecnologías y herramientas:

- Python
- Pandas
- Requests
- BeautifulSoup
- spaCy
- Scikit-learn
- Joblib
- Ollama
- Qwen
- Pydantic
- Streamlit
- Plotly
- Power BI
- Git
- GitHub

---

## Estructura del proyecto

```text
sistema-noticias-panama/
│
├── README.md
├── requirements.txt
│
├── data/
│   │
│   ├── raw/
│   │   ├── noticias_tvn.csv
│   │   ├── noticias_telemetro.csv
│   │   └── noticias_laprensa.csv
│   │
│   └── processed/
│       ├── noticias_panama_procesadas.csv
│       ├── noticias_panama_analizadas.csv
│       └── noticias_panama_ml.csv
│
├── scrapers/
│   ├── scraper_tvn.py
│   ├── scraper_telemetro.py
│   ├── scraper_laprensa.py
│   └── __init__.py
│
├── pipeline/
│   ├── ingestion.py
│   ├── cleaning.py
│   ├── transformation.py
│   ├── commons.py
│   ├── pipeline_main.py
│   └── __init__.py
│
├── models/
│   │
│   ├── llm/
│   │   ├── llm_news_analysis.py
│   │   ├── alert_logic.py
│   │   ├── commons.py
│   │   └── __init__.py
│   │
│   └── ml/
│       ├── train_category_model.py
│       ├── category_classifier.py
│       ├── predict_existing_csv.py
│       ├── __init__.py
│       │
│       ├── artifacts/
│       │   └── category_classifier.joblib
│       │
│       └── metrics/
│           ├── model_metrics.json
│           ├── model_comparison.csv
│           ├── classification_report.csv
│           └── confusion_matrix.csv
│
└── dashboard/
    └── streamlit_app.py
```

---

# Funcionamiento del sistema

El sistema utiliza un pipeline dividido en diferentes etapas.

## 1. Ingesta de datos

La primera etapa recopila noticias desde diferentes medios digitales panameños mediante técnicas de web scraping.

Los scrapers extraen información desde:

- TVN Noticias.
- Telemetro.
- La Prensa.

Los datos recopilados se almacenan inicialmente en archivos independientes dentro de:

```text
data/raw/
```

Los archivos generados son:

```text
noticias_tvn.csv
noticias_telemetro.csv
noticias_laprensa.csv
```

---

## 2. Limpieza de datos

Después de recopilar la información, los archivos son unidos en un único DataFrame.

El proceso de limpieza incluye:

- Unión de los archivos CSV.
- Eliminación de registros sin título.
- Eliminación de registros sin contenido.
- Eliminación de noticias duplicadas.
- Normalización de categorías.
- Conversión de texto a minúsculas.
- Eliminación de caracteres no permitidos.
- Normalización de nombres de categorías.

Las categorías no reconocidas se almacenan como:

```text
otro
```

---

## 3. Transformación de datos

Durante la etapa de transformación se crean nuevas variables para facilitar el análisis.

Las principales transformaciones incluyen:

- Conteo de palabras.
- Lematización del contenido.
- Cálculo del índice de criticidad.
- Inicialización de variables de inteligencia artificial.
- Preparación de columnas para sentimiento y alertas.

El contenido de las noticias es procesado mediante spaCy utilizando el modelo:

```text
es_core_news_sm
```

La lematización permite reducir las palabras a su forma base y facilita la identificación de conceptos críticos.

---

## 4. Cálculo de criticidad

El sistema utiliza un conjunto de palabras y conceptos críticos almacenados en:

```text
critical_words.json
```

Cada concepto posee un peso relacionado con su nivel de importancia.

Algunos conceptos utilizados son:

- Homicidio.
- Masacre.
- Terrorismo.
- Secuestro.
- Violación.
- Desaparición.
- Robo.
- Incendio.
- Accidentes graves.
- Corrupción.
- Narcotráfico.
- Protestas.
- Bloqueos viales.
- Violencia.
- Inundaciones.
- Tormentas.
- Emergencias.
- Epidemias.
- Crisis.

El sistema compara los lemas encontrados en cada noticia con los conceptos definidos y calcula un valor de criticidad.

---

# Implementación de Machine Learning

## Tipo de aprendizaje

Se implementó una técnica de aprendizaje supervisado para resolver un problema de clasificación multiclase.

El objetivo del modelo es predecir automáticamente la categoría temática de una noticia utilizando su título y contenido.

La variable objetivo utilizada fue:

```text
categoria_original
```

La variable generada por el modelo es:

```text
categoria_ml
```

La implementación no reemplaza las categorías existentes.

El dataset final conserva:

```text
categoria_original
categoria_predicha
categoria_ml
```

Cada columna representa una fuente diferente:

| Columna | Descripción |
|---|---|
| categoria_original | Categoría obtenida directamente del medio digital |
| categoria_predicha | Categoría generada por el Modelo de Lenguaje de Gran Escala |
| categoria_ml | Categoría generada por el modelo de Machine Learning |

---

## Preparación de los datos

El modelo utiliza las columnas:

```text
titulo
texto
```

Ambas variables son combinadas para crear la entrada utilizada durante el entrenamiento.

El título se repite una vez para aumentar su importancia temática:

```text
titulo + titulo + texto
```

La información textual se convierte en valores numéricos mediante TF-IDF.

---

## Vectorización TF-IDF

TF-IDF significa:

```text
Term Frequency - Inverse Document Frequency
```

Esta técnica transforma el contenido textual en una representación numérica.

TF-IDF asigna mayor importancia a las palabras que son relevantes dentro de una noticia y reduce la influencia de términos que aparecen frecuentemente en todo el conjunto de datos.

La configuración utilizada incluye:

```text
N-gramas: unigramas y bigramas
Rango: (1, 2)
Frecuencia mínima: 2 documentos
Frecuencia máxima: 95 %
Cantidad máxima de características: 50,000
Sublinear TF: activado
```

Los unigramas representan palabras individuales.

Ejemplos:

```text
economía
gobierno
fútbol
elecciones
```

Los bigramas representan combinaciones de dos palabras.

Ejemplos:

```text
selección nacional
asamblea nacional
cambio climático
crecimiento económico
```

---

## Selección de categorías

El dataset original contenía:

```text
1,196 noticias
```

Se estableció un mínimo de:

```text
30 noticias por categoría
```

Las categorías con una cantidad inferior fueron excluidas únicamente del entrenamiento.

Las categorías originales del dataset no fueron modificadas.

### Categorías utilizadas

| Categoría | Cantidad |
|---|---:|
| Deportes | 278 |
| Otro | 207 |
| Nacionales | 201 |
| Mundo | 156 |
| Economía | 103 |
| Entretenimiento | 93 |
| Política | 92 |
| Contenido exclusivo | 39 |

Cantidad total utilizada:

```text
1,169 noticias
```

### Categorías excluidas

| Categoría | Cantidad | Motivo |
|---|---:|---|
| Tecnología | 23 | Cantidad inferior al mínimo establecido |
| Salud | 4 | Cantidad insuficiente para un entrenamiento confiable |

Las categorías fueron excluidas solamente durante el entrenamiento.

El contenido original del dataset permanece sin modificaciones.

---

## División de los datos

Los datos fueron divididos mediante una separación estratificada.

La distribución utilizada fue:

```text
80 % entrenamiento
20 % prueba
```

Cantidad de registros:

```text
Entrenamiento: 935 noticias
Prueba: 234 noticias
```

Se utilizó:

```text
random_state = 42
```

La división estratificada permitió conservar una proporción similar de cada categoría dentro de los conjuntos de entrenamiento y prueba.

---

## Modelos evaluados

Se evaluaron tres algoritmos:

1. Linear Support Vector Classification.
2. Regresión logística.
3. Complement Naive Bayes.

Los tres modelos utilizaron la misma representación TF-IDF.

---

## Resultados de los modelos

| Modelo | Accuracy | F1 Macro | F1 ponderado |
|---|---:|---:|---:|
| LinearSVC | 81.20 % | 81.64 % | 81.07 % |
| Regresión logística | 79.49 % | 80.53 % | 79.26 % |
| Complement Naive Bayes | 76.07 % | 69.94 % | 74.90 % |

---

## Modelo seleccionado

El modelo seleccionado fue:

```text
TF-IDF + Linear Support Vector Classification
```

El algoritmo obtuvo el mejor valor de F1 Macro y la mayor exactitud entre los modelos evaluados.

Resultados:

```text
Accuracy: 81.20 %
F1 Macro: 81.64 %
F1 ponderado: 81.07 %
```

El criterio principal de selección fue:

```text
F1 Macro
```

Esta métrica fue seleccionada debido a que calcula el rendimiento promedio de todas las categorías y evita que las categorías con mayor cantidad de noticias oculten el desempeño de las categorías más pequeñas.

---

## Justificación del modelo

LinearSVC fue seleccionado porque presenta un buen rendimiento en problemas de clasificación de texto.

El modelo es adecuado debido a las siguientes características:

- Funciona eficientemente con matrices dispersas.
- Puede trabajar con una gran cantidad de características.
- Presenta buen rendimiento con representaciones TF-IDF.
- Permite clasificar múltiples categorías.
- Es eficiente durante la etapa de predicción.
- Obtuvo los mejores resultados entre los algoritmos evaluados.
- Presentó el mayor F1 Macro.
- Presentó la mayor exactitud.

Después de evaluar los modelos utilizando el conjunto de prueba, LinearSVC fue entrenado nuevamente utilizando las 1,169 noticias elegibles.

El modelo final fue almacenado en:

```text
models/ml/artifacts/category_classifier.joblib
```

El archivo se mantiene dentro del repositorio de GitHub para que todos los integrantes utilicen el mismo modelo sin necesidad de volver a entrenarlo.

---

## Métricas generadas

Los resultados del entrenamiento se almacenan en:

```text
models/ml/metrics/
```

### model_metrics.json

Contiene:

- Modelo seleccionado.
- Fecha de entrenamiento.
- Cantidad de noticias utilizadas.
- Categorías incluidas.
- Categorías excluidas.
- Accuracy.
- F1 Macro.
- F1 ponderado.
- Versiones de Python y Scikit-learn.

### model_comparison.csv

Contiene la comparación de los tres algoritmos evaluados.

### classification_report.csv

Contiene:

- Precision.
- Recall.
- F1-score.
- Cantidad de registros por categoría.

### confusion_matrix.csv

Permite analizar:

- Clasificaciones correctas.
- Categorías confundidas.
- Errores de clasificación.
- Comportamiento del modelo por categoría.

---

## Entrenamiento del modelo

Para entrenar nuevamente el modelo:

```bash
python -m models.ml.train_category_model
```

El entrenamiento solamente debe ejecutarse cuando:

- Se agreguen nuevas noticias.
- Cambie el conjunto de datos.
- Se modifique la cantidad mínima por categoría.
- Se realicen cambios en los parámetros del modelo.

El modelo actual ya se encuentra entrenado.

Por esta razón, no es necesario volver a ejecutar el entrenamiento para utilizarlo.

---

## Ejecución del ML sobre el CSV existente

Para aplicar el modelo sobre el archivo que ya contiene el análisis del LLM:

```bash
python -m models.ml.predict_existing_csv
```

Este proceso:

1. Lee:

```text
data/processed/noticias_panama_analizadas.csv
```

2. Carga:

```text
models/ml/artifacts/category_classifier.joblib
```

3. Genera:

```text
categoria_ml
```

4. Guarda:

```text
data/processed/noticias_panama_ml.csv
```

Este proceso no ejecuta:

- Web scraping.
- Limpieza.
- Lematización.
- Ollama.
- Análisis de sentimiento.
- El pipeline completo.

Solamente carga el modelo entrenado y genera las predicciones de Machine Learning.

---

# Análisis mediante Modelo de Lenguaje de Gran Escala

El proyecto utiliza un Modelo de Lenguaje de Gran Escala mediante Ollama.

El modelo configurado es:

```text
qwen3.5:0.8b
```

El LLM recibe:

```text
titulo
texto
```

El modelo genera:

```text
sentimiento
categoria_predicha
```

---

## Análisis de sentimiento

El sentimiento utiliza una escala numérica:

```text
-1.0 = muy negativo
 0.0 = neutral
 1.0 = muy positivo
```

El LLM analiza el tono general de la noticia.

El sentimiento se basa en la forma en que se presenta la información y no únicamente en la gravedad del tema.

---

## Clasificación mediante LLM

El Modelo de Lenguaje de Gran Escala también genera una categoría temática.

La predicción se almacena en:

```text
categoria_predicha
```

Las categorías permitidas son:

- Nacionales.
- Mundo.
- Deportes.
- Entretenimiento.
- Contenido exclusivo.
- Política.
- Economía.
- Seguridad.
- Salud.
- Educación.
- Ambiente.
- Tecnología.
- Otro.

La clasificación del LLM se mantiene separada de la clasificación del modelo de Machine Learning.

Esto permite comparar:

```text
categoria_original
categoria_predicha
categoria_ml
```

---

## Validación de respuestas

Las respuestas generadas por Ollama utilizan una estructura JSON validada mediante Pydantic.

El sistema verifica:

- Que el sentimiento se encuentre entre -1.0 y 1.0.
- Que la categoría pertenezca a las categorías permitidas.
- Que la respuesta pueda convertirse correctamente desde JSON.

Cuando el LLM genera un valor no válido, el sistema aplica valores predeterminados para evitar la interrupción del análisis.

---

# Sistema de alertas

El sistema utiliza:

```text
criticidad
sentimiento
```

para determinar:

```text
es_alerta
nivel_alerta
```

La lógica combina la cantidad de conceptos críticos encontrados con el sentimiento generado por el LLM.

Las noticias con mayor criticidad y sentimiento negativo reciben niveles de alerta superiores.

Los niveles generados son:

```text
0 = Sin alerta
1 = Alerta baja
2 = Alerta media
3 = Alerta alta
```

---

# Dataset final

El archivo consolidado final es:

```text
data/processed/noticias_panama_ml.csv
```

Este archivo contiene los resultados de:

- Web scraping.
- Limpieza.
- Transformación.
- Lematización.
- Cálculo de criticidad.
- Clasificación mediante Machine Learning.
- Clasificación mediante LLM.
- Análisis de sentimiento.
- Sistema de alertas.

---

## Variables principales

| Columna | Descripción |
|---|---|
| medio | Medio de comunicación de origen |
| titulo | Título de la noticia |
| fecha | Fecha de publicación |
| categoria_original | Categoría obtenida directamente del medio |
| texto | Resumen o contenido principal |
| url | Enlace original |
| cantidad_palabras | Cantidad de palabras de la noticia |
| texto_lematizado | Contenido transformado mediante lematización |
| criticidad | Índice calculado mediante palabras críticas |
| sentimiento | Valor entre -1.0 y 1.0 generado por el LLM |
| categoria_predicha | Categoría generada mediante Ollama |
| categoria_ml | Categoría generada mediante LinearSVC |
| es_alerta | Indica si una noticia representa una alerta |
| nivel_alerta | Nivel asignado a la alerta |

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

Ingresar a la carpeta:

```bash
cd sistema-noticias-panama
```

---

## 2. Crear un entorno virtual

```bash
python -m venv venv
```

Activar en Windows:

```bash
venv\Scripts\activate
```

Activar en Linux o macOS:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Instalar el modelo de spaCy

```bash
python -m spacy download es_core_news_sm
```

---

## 5. Instalar Ollama

Descargar Ollama desde:

```text
https://ollama.com/download
```

Instalar el modelo:

```bash
ollama pull qwen3.5:0.8b
```

---

# Ejecución

## Ejecutar el pipeline completo

```bash
python -m pipeline.pipeline_main
```

El pipeline completo ejecuta:

```text
Web scraping
       ↓
Ingesta
       ↓
Limpieza
       ↓
Transformación
       ↓
Machine Learning
       ↓
LLM
       ↓
Sistema de alertas
       ↓
Dataset final
```

---

## Ejecutar solamente Machine Learning

Para trabajar con el CSV previamente analizado:

```bash
python -m models.ml.predict_existing_csv
```

Esta es la opción recomendada cuando no se desea:

- Descargar noticias nuevamente.
- Ejecutar Ollama nuevamente.
- Generar nuevamente el análisis de sentimiento.
- Ejecutar todo el pipeline.

---

## Ejecutar el dashboard de Streamlit

```bash
streamlit run dashboard/streamlit_app.py
```

---

# Integración futura con Power BI

El archivo utilizado como fuente principal será:

```text
noticias_panama_ml.csv
```

El proyecto continuará con:

- Diseño de un modelo estrella.
- Creación de una tabla de hechos.
- Creación de dimensiones.
- Desarrollo de dashboards.
- Implementación de filtros interactivos.
- Ampliación de KPIs.
- Comparación de categorías.
- Análisis de medios.
- Análisis temporal.
- Análisis de sentimientos.
- Visualización de alertas.
- Comparación entre ML y LLM.

---

## KPIs propuestos

Los siguientes indicadores podrán utilizarse en Power BI:

- Total de noticias.
- Total de medios analizados.
- Noticias por categoría.
- Noticias por medio.
- Noticias positivas.
- Noticias negativas.
- Noticias neutrales.
- Porcentaje de noticias negativas.
- Cantidad de alertas.
- Cantidad de alertas altas.
- Nivel promedio de criticidad.
- Categoría con mayor número de noticias.
- Medio con mayor número de publicaciones.
- Promedio de palabras por noticia.
- Porcentaje de coincidencia entre ML y categoría original.
- Porcentaje de coincidencia entre ML y LLM.
- Noticias por fecha.
- Tendencia de sentimiento.
- Evolución de alertas.
- Categorías con mayor criticidad.

---

# Resultados obtenidos

El proyecto generó:

- Un dataset consolidado con noticias de medios panameños.
- Un proceso automatizado de limpieza.
- Un sistema de transformación y lematización.
- Un índice de criticidad.
- Clasificación mediante Machine Learning.
- Clasificación mediante un Modelo de Lenguaje de Gran Escala.
- Análisis de sentimiento.
- Sistema de alertas.
- Modelo LinearSVC entrenado.
- Métricas de evaluación.
- Matriz de confusión.
- Reporte de clasificación.
- Archivo consolidado preparado para Power BI.

---

# Estado actual

| Componente | Estado |
|---|---|
| Web scraping | Completado |
| Ingesta de datos | Completado |
| Limpieza | Completado |
| Transformación | Completado |
| Lematización | Completado |
| Índice de criticidad | Completado |
| Análisis mediante LLM | Completado |
| Análisis de sentimiento | Completado |
| Clasificación mediante LLM | Completado |
| Sistema de alertas | Completado |
| Machine Learning | Completado |
| Comparación de modelos | Completado |
| Evaluación del modelo | Completado |
| Modelo entrenado | Completado |
| Dataset consolidado | Completado |
| Modelo estrella | Pendiente |
| Dashboards de Power BI | Pendiente |
| Ampliación de KPIs | Pendiente |

---

# Posibles mejoras futuras

- Recopilar más noticias de tecnología.
- Recopilar más noticias de salud.
- Incorporar categorías de seguridad.
- Incorporar categorías de educación.
- Incorporar categorías de ambiente.
- Aumentar la cantidad de medios.
- Automatizar la actualización diaria.
- Implementar una base de datos.
- Desarrollar un chatbot para consultar las noticias.
- Generar resúmenes automáticos.
- Comparar el desempeño del ML y el LLM.
- Implementar modelos especializados en español.
- Incorporar análisis geográfico.
- Identificar provincias y ubicaciones.
- Analizar tendencias por periodo.
- Implementar actualización automática del modelo.

---

# Integrantes

- Calderón, Ovidio
- Fu, Winson
- Huertas, José
- Luo, Anie
- Takata, Gabriela

---

# Curso

Gestión de la Información

Facultad de Ingeniería de Sistemas Computacionales

Universidad Tecnológica de Panamá

I Semestre 2026

---

# Estado del proyecto

Proyecto en desarrollo.

Las etapas de recopilación, procesamiento, Machine Learning, análisis mediante LLM y generación del dataset consolidado se encuentran completadas.

Las siguientes etapas corresponden al diseño del modelo estrella, desarrollo de dashboards en Power BI y ampliación de indicadores.