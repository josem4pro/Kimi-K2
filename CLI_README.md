# Kimi CLI - Wrapper de Línea de Comandos

Wrapper CLI completo para acceder a Kimi K2 Thinking desde la terminal con todas las capacidades activadas.

## Instalación

### 1. Instalación automática (recomendada)

```bash
# Desde el repositorio Kimi-K2
cd ~/Kimi-K2

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias (si no están instaladas)
pip install python-dotenv openai

# Copiar script a ~/.local/bin/
cp kimi_cli.py ~/.local/bin/kimi
chmod +x ~/.local/bin/kimi

# Verificar instalación
kimi --help
```

### 2. Configurar API Key

```bash
# Agregar API key a ~/.env (si no existe)
echo 'CHUTES_API_KEY="tu-api-key-aqui"' >> ~/.env

# Verificar que está configurada
grep CHUTES_API_KEY ~/.env
```

### 3. Configurar alias (opcional pero recomendado)

Agregar a `~/.bash_aliases`:

```bash
# Kimi K2 CLI aliases
alias kimis='kimi --simple'    # Modo simple (rápido)
alias kimih='kimi --heavy'     # Heavy mode (8 trayectorias)
```

Recargar shell:
```bash
source ~/.bashrc
```

## Uso

### Modo Interactivo

```bash
kimi
```

Esto inicia una sesión de conversación continua. Escribe tus preguntas y presiona Enter.

**Comandos especiales en modo interactivo**:
- `heavy: tu pregunta` - Activa Heavy Mode para esa pregunta
- `salir`, `exit`, `quit` - Termina la sesión
- `Ctrl+C` - Salir rápido

### Modo Comando Único

```bash
# Pregunta simple
kimi "¿Qué es Kimi K2 Thinking?"

# Con comillas si tiene caracteres especiales
kimi "Explica la arquitectura MoE en modelos LLM"
```

### Heavy Mode (8 trayectorias paralelas)

```bash
# Usando --heavy flag
kimi --heavy "Diseña una arquitectura completa de sistema multi-agente con memoria distribuida"

# Usando alias (más corto)
kimih "Diseña una arquitectura completa de sistema multi-agente con memoria distribuida"
```

**Cuándo usar Heavy Mode**:
- Problemas complejos de diseño de sistemas
- Razonamiento multi-paso profundo
- Análisis exhaustivos
- Cuando necesites explorar múltiples enfoques

**Nota**: Consume más tokens (~3-4x) pero produce razonamientos más completos.

### Simple Mode (respuestas rápidas)

```bash
# Usando --simple flag
kimi --simple "Resume en pocas palabras qué es K2 Thinking"

# Usando alias (más corto)
kimis "Resume en pocas palabras qué es K2 Thinking"
```

**Cuándo usar Simple Mode**:
- Preguntas directas
- Definiciones cortas
- Verificaciones rápidas
- Cuando no necesites razonamiento extendido

## Capacidades del CLI

### ✅ Activadas

- **Contexto extenso**: 256K tokens
- **Razonamiento extendido**: 200-300 pasos de pensamiento
- **Heavy Mode**: 8 trayectorias paralelas (opcional)
- **Respuestas exhaustivas**: Hasta 16,384 tokens de output
- **Transparencia**: Cadenas de pensamiento visibles
- **Modo interactivo**: Conversación continua

### 🔧 En desarrollo (deshabilitadas)

- **Tool-calling**: Búsqueda en internet
- **Ejecución de código**: Python sandboxed
- **Memoria distribuida**: Integración con Neo4j/Centro Consciente

**Nota**: Las tools están comentadas en el código (`kimi_cli.py:159-163`). Para habilitarlas, descomentar esas líneas cuando estén implementadas.

## Ejemplos de Uso

### Ejemplo 1: Consulta simple

```bash
$ kimi "¿Cuál es la diferencia entre Kimi K1.5 y K2?"

╔═══════════════════════════════════════════════════════════╗
║                  KIMI K2 THINKING                         ║
║              Moonshot AI - Open Agentic Intelligence      ║
╚═══════════════════════════════════════════════════════════╝

✓ API Key cargada: cpk_e070015df549...
✓ Cliente configurado: llm.chutes.ai
✓ Modelo listo: Kimi K2 Thinking
📊 Capacidades activas:
   • Contexto: 256K tokens
   • Tool-calling: Deshabilitado (respuesta directa)
   • Max tokens: 16384
   • Temperature: 0.3

🤔 Procesando...

═══ RESPUESTA ═══

[Respuesta detallada del modelo...]

═══ USO DE TOKENS ═══
  Input: 123 tokens
  Output: 456 tokens
  Total: 579 tokens
  Costo estimado: $0.001200 USD
```

### Ejemplo 2: Heavy Mode para diseño de sistemas

```bash
$ kimih "Diseña una arquitectura de sistema multi-agente con estas características: [...]"

⚡ Heavy Mode activado: 8 trayectorias paralelas

[Respuesta exhaustiva con múltiples enfoques explorados...]
```

### Ejemplo 3: Modo interactivo

```bash
$ kimi

╔═══════════════════════════════════════════════════════════╗
║                  KIMI K2 THINKING                         ║
╚═══════════════════════════════════════════════════════════╝

💬 Modo interactivo activado
Escribe 'salir', 'exit' o 'quit' para terminar
Escribe 'heavy: tu pregunta' para usar Heavy Mode

Tú ➜ ¿Qué es un grafo de conocimiento?
[Respuesta...]

Tú ➜ heavy: ¿Cómo implementarías uno distribuido?
⚡ Heavy Mode activado: 8 trayectorias paralelas
[Respuesta exhaustiva...]

Tú ➜ salir

👋 ¡Hasta pronto!
```

## Verificación de Instalación

Ejecuta el script de prueba incluido:

```bash
cd ~/Kimi-K2
./test_kimi_funcionamiento.sh
```

Este script verifica:
- ✓ Script kimi instalado y ejecutable
- ✓ Dependencias Python (dotenv, openai)
- ✓ Archivo .env con CHUTES_API_KEY
- ✓ Alias configurados (kimih, kimis)
- ✓ Funcionalidad básica del script

## Estructura del Código

```python
# kimi_cli.py estructura

1. Imports y configuración
   - dotenv, openai, sys, os
   - Clase Colors para terminal

2. Funciones principales
   - load_api_key(): Carga desde ~/.env
   - create_client(): Configura OpenAI client
   - get_tools(): Define herramientas (deshabilitadas)
   - query_kimi(): Core de la consulta

3. Modos de operación
   - interactive_mode(): Conversación continua
   - query_kimi(heavy_mode=True): Heavy Mode
   - query_kimi(simple_mode=True): Simple Mode

4. CLI entry point
   - main(): Parsea args y decide modo
```

## Configuración Avanzada

### Modificar parámetros por defecto

Edita `kimi_cli.py` (líneas 157-168):

```python
config = {
    "model": "moonshotai/Kimi-K2-Thinking",
    "max_tokens": 16384,      # ← Cambia aquí para respuestas más cortas/largas
    "temperature": 0.3,       # ← Ajusta creatividad (0.0-1.0)
}
```

### Habilitar tool-calling

Descomenta líneas 159-163 en `kimi_cli.py`:

```python
# "tools": get_tools(),
# "tool_choice": "auto",
```

**Nota**: Requiere implementar las funciones de las tools primero.

### Cambiar endpoint

Modifica `create_client()` (línea 114):

```python
client = OpenAI(
    api_key=api_key,
    base_url="https://llm.chutes.ai/v1"  # ← Cambiar aquí
)
```

## Troubleshooting

### Error: "CHUTES_API_KEY not configured"

**Causa**: No existe ~/.env o falta la key.

**Solución**:
```bash
echo 'CHUTES_API_KEY="tu-key-aqui"' >> ~/.env
```

### Error: "kimi: command not found"

**Causa**: Script no instalado en PATH.

**Solución**:
```bash
cp kimi_cli.py ~/.local/bin/kimi
chmod +x ~/.local/bin/kimi

# Verificar que ~/.local/bin está en PATH
echo $PATH | grep .local/bin

# Si no está, agregar a ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Causa**: Faltan dependencias Python.

**Solución**:
```bash
source ~/Kimi-K2/venv/bin/activate
pip install python-dotenv openai
```

### Problema: Respuestas muy cortas

**Causa**: `max_tokens` configurado bajo.

**Solución**: Edita `kimi_cli.py` línea 163:
```python
"max_tokens": 16384,  # Aumentar si es necesario
```

## Costos

Basado en pricing de Chutes.ai:

| Tipo de uso | Tokens aprox. | Costo por consulta |
|-------------|---------------|-------------------|
| Simple mode | 500-1,000 | $0.0015 - $0.003 |
| Normal | 2,000-5,000 | $0.006 - $0.015 |
| Heavy mode | 8,000-16,000 | $0.024 - $0.048 |

**Fórmula**:
- Input: $0.60 / 1M tokens
- Output: $2.50 / 1M tokens

## Benchmarks de Kimi K2

- **SWE-Bench Verified**: 71.3% (vs GPT-4: 54.6%)
- **HLE (Hard Logical Equivalence)**: 44.9% SOTA
- **Context**: 256K tokens
- **Architecture**: MoE 1T params (32B activos)

## Recursos

- **Docs locales**: `SETUP_LOCAL.md`, `tech_report.pdf`
- **GitHub Upstream**: https://github.com/moonshotai/Kimi-K2
- **Paper**: arXiv:2501.17055
- **Chutes Dashboard**: https://chutes.ai

---

**Última actualización**: 2025-11-13
**Versión**: 1.0
**Autor**: Jose M. (josem4pro)
