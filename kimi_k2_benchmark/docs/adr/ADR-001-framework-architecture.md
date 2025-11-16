# ADR-001: Framework en Python Modular

## Status
Accepted

## Context
Necesitamos un framework de benchmarking que permita evaluar Kimi K2 (normal vs heavy mode) contra Qwen3-Coder:30B de forma reproducible y extensible.

## Decision
Implementar un framework en Python con estructura modular:

- `src/evaluator.py`: Bucle principal de benchmarks, llamadas a modelos
- `src/comparator.py`: Comparaciones entre modelos y cálculo de métricas
- `src/reporter.py`: Generación de reportes en Markdown/JSON/CSV

## Rationale
- Python es el estándar para ML/AI benchmarking
- Estructura modular permite testing unitario (TDD)
- Separación de responsabilidades facilita mantenimiento
- Compatible con ecosistema existente (Ollama, OpenAI-compatible APIs)

## Consequences
- Requiere implementar TDD antes de código de producción (BLOQUEANTE)
- Cada módulo debe tener interfaz clara y documentada
- Facilita extensión a nuevos modelos/benchmarks en el futuro
