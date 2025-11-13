# Setup Local - Kimi K2 Thinking Development

Configuración para desarrollo local con Kimi K2 Thinking vía Chutes.ai API.

## Requisitos

- **Python**: 3.10+
- **Sistema**: Ubuntu 24.04 LTS (compatible con otras distros Linux)
- **RAM**: Mínimo 4GB (8GB+ recomendado)
- **API Key**: Cuenta activa en [Chutes.ai](https://chutes.ai)

## Instalación Rápida

```bash
# 1. Clonar repositorio
git clone git@github.com:josem4pro/Kimi-K2.git
cd Kimi-K2

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
echo 'CHUTES_API_KEY="tu-api-key-aqui"' > .env

# 5. Ejecutar servidor local
python kimi_k2_local_server.py
```

## Configuración Detallada

### 1. Obtener API Key de Chutes.ai

1. Registrarse en: https://chutes.ai
2. Ir a: Dashboard → API Keys
3. Crear nueva API key
4. Copiar la key (formato: `cpk_...`)

### 2. Configurar .env

```bash
# Crear archivo .env en la raíz del proyecto
cat > .env << EOF
CHUTES_API_KEY="cpk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
EOF

# Verificar permisos (solo usuario puede leer)
chmod 600 .env
```

### 3. Verificar instalación

```bash
# Activar entorno virtual
source venv/bin/activate

# Verificar CLI de Chutes
chutes --help

# Verificar dependencias
pip list | grep -E "chutes|fastapi|uvicorn|requests"
```

## Uso del Servidor Local

### Iniciar servidor

```bash
source venv/bin/activate
python kimi_k2_local_server.py
```

Esto inicia un servidor FastAPI en `http://localhost:8080` con:
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/
- **Test Simple**: http://localhost:8080/test/simple

### Endpoints disponibles

#### 1. Health Check
```bash
curl http://localhost:8080/
```

#### 2. Test Simple
```bash
curl -X POST "http://localhost:8080/test/simple?prompt=Explica%20Kimi%20K2"
```

#### 3. Chat Completion (Compatible OpenAI API)
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot/kimi-k2-thinking",
    "messages": [
      {"role": "user", "content": "¿Qué es Kimi K2?"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

#### 4. Streaming Response
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot/kimi-k2-thinking",
    "messages": [
      {"role": "user", "content": "Cuenta hasta 10"}
    ],
    "stream": true
  }'
```

### Integración con Python

```python
import requests

# Configuración
API_URL = "http://localhost:8080/v1/chat/completions"

# Petición
response = requests.post(
    API_URL,
    json={
        "model": "moonshot/kimi-k2-thinking",
        "messages": [
            {"role": "user", "content": "Hola, Kimi K2!"}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
)

# Resultado
result = response.json()
print(result["choices"][0]["message"]["content"])
```

## Características de Kimi K2 Thinking

- **Parámetros**: 1T total, 32B activos (MoE architecture)
- **Contexto**: 256K tokens
- **Capacidades**: Reasoning agentic, tool calls, coding
- **Benchmarks**: 71.3% en SWE-Bench (vs GPT-4: 54.6%)

## Troubleshooting

### Error: "CHUTES_API_KEY not configured"

**Solución**:
```bash
# Verificar que .env existe
cat .env

# Verificar que la key está cargada
source venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('CHUTES_API_KEY'))"
```

### Error: "Module 'chutes' not found"

**Solución**:
```bash
# Reinstalar dependencias
source venv/bin/activate
pip install -r requirements.txt
```

### Error de conexión a Chutes.ai

**Solución**:
```bash
# Verificar conectividad
curl -I https://api.chutes.ai/v1/models

# Verificar API key
curl https://api.chutes.ai/v1/models \
  -H "Authorization: Bearer $CHUTES_API_KEY"
```

## Scripts Adicionales

### test_chutes_Kimi-K2-Thinking.py

Script de prueba original para validar API:

```bash
source venv/bin/activate
python test_chutes_Kimi-K2-Thinking.py
```

## Recursos

- **Chutes.ai Docs**: https://chutes.ai/resources
- **Kimi K2 Tech Report**: `tech_report.pdf`
- **GitHub Repo**: https://github.com/josem4pro/Kimi-K2
- **Upstream**: https://github.com/moonshotai/Kimi-K2

## Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│  Cliente (curl, Python, browser)        │
└──────────────┬──────────────────────────┘
               │
               │ HTTP POST
               ▼
┌─────────────────────────────────────────┐
│  kimi_k2_local_server.py (FastAPI)      │
│  - Health checks                        │
│  - Request validation                   │
│  - Logging                              │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS + API Key
               ▼
┌─────────────────────────────────────────┐
│  Chutes.ai API (api.chutes.ai/v1)       │
│  - Load balancing                       │
│  - Descentralized compute               │
└──────────────┬──────────────────────────┘
               │
               │ Model inference
               ▼
┌─────────────────────────────────────────┐
│  Kimi K2 Thinking (MoE 1T params)       │
│  - 32B active parameters                │
│  - 256K context window                  │
│  - Tool calling support                 │
└─────────────────────────────────────────┘
```

## Next Steps

1. ✅ Setup local completado
2. 🔄 Explorar tool calling con Kimi K2
3. 🔄 Integrar con frameworks (LangChain, LlamaIndex)
4. 🔄 Deploy a producción vía `chutes deploy`
5. 🔄 CI/CD con GitHub Actions

---

**Última actualización**: 2025-11-13
**Autor**: Jose M. (josem4pro)
**License**: MIT
