# ADR-002: Estructura de Almacenamiento de Resultados

## Status
Accepted

## Context
Los resultados del benchmark deben ser persistentes, analizables y reproducibles.

## Decision
Estructura de directorios:
```
results/
├── raw/           # Resultados crudos en JSON/CSV
├── analysis/      # Notebooks Jupyter para análisis
└── visualizations/ # Gráficos y reportes finales
```

Formato de resultados crudos:
- JSON para datos estructurados con metadatos completos
- CSV para exportación y análisis tabular
- Nombres con timestamp y seed para reproducibilidad

## Rationale
- Separación clara entre datos crudos y análisis derivados
- JSON preserva toda la información (reasoning, metadatos)
- CSV facilita análisis con pandas/Excel
- Estructura permite versionado y comparación histórica

## Consequences
- Requiere esquema consistente para todos los resultados
- Notebooks deben ser autocontenidos y ejecutables
- Visualizaciones deben ser regenerables desde datos crudos
