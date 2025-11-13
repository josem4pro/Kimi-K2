# OKimi - OpenRouter Wrapper para Kimi K2 Thinking

Wrapper CLI para acceder a Kimi K2 Thinking vía OpenRouter, proporcionando acceso unificado a 100+ modelos LLM con una sola API key.

## ¿Por qué OpenRouter?

OpenRouter es un **agregador de proveedores LLM** que te da acceso a modelos de:
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini)
- Meta (Llama)
- Moonshot AI (Kimi K2)
- Y 100+ modelos más

**Ventajas**:
- ✅ Una sola API key para todos los modelos
- ✅ Fallback automático si un modelo falla
- ✅ Selección automática del proveedor más barato
- ✅ Rankings y analytics en openrouter.ai
- ✅ Compatible con OpenAI SDK

## Diferencia: kimi vs okimi

| Característica | `kimi` (Chutes.ai) | `okimi` (OpenRouter) |
|----------------|-------------------|---------------------|
| **Provider** | Chutes.ai descentralizado | OpenRouter agregador |
| **Endpoint** | llm.chutes.ai | openrouter.ai |
| **Modelos** | Kimi K2 especializado | 100+ modelos disponibles |
| **Infraestructura** | Descentralizada (Bittensor) | Centralizada multi-proveedor |
| **Precio** | $0.60/$2.50 por 1M tokens | $0.60/$2.50 por 1M tokens |
| **Use case** | Kimi K2 optimizado | Experimentación multi-modelo |

**Ambos acceden al mismo modelo**: `moonshotai/kimi-k2-thinking`

## Instalación

### Ya instalado en:
- ✅ RTX (192.168.0.103)
- ✅ Lenovo (192.168.0.198)

### Instalación manual (si es necesario):

```bash
# 1. Obtener API key de OpenRouter
# Ir a: https://openrouter.ai/keys
# Crear nueva key y copiarla

# 2. Agregar a ~/.env
echo 'OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.env

# 3. Instalar script
cp ~/Kimi-K2/okimi_cli.py ~/.local/bin/okimi
chmod +x ~/.local/bin/okimi

# 4. Agregar aliases a ~/.bash_aliases
cat >> ~/.bash_aliases << 'EOF'
alias okimi='~/.local/bin/okimi'
alias okimis='okimi --simple'
alias okimih='okimi --heavy'
EOF

# 5. Recargar shell
source ~/.bashrc
```

## Uso

### Comandos disponibles:

```bash
# Modo interactivo
okimi

# Comando único
okimi "¿Qué es un grafo de conocimiento?"

# Simple mode (respuesta rápida)
okimis "Define MoE en 2 líneas"

# Heavy mode (8 trayectorias paralelas)
okimih "Diseña una arquitectura completa de sistema distribuido multi-agente"
```

### Ejemplos de uso:

#### 1. Pregunta simple

```bash
$ okimi "¿Cuál es la diferencia entre Kimi K1.5 y K2?"

╔═══════════════════════════════════════════════════════════╗
║              KIMI K2 THINKING (OpenRouter)                ║
║              Moonshot AI - Open Agentic Intelligence      ║
╚═══════════════════════════════════════════════════════════╝

✓ API Key cargada: sk-or-v1-423499fd...
✓ Cliente configurado: openrouter.ai
✓ Modelo listo: Kimi K2 Thinking (OpenRouter)
📊 Capacidades activas:
   • Contexto: 256K tokens
   • Tool-calling: Deshabilitado (respuesta directa)
   • Max tokens: 16384
   • Temperature: 0.3
   • Provider: OpenRouter

🤔 Procesando...

═══ RESPUESTA ═══
[Respuesta detallada del modelo...]

═══ USO DE TOKENS ═══
  Input: 45 tokens
  Output: 523 tokens
  Total: 568 tokens
  Costo estimado: $0.001335 USD
```

#### 2. Modo interactivo

```bash
$ okimi

╔═══════════════════════════════════════════════════════════╗
║              KIMI K2 THINKING (OpenRouter)                ║
╚═══════════════════════════════════════════════════════════╝

💬 Modo interactivo activado
Escribe 'salir', 'exit' o 'quit' para terminar
Escribe 'heavy: tu pregunta' para usar Heavy Mode

Tú ➜ ¿Qué es OpenRouter?
[Respuesta...]

Tú ➜ heavy: Compara OpenRouter vs Chutes.ai para Kimi K2
⚡ Heavy Mode activado: 8 trayectorias paralelas
[Respuesta exhaustiva...]

Tú ➜ salir
👋 ¡Hasta pronto!
```

#### 3. Heavy Mode para diseño de sistemas

```bash
$ okimih "Diseña una arquitectura de sistema multi-agente con memoria distribuida, considerando: escalabilidad horizontal, fault tolerance, consistencia eventual, y latencia <100ms"

⚡ Heavy Mode activado: 8 trayectorias paralelas

[Respuesta exhaustiva explorando 8 enfoques diferentes...]
```

## Comparación de Modos

### Simple Mode (`okimis`)

**Cuándo usar**:
- Definiciones rápidas
- Preguntas directas
- Verificaciones simples

**Características**:
- Max tokens: 1,000
- Temperature: 0.1 (más determinista)
- Costo: ~$0.001-0.003 USD
- Tiempo: ~5-15 segundos

**Ejemplo**:
```bash
okimis "Define MoE"
# → Respuesta: 2-3 párrafos concisos
```

### Normal Mode (`okimi`)

**Cuándo usar**:
- Preguntas generales
- Explicaciones paso a paso
- Código y debugging
- Uso diario

**Características**:
- Max tokens: 16,384
- Temperature: 0.3 (balanceado)
- Costo: ~$0.006-0.015 USD
- Tiempo: ~10-30 segundos

**Ejemplo**:
```bash
okimi "¿Cómo implementar autenticación JWT en Express.js?"
# → Respuesta: Explicación paso a paso con código
```

### Heavy Mode (`okimih`)

**Cuándo usar**:
- Diseño de arquitecturas complejas
- Análisis exhaustivos
- Comparación de múltiples enfoques
- Problemas de investigación

**Características**:
- Max tokens: 16,384
- Temperature: 0.3
- **8 trayectorias paralelas** (beam search)
- Costo: ~$0.024-0.048 USD (3-4x más)
- Tiempo: ~30-90 segundos

**Ejemplo**:
```bash
okimih "Diseña una arquitectura completa de sistema distribuido..."
# → Respuesta: 8 enfoques explorados, pros/contras, recomendación final
```

## Gestión de Créditos en OpenRouter

### Ver créditos disponibles:

1. Ir a: https://openrouter.ai/credits
2. Ver balance actual
3. Recargar si es necesario

### Límites de uso:

OpenRouter tiene **rate limits** por nivel:
- **Free tier**: 10 requests/minuto
- **Paid tier**: 200 requests/minuto (con créditos)

### Monitoreo de costos:

Cada comando muestra el costo estimado:
```
Costo estimado: $0.001335 USD
```

## Troubleshooting

### Error: "OPENROUTER_API_KEY not configured"

**Solución**:
```bash
echo 'OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.env
```

### Error: "Insufficient credits"

**Solución**:
1. Ir a: https://openrouter.ai/credits
2. Agregar créditos (mínimo $5 USD recomendado)
3. Verificar: https://openrouter.ai/activity

### Error: "Model not found"

**Solución**:
Verificar que el modelo esté disponible:
```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | grep kimi
```

### Comparar con kimi (Chutes.ai)

Si tienes problemas con `okimi`, prueba con `kimi`:
```bash
# OpenRouter
okimi "prueba"

# Chutes.ai (alternativa)
kimi "prueba"
```

## Acceso a Otros Modelos

OpenRouter te da acceso a **100+ modelos**. Para usar otros:

### Ver modelos disponibles:

```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  | jq -r '.data[] | "\(.id) - \(.name)"'
```

### Modificar okimi para usar otro modelo:

Edita `~/.local/bin/okimi` (línea 156):

```python
config = {
    "model": "openai/gpt-4o",  # ← Cambiar aquí
    # ...
}
```

**Modelos recomendados**:
- `openai/gpt-4o` - GPT-4 Optimized
- `anthropic/claude-3.5-sonnet` - Claude 3.5
- `google/gemini-pro` - Gemini Pro
- `meta-llama/llama-3.1-405b` - Llama 3.1 405B
- `moonshotai/kimi-k2-thinking` - Kimi K2 (actual)

## Recursos

- **OpenRouter Dashboard**: https://openrouter.ai/dashboard
- **API Keys**: https://openrouter.ai/keys
- **Créditos**: https://openrouter.ai/credits
- **Activity Log**: https://openrouter.ai/activity
- **Modelos**: https://openrouter.ai/models
- **Docs**: https://openrouter.ai/docs

- **Kimi K2 GitHub**: https://github.com/moonshotai/Kimi-K2
- **Tech Report**: `~/Kimi-K2/tech_report.pdf`

## Comparación Final: kimi vs okimi

### Usa `kimi` (Chutes.ai) cuando:
- Solo necesites Kimi K2
- Quieras infraestructura descentralizada
- Experimentes con Bittensor

### Usa `okimi` (OpenRouter) cuando:
- Quieras acceso multi-modelo
- Necesites fallbacks automáticos
- Prefieras un agregador centralizado
- Quieras aparecer en rankings de OpenRouter

**Recomendación**: Usa ambos según el caso de uso. Los $20 USD que agregaste a OpenRouter te dan acceso a todos los modelos, no solo Kimi K2.

---

**Última actualización**: 2025-11-13
**Versión**: 1.0
**Instalado en**: RTX (192.168.0.103), Lenovo (192.168.0.198)
