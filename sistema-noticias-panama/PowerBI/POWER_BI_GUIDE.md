# Guía de implementación del modelo estrella y dashboard en Power BI

## Sistema Inteligente de Análisis de Noticias de Panamá

---

# 1. Objetivo

Esta guía describe el proceso para importar, transformar y modelar la información generada por el Sistema Inteligente de Análisis de Noticias de Panamá dentro de Power BI.

El objetivo es construir un modelo estrella que facilite:

- El análisis de noticias por medio.
- El análisis de categorías.
- La comparación entre categorías originales, categorías generadas mediante Machine Learning y categorías generadas mediante el LLM.
- El análisis de sentimiento.
- La identificación de noticias críticas.
- El seguimiento de alertas.
- La creación de indicadores clave de rendimiento.
- El desarrollo de dashboards interactivos.

---

# 2. Dataset que debe utilizarse

El archivo que debe utilizarse como fuente principal del dashboard es:

```text
data/processed/noticias_panama_analizadas_ml.csv
```

Este archivo corresponde al dataset consolidado final del proyecto.

El archivo ya contiene los resultados de:

- Web scraping.
- Limpieza.
- Normalización.
- Transformación.
- Lematización.
- Cálculo de criticidad.
- Clasificación mediante Machine Learning.
- Clasificación mediante el Modelo de Lenguaje de Gran Escala.
- Análisis de sentimiento.
- Sistema de alertas.

No debe utilizarse como fuente principal:

```text
noticias_panama_procesadas.csv
```

debido a que este archivo no contiene todos los resultados del análisis.

Tampoco debe utilizarse:

```text
noticias_panama_analizadas.csv
```

debido a que todavía no contiene la columna:

```text
categoria_ml
```

Por lo tanto, el archivo oficial para Power BI es:

```text
noticias_panama_analizadas_ml.csv
```

---

# 3. Variables esperadas

El archivo debe contener columnas similares a las siguientes:

| Columna | Descripción |
|---|---|
| medio | Medio digital que publicó la noticia |
| titulo | Título de la noticia |
| fecha | Fecha de publicación |
| categoria_original | Categoría obtenida directamente del medio |
| texto | Resumen o contenido de la noticia |
| url | Enlace original |
| cantidad_palabras | Cantidad de palabras encontradas |
| texto_lematizado | Texto procesado mediante lematización |
| criticidad | Índice calculado mediante conceptos críticos |
| sentimiento | Valor de sentimiento generado mediante el LLM |
| categoria_predicha | Categoría generada mediante el LLM |
| es_alerta | Indica si la noticia fue clasificada como alerta |
| nivel_alerta | Nivel asignado a la alerta |
| categoria_ml | Categoría generada mediante Machine Learning |

La columna:

```text
categoria_predicha
```

representa la categoría generada mediante el LLM.

La columna:

```text
categoria_ml
```

representa la categoría generada mediante el modelo:

```text
TF-IDF + LinearSVC
```

---

# 4. Importar el archivo en Power BI

## Paso 1. Abrir Power BI

Abrir:

```text
Power BI Desktop
```

---

## Paso 2. Importar el CSV

Seleccionar:

```text
Home
→ Get data
→ Text/CSV
```

Buscar el archivo:

```text
noticias_panama_analizadas_ml.csv
```

Seleccionarlo y presionar:

```text
Transform Data
```

No seleccionar inmediatamente:

```text
Load
```

Es recomendable revisar primero los datos en Power Query.

---

# 5. Preparar los datos en Power Query

Al abrir Power Query, cambiar el nombre de la consulta original a:

```text
StgNoticias
```

El prefijo:

```text
Stg
```

significa:

```text
Staging
```

Esta consulta funcionará como la tabla base desde la cual se crearán las tablas del modelo estrella.

La consulta original no debe utilizarse directamente en las visualizaciones.

---

## 5.1. Verificar los tipos de datos

Revisar que las columnas tengan los siguientes tipos:

| Columna | Tipo recomendado |
|---|---|
| medio | Text |
| titulo | Text |
| fecha | Date |
| categoria_original | Text |
| texto | Text |
| url | Text |
| cantidad_palabras | Whole Number |
| texto_lematizado | Text |
| criticidad | Whole Number |
| sentimiento | Decimal Number |
| categoria_predicha | Text |
| es_alerta | True/False |
| nivel_alerta | Whole Number |
| categoria_ml | Text |

La columna:

```text
fecha
```

debe tener el tipo:

```text
Date
```

No debe quedar como:

```text
Text
```

---

## 5.2. Limpiar valores de texto

Seleccionar las siguientes columnas:

```text
medio
categoria_original
categoria_predicha
categoria_ml
```

Luego seleccionar:

```text
Transform
→ Format
→ Trim
```

Después:

```text
Transform
→ Format
→ Clean
```

Esto elimina espacios innecesarios y caracteres ocultos.

---

## 5.3. Crear una clasificación de sentimiento

La columna:

```text
sentimiento
```

contiene valores numéricos entre:

```text
-1.0 y 1.0
```

Para facilitar la creación de gráficos, agregar una nueva columna.

Seleccionar:

```text
Add Column
→ Conditional Column
```

Nombre:

```text
tipo_sentimiento
```

Utilizar las siguientes reglas:

| Condición | Resultado |
|---|---|
| sentimiento < 0 | Negativo |
| sentimiento = 0 | Neutral |
| sentimiento > 0 | Positivo |

La lógica esperada es:

```text
Valor menor que 0
→ Negativo

Valor igual a 0
→ Neutral

Valor mayor que 0
→ Positivo
```

---

## 5.4. Crear una descripción del nivel de alerta

Agregar otra columna mediante:

```text
Add Column
→ Conditional Column
```

Nombre:

```text
descripcion_alerta
```

Reglas:

| nivel_alerta | Descripción |
|---:|---|
| 0 | Sin alerta |
| 1 | Alerta baja |
| 2 | Alerta media |
| 3 | Alerta alta |

---

## 5.5. Crear columnas de comparación

Agregar una nueva columna:

```text
coincide_ml_original
```

Seleccionar:

```text
Add Column
→ Custom Column
```

Utilizar:

```powerquery
if [categoria_ml] = [categoria_original]
then "Sí"
else "No"
```

Agregar:

```text
coincide_llm_original
```

Código:

```powerquery
if [categoria_predicha] = [categoria_original]
then "Sí"
else "No"
```

Agregar:

```text
coincide_ml_llm
```

Código:

```powerquery
if [categoria_ml] = [categoria_predicha]
then "Sí"
else "No"
```

Estas columnas permitirán comparar los resultados de las clasificaciones.

---

# 6. Diseño del modelo estrella

El modelo estará compuesto por:

```text
Una tabla de hechos

Varias tablas de dimensiones
```

La tabla central será:

```text
FactNoticias
```

Las dimensiones serán:

```text
DimFecha

DimMedio

DimCategoriaOriginal

DimCategoriaML

DimCategoriaLLM

DimSentimiento

DimAlerta
```

---

# 7. Estructura del modelo

```text
                         DimFecha
                             │
                             │
                             ▼

DimMedio ─────────────► FactNoticias ◄──────────── DimSentimiento

                             ▲

                             │

       DimCategoriaOriginal ─┤

       DimCategoriaML ───────┤

       DimCategoriaLLM ──────┤

       DimAlerta ────────────┘
```

La tabla:

```text
FactNoticias
```

debe estar en el centro.

Las dimensiones deben encontrarse alrededor.

---

# 8. Crear la tabla FactNoticias

Hacer clic derecho sobre:

```text
StgNoticias
```

Seleccionar:

```text
Reference
```

Cambiar el nombre de la nueva consulta a:

```text
FactNoticias
```

Mantener las columnas necesarias.

Columnas recomendadas:

```text
titulo

fecha

medio

categoria_original

categoria_ml

categoria_predicha

tipo_sentimiento

sentimiento

criticidad

cantidad_palabras

es_alerta

nivel_alerta

descripcion_alerta

coincide_ml_original

coincide_llm_original

coincide_ml_llm

texto

url
```

La columna:

```text
texto_lematizado
```

puede eliminarse de Power BI.

No es necesaria para los dashboards y puede aumentar el tamaño del modelo.

---

## Crear un identificador

Seleccionar:

```text
Add Column
→ Index Column
→ From 1
```

Cambiar el nombre a:

```text
IdNoticia
```

Este será el identificador único de cada noticia.

---

# 9. Crear DimMedio

Hacer clic derecho sobre:

```text
StgNoticias
```

Seleccionar:

```text
Reference
```

Cambiar el nombre a:

```text
DimMedio
```

Mantener únicamente:

```text
medio
```

Seleccionar:

```text
Home
→ Remove Rows
→ Remove Duplicates
```

Agregar:

```text
Add Column
→ Index Column
→ From 1
```

Cambiar el nombre a:

```text
IdMedio
```

El resultado debe ser similar a:

| IdMedio | medio |
|---:|---|
| 1 | TVN |
| 2 | Telemetro |
| 3 | La Prensa |

---

# 10. Crear DimCategoriaOriginal

Crear una nueva referencia desde:

```text
StgNoticias
```

Nombrarla:

```text
DimCategoriaOriginal
```

Mantener:

```text
categoria_original
```

Eliminar duplicados.

Agregar un índice:

```text
IdCategoriaOriginal
```

---

# 11. Crear DimCategoriaML

Crear una nueva referencia.

Nombre:

```text
DimCategoriaML
```

Mantener:

```text
categoria_ml
```

Eliminar duplicados.

Agregar:

```text
IdCategoriaML
```

---

# 12. Crear DimCategoriaLLM

Crear una nueva referencia.

Nombre:

```text
DimCategoriaLLM
```

Mantener:

```text
categoria_predicha
```

Eliminar duplicados.

Agregar:

```text
IdCategoriaLLM
```

La dimensión representa las categorías generadas mediante Ollama.

---

# 13. Crear DimSentimiento

Crear una nueva referencia.

Nombre:

```text
DimSentimiento
```

Mantener:

```text
tipo_sentimiento
```

Eliminar duplicados.

Agregar:

```text
IdSentimiento
```

La tabla debe contener:

| IdSentimiento | tipo_sentimiento |
|---:|---|
| 1 | Negativo |
| 2 | Neutral |
| 3 | Positivo |

---

# 14. Crear DimAlerta

Crear una referencia.

Nombre:

```text
DimAlerta
```

Mantener:

```text
nivel_alerta

descripcion_alerta
```

Eliminar duplicados.

La tabla esperada es:

| nivel_alerta | descripcion_alerta |
|---:|---|
| 0 | Sin alerta |
| 1 | Alerta baja |
| 2 | Alerta media |
| 3 | Alerta alta |

---

# 15. Crear DimFecha

La tabla de fechas puede crearse directamente mediante DAX.

Seleccionar:

```text
Modeling
→ New table
```

Escribir:

```DAX
DimFecha =
ADDCOLUMNS(
    CALENDAR(
        MIN(FactNoticias[fecha]),
        MAX(FactNoticias[fecha])
    ),
    "Año", YEAR([Date]),
    "MesNumero", MONTH([Date]),
    "Mes", FORMAT([Date], "MMMM"),
    "AñoMes", FORMAT([Date], "YYYY-MM"),
    "Trimestre", "T" & FORMAT([Date], "Q"),
    "Dia", DAY([Date]),
    "DiaSemanaNumero", WEEKDAY([Date], 2),
    "DiaSemana", FORMAT([Date], "dddd")
)
```

Seleccionar:

```text
Table tools
→ Mark as date table
```

Escoger:

```text
Date
```

---

## Ordenar los meses

Seleccionar:

```text
DimFecha[Mes]
```

Después:

```text
Column tools
→ Sort by column
→ MesNumero
```

Esto evita que Power BI ordene los meses alfabéticamente.

---

# 16. Relaciones del modelo

Ir a:

```text
Model view
```

Crear las relaciones.

---

## Relación de fecha

```text
DimFecha[Date]

1 → *

FactNoticias[fecha]
```

---

## Relación de medio

```text
DimMedio[medio]

1 → *

FactNoticias[medio]
```

---

## Relación de categoría original

```text
DimCategoriaOriginal[categoria_original]

1 → *

FactNoticias[categoria_original]
```

---

## Relación de categoría ML

```text
DimCategoriaML[categoria_ml]

1 → *

FactNoticias[categoria_ml]
```

---

## Relación de categoría LLM

```text
DimCategoriaLLM[categoria_predicha]

1 → *

FactNoticias[categoria_predicha]
```

---

## Relación de sentimiento

```text
DimSentimiento[tipo_sentimiento]

1 → *

FactNoticias[tipo_sentimiento]
```

---

## Relación de alerta

```text
DimAlerta[nivel_alerta]

1 → *

FactNoticias[nivel_alerta]
```

---

# 17. Configuración correcta de relaciones

Todas las relaciones deben utilizar:

```text
Cardinality:

One to many
```

La dimensión debe encontrarse en el lado:

```text
1
```

La tabla de hechos debe encontrarse en el lado:

```text
*
```

Configurar:

```text
Cross-filter direction:

Single
```

Evitar:

```text
Both
```

excepto cuando exista una justificación específica.

---

# 18. Resultado esperado

El modelo debe verse aproximadamente así:

```text
               DimFecha

                   │

                   │

                   ▼

DimMedio ───► FactNoticias ◄─── DimSentimiento

                   ▲

                   │

 DimCategoriaOriginal

                   │

     DimCategoriaML

                   │

    DimCategoriaLLM

                   │

             DimAlerta
```

---

# 19. Ocultar la tabla StgNoticias

Después de completar el modelo:

Hacer clic derecho sobre:

```text
StgNoticias
```

Seleccionar:

```text
Hide in report view
```

La tabla debe mantenerse como fuente de Power Query, pero no debe utilizarse en visualizaciones.

---

# 20. Medidas DAX

Crear una tabla exclusiva para las medidas.

Seleccionar:

```text
Home
→ Enter data
```

Crear una columna vacía.

Nombrar la tabla:

```text
Medidas
```

Las medidas se almacenarán dentro de esta tabla.

---

## Total de noticias

```DAX
Total Noticias =
COUNTROWS(FactNoticias)
```

---

## Total de medios

```DAX
Total Medios =
DISTINCTCOUNT(FactNoticias[medio])
```

---

## Noticias positivas

```DAX
Noticias Positivas =
CALCULATE(
    [Total Noticias],
    FactNoticias[tipo_sentimiento] = "Positivo"
)
```

---

## Noticias negativas

```DAX
Noticias Negativas =
CALCULATE(
    [Total Noticias],
    FactNoticias[tipo_sentimiento] = "Negativo"
)
```

---

## Noticias neutrales

```DAX
Noticias Neutrales =
CALCULATE(
    [Total Noticias],
    FactNoticias[tipo_sentimiento] = "Neutral"
)
```

---

## Porcentaje de noticias negativas

```DAX
Porcentaje Noticias Negativas =
DIVIDE(
    [Noticias Negativas],
    [Total Noticias],
    0
)
```

Configurar el formato como:

```text
Percentage
```

---

## Promedio de sentimiento

```DAX
Promedio Sentimiento =
AVERAGE(
    FactNoticias[sentimiento]
)
```

---

## Criticidad promedio

```DAX
Criticidad Promedio =
AVERAGE(
    FactNoticias[criticidad]
)
```

---

## Criticidad máxima

```DAX
Criticidad Máxima =
MAX(
    FactNoticias[criticidad]
)
```

---

## Total de alertas

```DAX
Total Alertas =
CALCULATE(
    [Total Noticias],
    FactNoticias[es_alerta] = TRUE()
)
```

---

## Porcentaje de alertas

```DAX
Porcentaje Alertas =
DIVIDE(
    [Total Alertas],
    [Total Noticias],
    0
)
```

Configurar como:

```text
Percentage
```

---

## Alertas altas

```DAX
Alertas Altas =
CALCULATE(
    [Total Noticias],
    FactNoticias[nivel_alerta] = 3
)
```

---

## Alertas medias

```DAX
Alertas Medias =
CALCULATE(
    [Total Noticias],
    FactNoticias[nivel_alerta] = 2
)
```

---

## Alertas bajas

```DAX
Alertas Bajas =
CALCULATE(
    [Total Noticias],
    FactNoticias[nivel_alerta] = 1
)
```

---

## Promedio de palabras

```DAX
Promedio Palabras =
AVERAGE(
    FactNoticias[cantidad_palabras]
)
```

---

# 21. Métricas de comparación entre ML, LLM y categoría original

## Coincidencias entre ML y categoría original

```DAX
Coincidencias ML Original =
CALCULATE(
    [Total Noticias],
    FactNoticias[coincide_ml_original] = "Sí"
)
```

---

## Porcentaje de coincidencia ML

```DAX
Porcentaje Coincidencia ML =
DIVIDE(
    [Coincidencias ML Original],
    [Total Noticias],
    0
)
```

Formatear como porcentaje.

---

## Coincidencias entre LLM y categoría original

```DAX
Coincidencias LLM Original =
CALCULATE(
    [Total Noticias],
    FactNoticias[coincide_llm_original] = "Sí"
)
```

---

## Porcentaje de coincidencia LLM

```DAX
Porcentaje Coincidencia LLM =
DIVIDE(
    [Coincidencias LLM Original],
    [Total Noticias],
    0
)
```

---

## Coincidencias entre ML y LLM

```DAX
Coincidencias ML LLM =
CALCULATE(
    [Total Noticias],
    FactNoticias[coincide_ml_llm] = "Sí"
)
```

---

## Porcentaje de coincidencia entre ML y LLM

```DAX
Porcentaje Coincidencia ML LLM =
DIVIDE(
    [Coincidencias ML LLM],
    [Total Noticias],
    0
)
```

---

# 22. Consideración importante sobre las métricas

El porcentaje de coincidencia calculado en Power BI no debe presentarse como la exactitud oficial del modelo.

El modelo fue evaluado utilizando un conjunto separado de prueba.

Las métricas oficiales son:

```text
Accuracy:

81.20 %

F1 Macro:

81.64 %

F1 ponderado:

81.07 %
```

El porcentaje calculado dentro del dashboard representa:

```text
Coincidencia entre las categorías existentes en el dataset
```

No representa una nueva evaluación independiente.

---

# 23. Dashboards recomendados

Se recomienda crear cuatro páginas.

---

# Página 1. Resumen general

Nombre:

```text
Resumen General
```

KPIs:

```text
Total Noticias

Total Medios

Noticias Negativas

Total Alertas

Criticidad Promedio
```

Visualizaciones:

- Noticias por medio.
- Noticias por fecha.
- Distribución del sentimiento.
- Noticias por categoría original.
- Segmentadores.

Filtros recomendados:

```text
Fecha

Medio

Categoría original

Tipo de sentimiento
```

---

# Página 2. Categorías y modelos

Nombre:

```text
Clasificación ML y LLM
```

KPIs:

```text
Porcentaje Coincidencia ML

Porcentaje Coincidencia LLM

Porcentaje Coincidencia ML LLM
```

Visualizaciones:

- Categorías originales.
- Categorías generadas mediante ML.
- Categorías generadas mediante LLM.
- Comparación entre ML y LLM.
- Tabla detallada de resultados.

Tabla recomendada:

```text
Título

Categoría original

Categoría ML

Categoría LLM

Coincide ML

Coincide LLM
```

---

# Página 3. Sentimiento

Nombre:

```text
Análisis de Sentimiento
```

KPIs:

```text
Noticias Positivas

Noticias Negativas

Noticias Neutrales

Promedio Sentimiento

Porcentaje Noticias Negativas
```

Visualizaciones:

- Distribución del sentimiento.
- Sentimiento por medio.
- Sentimiento por categoría.
- Evolución temporal.
- Promedio del sentimiento por medio.

---

# Página 4. Alertas y criticidad

Nombre:

```text
Alertas y Criticidad
```

KPIs:

```text
Total Alertas

Alertas Altas

Alertas Medias

Alertas Bajas

Criticidad Promedio

Criticidad Máxima
```

Visualizaciones:

- Alertas por nivel.
- Alertas por medio.
- Alertas por categoría.
- Evolución de alertas.
- Noticias con mayor criticidad.

Tabla:

```text
Título

Medio

Fecha

Criticidad

Sentimiento

Nivel de alerta

URL
```

---

# 24. Visualizaciones recomendadas

| Información | Visual recomendado |
|---|---|
| Total de noticias | Card |
| Total de alertas | Card |
| Noticias por medio | Clustered Column Chart |
| Noticias por categoría | Bar Chart |
| Distribución del sentimiento | Donut Chart |
| Noticias por fecha | Line Chart |
| Alertas por nivel | Column Chart |
| Criticidad por categoría | Bar Chart |
| Comparación ML y LLM | Matrix |
| Detalle de noticias | Table |
| Filtros | Slicer |

---

# 25. Segmentadores recomendados

Agregar:

```text
Fecha

Medio

Categoría original

Categoría ML

Categoría LLM

Tipo de sentimiento

Nivel de alerta
```

Se recomienda sincronizar los principales filtros mediante:

```text
View
→ Sync slicers
```

---

# 26. Diseño visual

Mantener una estructura limpia.

Recomendaciones:

- Utilizar un título por página.
- Mantener los KPIs en la parte superior.
- Colocar los filtros en el lado izquierdo o superior.
- Utilizar el mismo estilo en todas las páginas.
- Evitar utilizar demasiados colores.
- Evitar gráficos 3D.
- Mantener títulos claros.
- No sobrecargar las páginas.
- Mantener alineadas las visualizaciones.
- Utilizar el mismo formato para los números.

---

# 27. Verificaciones antes de entregar

Comprobar:

- El archivo utilizado es:

```text
noticias_panama_analizadas_ml.csv
```

- La columna:

```text
categoria_ml
```

existe.

- La columna:

```text
fecha
```

tiene tipo Date.

- No existen relaciones muchos a muchos.

- Las relaciones utilizan:

```text
One to many
```

- La dirección de filtro es:

```text
Single
```

- La tabla:

```text
FactNoticias
```

se encuentra en el centro.

- Las dimensiones se encuentran alrededor.

- La tabla:

```text
StgNoticias
```

está oculta.

- Las medidas utilizan DAX.

- Los filtros funcionan.

- Las tarjetas cambian al utilizar segmentadores.

- Los gráficos responden correctamente a los filtros.

- Los nombres de las visualizaciones son claros.

---

# 28. Resultado esperado

Al finalizar, Power BI debe incluir:

```text
Modelo estrella

Tabla de hechos

Dimensiones

Relaciones uno a muchos

Medidas DAX

KPIs

Filtros

Dashboard general

Dashboard de sentimiento

Dashboard de alertas

Dashboard de comparación entre ML y LLM
```

---

# 29. Resumen del flujo

```text
noticias_panama_analizadas_ml.csv

               ↓

Power Query

               ↓

Limpieza y transformación

               ↓

StgNoticias

               ↓

Modelo estrella

               ↓

FactNoticias

               ↓

Dimensiones

               ↓

Relaciones

               ↓

Medidas DAX

               ↓

KPIs

               ↓

Dashboards interactivos
```

---

# 30. Estado

| Componente | Estado |
|---|---|
| Dataset final | Completado |
| Machine Learning | Completado |
| Análisis mediante LLM | Completado |
| Análisis de sentimiento | Completado |
| Sistema de alertas | Completado |
| Archivo para Power BI | Completado |
| Modelo estrella | Pendiente de implementación |
| Medidas DAX | Pendiente de implementación |
| KPIs | Pendiente de implementación |
| Dashboards | Pendiente de implementación |

---

# Archivo oficial para Power BI

```text
data/processed/noticias_panama_analizadas_ml.csv
```

Este archivo debe utilizarse para construir el modelo estrella y todos los dashboards.