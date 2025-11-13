#!/usr/bin/env python3
"""
Servidor local para testing de Kimi K2 Thinking vía Chutes.ai API
Simula un endpoint local para desarrollo antes de deployar a infraestructura descentralizada
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import os
import requests
import json
from typing import Optional, List
from dotenv import load_dotenv
import asyncio

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Kimi K2 Thinking Local API",
    description="API local para testing de Kimi K2 vía Chutes.ai",
    version="1.0.0"
)

# Configuración
CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
CHUTES_BASE_URL = "https://api.chutes.ai/v1"
KIMI_K2_MODEL = "moonshot/kimi-k2-thinking"

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = KIMI_K2_MODEL
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Kimi K2 Thinking Local API",
        "version": "1.0.0",
        "model": KIMI_K2_MODEL,
        "chutes_api_configured": bool(CHUTES_API_KEY)
    }

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """
    Endpoint de chat compatible con OpenAI API
    Redirige peticiones a Chutes.ai API
    """

    if not CHUTES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="CHUTES_API_KEY not configured in .env"
        )

    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": request.model,
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": request.stream
    }

    try:
        # Hacer petición a Chutes.ai
        response = requests.post(
            f"{CHUTES_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            stream=request.stream,
            timeout=120
        )

        response.raise_for_status()

        if request.stream:
            # Streaming response
            async def generate():
                for line in response.iter_lines():
                    if line:
                        yield line + b'\n'

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            # Regular response
            return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Chutes.ai API: {str(e)}"
        )

@app.get("/v1/models")
async def list_models():
    """Listar modelos disponibles"""
    return {
        "object": "list",
        "data": [
            {
                "id": KIMI_K2_MODEL,
                "object": "model",
                "created": 1730000000,
                "owned_by": "moonshot-ai",
                "capabilities": ["chat", "reasoning", "tool-calls"]
            }
        ]
    }

@app.post("/test/simple")
async def simple_test(prompt: str = "Explica qué es Kimi K2 en 3 líneas"):
    """
    Endpoint de prueba simple para verificar conectividad
    """

    if not CHUTES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="CHUTES_API_KEY not configured"
        )

    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": KIMI_K2_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{CHUTES_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        return {
            "status": "success",
            "prompt": prompt,
            "response": result["choices"][0]["message"]["content"],
            "model": result["model"],
            "usage": result.get("usage", {})
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║   Kimi K2 Thinking - Local Development Server       ║
    ╚══════════════════════════════════════════════════════╝

    📍 Server: http://localhost:8080
    📖 Docs: http://localhost:8080/docs
    🧪 Test endpoint: http://localhost:8080/test/simple

    🔑 API Key: {"✅ Configured" if CHUTES_API_KEY else "❌ Missing"}
    🤖 Model: {KIMI_K2_MODEL}

    Usage example:

    curl -X POST http://localhost:8080/v1/chat/completions \\
      -H "Content-Type: application/json" \\
      -d '{{
        "model": "{KIMI_K2_MODEL}",
        "messages": [{{"role": "user", "content": "Hello!"}}]
      }}'

    Press Ctrl+C to stop server
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
