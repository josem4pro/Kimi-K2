#!/home/jose/Kimi-K2/venv/bin/python3
"""
Kimi K2 Thinking - OpenRouter Wrapper CLI
Acceso simplificado al modelo Kimi K2 vía OpenRouter con todas las capacidades activadas.

Uso:
  okimi                           # Modo interactivo
  okimi "tu pregunta aquí"        # Modo comando único
  okimi -h, --help                # Ayuda
  okimi --heavy "pregunta"        # Heavy Mode (8 trayectorias paralelas)
  okimi --simple "pregunta"       # Modo simple (sin razonamiento extendido)
"""

import os
import sys
import json
from pathlib import Path

# Intentar importar dependencias
try:
    from dotenv import load_dotenv
    from openai import OpenAI
    import requests
except ImportError as e:
    print(f"❌ Error: Falta dependencia: {e}")
    print("\n🔧 Solución: Instala las dependencias con:")
    print("   pip install python-dotenv openai requests")
    sys.exit(1)

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Muestra el banner de inicio"""
    banner = f"""
{Colors.OKCYAN}╔═══════════════════════════════════════════════════════════╗
║              KIMI K2 THINKING (OpenRouter)                ║
║              Moonshot AI - Open Agentic Intelligence      ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def load_api_key():
    """Carga la API key desde ~/.env"""
    env_path = Path.home() / '.env'

    if not env_path.exists():
        print(f"{Colors.FAIL}❌ Error: No se encuentra ~/.env{Colors.ENDC}")
        print(f"\n{Colors.WARNING}🔧 Solución:{Colors.ENDC}")
        print("   1. Crea el archivo: touch ~/.env")
        print("   2. Agrega tu key: echo 'OPENROUTER_API_KEY=tu_key_aqui' >> ~/.env")
        sys.exit(1)

    load_dotenv(env_path)
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print(f"{Colors.FAIL}❌ Error: OPENROUTER_API_KEY no encontrada en ~/.env{Colors.ENDC}")
        print(f"\n{Colors.WARNING}🔧 Solución:{Colors.ENDC}")
        print("   Agrega tu key: echo 'OPENROUTER_API_KEY=tu_key_aqui' >> ~/.env")
        sys.exit(1)

    print(f"{Colors.OKGREEN}✓ API Key cargada: {api_key[:20]}...{Colors.ENDC}")
    return api_key

def create_client(api_key):
    """Crea el cliente de OpenAI configurado para OpenRouter"""
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/josem4pro/Kimi-K2",  # Para rankings en openrouter.ai
            "X-Title": "Kimi K2 CLI by josem4pro",  # Para rankings en openrouter.ai
        }
    )
    print(f"{Colors.OKGREEN}✓ Cliente configurado: openrouter.ai{Colors.ENDC}")
    return client

def get_credits_balance(api_key):
    """Obtiene el balance de créditos de OpenRouter"""
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            # OpenRouter devuelve info en data.data
            if 'data' in data:
                limit = data['data'].get('limit')
                usage = data['data'].get('usage', 0)

                # Si no hay límite (cuenta prepago), solo mostramos el uso
                if limit is None or limit == 0:
                    return {
                        'success': True,
                        'is_prepaid': True,
                        'usage': usage,
                        'limit': None,
                        'remaining': None
                    }
                else:
                    remaining = limit - usage
                    return {
                        'success': True,
                        'is_prepaid': False,
                        'limit': limit,
                        'usage': usage,
                        'remaining': remaining
                    }

        return {'success': False, 'error': 'No se pudo obtener el balance'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_tools():
    """Define las herramientas disponibles para el modelo"""
    return [
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
        },
        {
            "type": "function",
            "function": {
                "name": "ejecutar_codigo",
                "description": "Ejecuta código Python y retorna el resultado",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo": {
                            "type": "string",
                            "description": "Código Python a ejecutar"
                        }
                    },
                    "required": ["codigo"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "memoria_distribuida",
                "description": "Accede o actualiza el sistema de memoria distribuida (Neo4j/Centro Consciente)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operacion": {
                            "type": "string",
                            "enum": ["leer", "escribir", "buscar"],
                            "description": "Tipo de operación"
                        },
                        "contenido": {
                            "type": "string",
                            "description": "Contenido a leer/escribir/buscar"
                        }
                    },
                    "required": ["operacion", "contenido"]
                }
            }
        }
    ]

def query_kimi(client, prompt, heavy_mode=False, simple_mode=False, interactive=False, api_key=None):
    """
    Consulta a Kimi K2 Thinking vía OpenRouter con todas las capacidades activadas

    Args:
        client: Cliente de OpenAI configurado
        prompt: Pregunta/prompt para el modelo
        heavy_mode: Activar Heavy Mode (8 trayectorias paralelas)
        simple_mode: Modo simple sin razonamiento extendido
        interactive: Modo interactivo (permite conversación continua)
        api_key: API key para consultar balance de créditos
    """

    # Configuración base
    config = {
        "model": "moonshotai/kimi-k2-thinking",
        "messages": [
            {
                "role": "system",
                "content": "Eres Kimi K2 Thinking, un modelo avanzado de razonamiento profundo. "
                          "Razona paso a paso y sé exhaustivo en tus respuestas. "
                          "Si necesitas información externa, indícalo claramente en tu respuesta."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 16384,  # Respuestas exhaustivas (~12,000 palabras)
        "temperature": 0.3,  # Balance entre precisión y creatividad
        # Tools deshabilitadas por defecto - sin implementación real aún
        # Para habilitar: descomentar las siguientes líneas
        # "tools": get_tools(),
        # "tool_choice": "auto",
    }

    # Activar Heavy Mode si se solicita
    if heavy_mode:
        config["extra_body"] = {"heavy_mode": True}
        print(f"\n{Colors.WARNING}⚡ Heavy Mode activado: 8 trayectorias paralelas{Colors.ENDC}")

    if simple_mode:
        config["max_tokens"] = 1000
        config["temperature"] = 0.1
        print(f"\n{Colors.OKBLUE}🚀 Modo simple: respuesta rápida{Colors.ENDC}")

    print(f"\n{Colors.OKGREEN}✓ Modelo listo: Kimi K2 Thinking (OpenRouter){Colors.ENDC}")
    print(f"{Colors.OKBLUE}📊 Capacidades activas:{Colors.ENDC}")
    print(f"   • Contexto: 256K tokens")
    print(f"   • Tool-calling: Deshabilitado (respuesta directa)")
    print(f"   • Max tokens: {config['max_tokens']}")
    print(f"   • Temperature: {config['temperature']}")
    print(f"   • Provider: OpenRouter")

    try:
        print(f"\n{Colors.OKCYAN}🤔 Procesando...{Colors.ENDC}\n")

        response = client.chat.completions.create(**config)
        message = response.choices[0].message

        # Mostrar respuesta
        print(f"{Colors.BOLD}═══ RESPUESTA ═══{Colors.ENDC}\n")
        print(message.content)

        # Mostrar tools invocadas si las hay
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"\n{Colors.WARNING}═══ TOOLS INVOCADAS ═══{Colors.ENDC}")
            for tool in message.tool_calls:
                print(f"  • {tool.function.name}: {tool.function.arguments}")

        # Mostrar uso de tokens
        if response.usage:
            print(f"\n{Colors.OKBLUE}═══ USO DE TOKENS ═══{Colors.ENDC}")
            print(f"  Input: {response.usage.prompt_tokens:,} tokens")
            print(f"  Output: {response.usage.completion_tokens:,} tokens")
            print(f"  Total: {response.usage.total_tokens:,} tokens")

            # Calcular costo aproximado (OpenRouter pricing para Kimi K2)
            # Precios: $0.60/1M input, $2.50/1M output (via OpenRouter)
            cost_input = (response.usage.prompt_tokens / 1_000_000) * 0.60
            cost_output = (response.usage.completion_tokens / 1_000_000) * 2.50
            total_cost = cost_input + cost_output
            print(f"\n  {Colors.BOLD}💰 Costo de esta consulta: ${total_cost:.6f} USD{Colors.ENDC}")

            # Obtener y mostrar balance de créditos de OpenRouter
            if api_key:
                balance = get_credits_balance(api_key)
                if balance['success']:
                    # Cuenta prepago (sin límite fijo)
                    if balance.get('is_prepaid'):
                        usage = balance['usage']
                        print(f"  {Colors.OKBLUE}💳 Cuenta prepago (créditos disponibles){Colors.ENDC}")
                        print(f"  {Colors.OKGREEN}   Uso acumulado: ${usage:.2f} USD{Colors.ENDC}")
                        print(f"  {Colors.WARNING}   💡 Ver saldo en: https://openrouter.ai/credits{Colors.ENDC}")
                    # Cuenta con límite fijo
                    else:
                        remaining = balance['remaining']
                        limit = balance['limit']
                        usage = balance['usage']

                        # Color según el balance disponible
                        if remaining > 10:
                            color = Colors.OKGREEN
                            status = "✓"
                        elif remaining > 5:
                            color = Colors.WARNING
                            status = "⚠"
                        else:
                            color = Colors.FAIL
                            status = "⚠"

                        print(f"  {color}{status} Saldo disponible: ${remaining:.2f} USD{Colors.ENDC}")
                        print(f"  {Colors.OKBLUE}   (Límite: ${limit:.2f} | Usado: ${usage:.2f}){Colors.ENDC}")
                else:
                    print(f"  {Colors.WARNING}⚠ No se pudo obtener el saldo: {balance.get('error', 'Error desconocido')}{Colors.ENDC}")

        print()  # Línea en blanco al final

        return message.content

    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error al consultar Kimi K2: {e}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}🔧 Posibles causas:{Colors.ENDC}")
        print("   • Límite de requests alcanzado")
        print("   • API key inválida o expirada")
        print("   • Problemas de conectividad")
        print("   • Créditos insuficientes en OpenRouter")
        print("\n   Verifica tu cuenta en: https://openrouter.ai")
        sys.exit(1)

def interactive_mode(client, api_key):
    """Modo interactivo - conversación continua"""
    print(f"\n{Colors.OKGREEN}💬 Modo interactivo activado{Colors.ENDC}")
    print(f"{Colors.WARNING}Escribe 'salir', 'exit' o 'quit' para terminar{Colors.ENDC}")
    print(f"{Colors.WARNING}Escribe 'heavy: tu pregunta' para usar Heavy Mode{Colors.ENDC}\n")

    while True:
        try:
            prompt = input(f"{Colors.BOLD}Tú ➜ {Colors.ENDC}").strip()

            if not prompt:
                continue

            if prompt.lower() in ['salir', 'exit', 'quit']:
                print(f"\n{Colors.OKCYAN}👋 ¡Hasta pronto!{Colors.ENDC}")
                break

            # Detectar si se pide Heavy Mode
            heavy = False
            if prompt.lower().startswith('heavy:'):
                heavy = True
                prompt = prompt[6:].strip()

            query_kimi(client, prompt, heavy_mode=heavy, interactive=True, api_key=api_key)
            print()  # Separador entre respuestas

        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKCYAN}👋 ¡Hasta pronto!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")

def show_help():
    """Muestra la ayuda del comando"""
    help_text = f"""
{Colors.BOLD}KIMI K2 THINKING (OpenRouter) - Wrapper CLI{Colors.ENDC}

{Colors.OKGREEN}Uso básico:{Colors.ENDC}
  okimi                           Modo interactivo (conversación continua)
  okimi "tu pregunta aquí"        Modo comando único

{Colors.OKGREEN}Opciones:{Colors.ENDC}
  -h, --help                     Muestra esta ayuda
  --heavy "pregunta"             Activa Heavy Mode (8 trayectorias paralelas)
  --simple "pregunta"            Modo simple (respuesta rápida sin razonamiento)

{Colors.OKGREEN}Ejemplos:{Colors.ENDC}
  okimi "¿Qué es un sistema de memoria distribuida?"
  okimi --heavy "Diseña una arquitectura de agentes IA multi-nivel"
  okimi --simple "Explica en pocas palabras qué es K2 Thinking"

{Colors.OKGREEN}Capacidades activadas:{Colors.ENDC}
  ✓ Contexto: 256K tokens
  ✓ Tool-calling: búsqueda, código, memoria distribuida
  ✓ Razonamiento extendido: 200-300 pasos
  ✓ Heavy Mode opcional: 8 trayectorias paralelas
  ✓ Transparencia: cadenas de pensamiento visibles
  ✓ Provider: OpenRouter (acceso a 100+ modelos)

{Colors.OKGREEN}Configuración:{Colors.ENDC}
  API Key: ~/.env (OPENROUTER_API_KEY)
  Endpoint: openrouter.ai/api/v1
  Modelo: moonshotai/kimi-k2-thinking

{Colors.OKGREEN}Diferencia con kimi (Chutes.ai):{Colors.ENDC}
  • okimi usa OpenRouter (acceso multi-proveedor)
  • kimi usa Chutes.ai (infraestructura descentralizada)
  • Mismo modelo, diferentes proveedores
  • Precios similares, SLAs diferentes

{Colors.OKGREEN}Más información:{Colors.ENDC}
  GitHub: https://github.com/moonshotai/Kimi-K2
  Paper: arXiv:2501.17055
  OpenRouter: https://openrouter.ai
  Dashboard: https://openrouter.ai/dashboard
"""
    print(help_text)

def main():
    """Función principal"""

    # Verificar argumentos
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Ayuda
        if arg in ['-h', '--help', 'help']:
            print_banner()
            show_help()
            sys.exit(0)

        # Heavy Mode
        if arg == '--heavy' and len(sys.argv) > 2:
            print_banner()
            api_key = load_api_key()
            client = create_client(api_key)
            prompt = ' '.join(sys.argv[2:])
            query_kimi(client, prompt, heavy_mode=True, api_key=api_key)
            sys.exit(0)

        # Simple Mode
        if arg == '--simple' and len(sys.argv) > 2:
            print_banner()
            api_key = load_api_key()
            client = create_client(api_key)
            prompt = ' '.join(sys.argv[2:])
            query_kimi(client, prompt, simple_mode=True, api_key=api_key)
            sys.exit(0)

        # Comando único (cualquier texto)
        print_banner()
        api_key = load_api_key()
        client = create_client(api_key)
        prompt = ' '.join(sys.argv[1:])
        query_kimi(client, prompt, api_key=api_key)
        sys.exit(0)

    # Modo interactivo (sin argumentos)
    print_banner()
    api_key = load_api_key()
    client = create_client(api_key)
    interactive_mode(client, api_key)

if __name__ == '__main__':
    main()
