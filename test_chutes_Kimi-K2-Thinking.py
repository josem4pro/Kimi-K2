from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv('/home/jose/.env')

api_key = os.getenv('CHUTES_API_KEY')
if not api_key:
    raise ValueError("CHUTES_API_KEY no encontrada")

print(f"✓ API Key cargada: {api_key[:20]}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://llm.chutes.ai/v1"
)

# Tools opcionales (búsqueda web simulada, puedes agregar más)
tools = [
    {
        "type": "function",
        "function": {
            "name": "buscar_informacion",
            "description": "Busca información en internet sobre un tema específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "Qué buscar (ej: 'sistemas multi-agente IA')"
                    }
                },
                "required": ["consulta"]
            }
        }
    }
]

try:
    response = client.chat.completions.create(
        model="moonshotai/Kimi-K2-Thinking",
        messages=[
            {"role": "system", "content": "Eres un experto en IA y sistemas complejos. Razona paso a paso."},
            {"role": "user", "content": "Explica cómo diseñar un sistema de memoria viviente distribuida con múltiples agentes IA que evoluciona dinámicamente."}
        ],
        max_tokens=4000,  # Respuestas largas (antes tenías 512)
        temperature=0.3,  # Precisión (0.0=muy preciso, 1.0=creativo)
        tools=tools,  # Activa tool-calling (opcional, remueve si no quieres)
        tool_choice="auto",  # Deja que K2 decida si usa tools
        # extra_body={"heavy_mode": True}  # Descomenta para Heavy Mode (8 respuestas paralelas)
    )
    
    message = response.choices[0].message
    
    print("\n=== RESPUESTA COMPLETA ===")
    print(json.dumps(message.content, indent=2, ensure_ascii=False))
    
    # Si usó tools (búsqueda, etc.)
    if message.tool_calls:
        print("\n=== TOOLS INVOCADAS ===")
        for tool in message.tool_calls:
            print(f"- {tool.function.name}: {tool.function.arguments}")
    
    # Info de uso
    if response.usage:
        print(f"\n=== TOKENS USADOS ===")
        print(f"Input: {response.usage.prompt_tokens}, Output: {response.usage.completion_tokens}")
    
except Exception as e:
    print(f"\nError: {e}")
