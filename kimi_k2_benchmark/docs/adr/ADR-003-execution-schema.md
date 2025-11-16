# ADR-003: Esquema de Ejecución y Metadatos

## Status
Accepted

## Context
Cada ejecución de benchmark debe ser rastreable y reproducible.

## Decision
Cada resultado de ejecución incluye:

```json
{
  "execution_id": "uuid",
  "timestamp": "ISO8601",
  "model_id": "kimi_k2_heavy | kimi_k2_normal | qwen3_coder_30b",
  "benchmark_id": "reasoning.multi_hop_puzzles.case_001",
  "config": {
    "max_tokens": 8000,
    "temperature": 0.3,
    "heavy_mode": true,
    "seed": 42
  },
  "input": {
    "prompt": "...",
    "system_prompt": "...",
    "context_tokens": 1500
  },
  "output": {
    "response": "...",
    "reasoning": "..." // Campo para cadena de razonamiento si disponible
  },
  "metrics": {
    "correctness": true,
    "time_to_first_token": 0.234,
    "tokens_per_second": 45.6,
    "total_time": 12.34,
    "output_tokens": 562
  },
  "heavy_mode_data": {
    "trajectories": [...], // 8 trayectorias si heavy_mode=true
    "hybridized_output": "...",
    "diversity_score": 0.75,
    "convergence_pattern": "majority"
  }
}
```

## Rationale
- UUID único permite rastreo preciso
- Timestamp ISO8601 para ordenamiento temporal
- Config completo permite reproducción exacta
- Separación input/output/metrics facilita análisis
- Campo reasoning captura cadena de pensamiento
- heavy_mode_data solo para Kimi en heavy mode

## Consequences
- Esquema debe ser validado (Pydantic/JSON Schema)
- Todos los módulos deben respetar este formato
- Permite análisis post-hoc de cualquier ejecución
