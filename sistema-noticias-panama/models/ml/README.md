# Módulo de Machine Learning

Este módulo entrena y utiliza un clasificador supervisado multiclase para predecir la categoría temática de noticias panameñas.

## Enfoque

- Entrada: título y texto de la noticia.
- Representación: TF-IDF con unigramas y bigramas.
- Modelos comparados: LinearSVC, Logistic Regression y Complement Naive Bayes.
- Criterio de selección: mayor F1 macro.
- Salida del pipeline: `categoria_ml`.

Las categorías con menos de 30 registros se excluyen del entrenamiento. La columna `categoria_original` no se modifica.

## Entrenar el modelo

Desde la raíz del proyecto:

```bash
python -m models.ml.train_category_model
```

El entrenamiento genera:

```text
models/ml/artifacts/category_classifier.joblib
models/ml/metrics/model_comparison.csv
models/ml/metrics/classification_report.csv
models/ml/metrics/confusion_matrix.csv
models/ml/metrics/model_metrics.json
```

## Dependencias

Agregar a `requirements.txt`:

```text
scikit-learn==1.8.0
joblib==1.5.3
```

## Uso desde el pipeline

```python
from models.ml import predecir_categorias_ml

transformed_data = transform_data(cleaned_data)
ml_data = predecir_categorias_ml(transformed_data)
```
