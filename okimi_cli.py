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
        # Intentar primero el endpoint de créditos (para cuentas prepago)
        credits_response = requests.get(
            "https://openrouter.ai/api/v1/credits",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )

        if credits_response.status_code == 200:
            credits_data = credits_response.json()
            if 'data' in credits_data:
                total_credits = credits_data['data'].get('total_credits', 0)
                total_usage = credits_data['data'].get('total_usage', 0)
                balance = total_credits - total_usage

                return {
                    'success': True,
                    'is_prepaid': True,
                    'total_credits': total_credits,
                    'usage': total_usage,
                    'balance': balance
                }

        # Si falla, intentar el endpoint de auth/key (cuentas con límite)
        auth_response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )

        if auth_response.status_code == 200:
            data = auth_response.json()
            if 'data' in data:
                limit = data['data'].get('limit')
                usage = data['data'].get('usage', 0)

                if limit is not None and limit > 0:
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
    """Define las herramientas disponibles para el modelo (solo búsqueda web por ahora)"""
    return [
        {
            "type": "function",
            "function": {
                "name": "buscar_informacion",
                "description": "Busca información en internet usando SearXNG (meta-buscador con múltiples motores: ArXiv, Google Scholar, GitHub, StackOverflow, Brave, DuckDuckGo)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consulta": {
                            "type": "string",
                            "description": "Qué buscar (ej: 'chutes.ai API documentation balance endpoint')"
                        }
                    },
                    "required": ["consulta"]
                }
            }
        }
    ]

def execute_tool(tool_name, arguments):
    """Ejecuta una herramienta y retorna el resultado"""
    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments

        if tool_name == "buscar_informacion":
            query = args.get("consulta", "")

            # Usar SearXNG local (puerto 8888)
            response = requests.get(
                "http://localhost:8888/search",
                params={"q": query, "format": "json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])[:5]  # Top 5 resultados

                if not results:
                    return "No se encontraron resultados para esta búsqueda."

                # Formatear resultados
                formatted = f"Resultados de búsqueda para '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    title = result.get("title", "Sin título")
                    url = result.get("url", "")
                    content = result.get("content", "")
                    engine = result.get("engine", "")

                    formatted += f"{i}. {title}\n"
                    formatted += f"   URL: {url}\n"
                    if content:
                        # Limitar contenido a 200 caracteres
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        formatted += f"   Contenido: {content_preview}\n"
                    formatted += f"   Motor: {engine}\n\n"

                return formatted
            else:
                return f"Error al buscar: HTTP {response.status_code}"

        else:
            return f"Tool '{tool_name}' no implementada aún"

    except Exception as e:
        return f"Error al ejecutar {tool_name}: {str(e)}"

def query_kimi(client, prompt, heavy_mode=False, simple_mode=False, web_mode=False, interactive=False, api_key=None):
    """
    Consulta a Kimi K2 Thinking vía OpenRouter con todas las capacidades activadas

    Args:
        client: Cliente de OpenAI configurado
        prompt: Pregunta/prompt para el modelo
        heavy_mode: Activar Heavy Mode (8 trayectorias paralelas + tools)
        simple_mode: Modo simple sin razonamiento extendido
        web_mode: Activar herramientas (web, código, memoria) sin heavy mode
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
                          "Tienes acceso a herramientas para búsqueda web, ejecución de código y memoria distribuida."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 16384,  # Respuestas exhaustivas (~12,000 palabras)
        "temperature": 0.3,  # Balance entre precisión y creatividad
    }

    # Activar herramientas si se solicita (web_mode o heavy_mode)
    if web_mode or heavy_mode:
        config["tools"] = get_tools()
        config["tool_choice"] = "auto"

    # Activar Heavy Mode si se solicita (8 trayectorias + tools)
    if heavy_mode:
        config["extra_body"] = {"heavy_mode": True}
        print(f"\n{Colors.WARNING}⚡ Heavy Mode activado: 8 trayectorias paralelas + herramientas{Colors.ENDC}")
    elif web_mode:
        print(f"\n{Colors.OKCYAN}🌐 Web Mode activado: razonamiento + herramientas{Colors.ENDC}")

    if simple_mode:
        config["max_tokens"] = 1000
        config["temperature"] = 0.1
        print(f"\n{Colors.OKBLUE}🚀 Modo simple: respuesta rápida{Colors.ENDC}")

    print(f"\n{Colors.OKGREEN}✓ Modelo listo: Kimi K2 Thinking (OpenRouter){Colors.ENDC}")
    print(f"{Colors.OKBLUE}📊 Capacidades activas:{Colors.ENDC}")
    print(f"   • Contexto: 256K tokens")

    # Indicar si las herramientas están activas
    if web_mode or heavy_mode:
        print(f"   • Tool-calling: ✓ Habilitado (búsqueda web vía SearXNG)")
    else:
        print(f"   • Tool-calling: ✗ Deshabilitado (respuesta directa)")

    print(f"   • Max tokens: {config['max_tokens']}")
    print(f"   • Temperature: {config['temperature']}")
    print(f"   • Provider: OpenRouter")

    try:
        print(f"\n{Colors.OKCYAN}🤔 Procesando...{Colors.ENDC}\n")

        # Primera llamada al modelo
        response = client.chat.completions.create(**config)
        message = response.choices[0].message

        # Si el modelo quiere usar tools, ejecutarlas
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"{Colors.WARNING}🔧 Ejecutando herramientas...{Colors.ENDC}\n")

            # Agregar el mensaje del asistente con tool_calls
            # Convertir tool_calls a dict serializables
            tool_calls_list = []
            for tc in message.tool_calls:
                tool_calls_list.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

            config["messages"].append({
                "role": "assistant",
                "content": None,  # Debe ser None cuando hay tool_calls
                "tool_calls": tool_calls_list
            })

            # Ejecutar cada tool y agregar resultados
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments

                print(f"  📡 {tool_name}({tool_args[:80]}...)" if len(tool_args) > 80 else f"  📡 {tool_name}({tool_args})")

                # Ejecutar la tool
                tool_result = execute_tool(tool_name, tool_args)

                # Agregar el resultado a messages
                config["messages"].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result
                })

                print(f"  ✓ Resultado obtenido ({len(tool_result)} caracteres)\n")

            # Remover tools de config para la segunda llamada
            config_second = config.copy()
            config_second.pop("tools", None)
            config_second.pop("tool_choice", None)

            # Segunda llamada al modelo con los resultados de las tools
            print(f"{Colors.OKCYAN}🤔 Generando respuesta final...{Colors.ENDC}\n")
            response = client.chat.completions.create(**config_second)
            message = response.choices[0].message

        # Mostrar respuesta final
        print(f"{Colors.BOLD}═══ RESPUESTA ═══{Colors.ENDC}\n")
        if message.content:
            print(message.content)
        else:
            print(f"{Colors.WARNING}(Sin contenido de texto){Colors.ENDC}")

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
                balance_info = get_credits_balance(api_key)
                if balance_info['success']:
                    # Cuenta prepago (créditos prepagados)
                    if balance_info.get('is_prepaid'):
                        balance = balance_info['balance']
                        total_credits = balance_info['total_credits']
                        usage = balance_info['usage']

                        # Color según el balance disponible
                        if balance > 10:
                            color = Colors.OKGREEN
                            status = "✓"
                        elif balance > 5:
                            color = Colors.WARNING
                            status = "⚠"
                        else:
                            color = Colors.FAIL
                            status = "⚠"

                        print(f"  {color}{status} Balance disponible: ${balance:.2f} USD{Colors.ENDC}")
                        print(f"  {Colors.OKBLUE}   (Total: ${total_credits:.2f} | Gastado: ${usage:.4f}){Colors.ENDC}")
                    # Cuenta con límite fijo
                    else:
                        remaining = balance_info['remaining']
                        limit = balance_info['limit']
                        usage = balance_info['usage']

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
                    print(f"  {Colors.WARNING}⚠ No se pudo obtener el saldo: {balance_info.get('error', 'Error desconocido')}{Colors.ENDC}")

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
    print(f"{Colors.WARNING}Escribe 'heavy: tu pregunta' para Heavy Mode{Colors.ENDC}")
    print(f"{Colors.WARNING}Escribe 'web: tu pregunta' para Web Mode{Colors.ENDC}\n")

    while True:
        try:
            prompt = input(f"{Colors.BOLD}Tú ➜ {Colors.ENDC}").strip()

            if not prompt:
                continue

            if prompt.lower() in ['salir', 'exit', 'quit']:
                print(f"\n{Colors.OKCYAN}👋 ¡Hasta pronto!{Colors.ENDC}")
                break

            # Detectar modo especial
            heavy = False
            web = False

            if prompt.lower().startswith('heavy:'):
                heavy = True
                prompt = prompt[6:].strip()
            elif prompt.lower().startswith('web:'):
                web = True
                prompt = prompt[4:].strip()

            query_kimi(client, prompt, heavy_mode=heavy, web_mode=web, interactive=True, api_key=api_key)
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
  --simple "pregunta"            Modo simple (respuesta rápida sin razonamiento)
  --web "pregunta"               Web Mode (razonamiento + herramientas)
  --heavy "pregunta"             Heavy Mode (8 trayectorias + herramientas)

{Colors.OKGREEN}Ejemplos:{Colors.ENDC}
  okimi "¿Qué es un sistema de memoria distribuida?"
  okimi --simple "Resume en 3 líneas qué es K2 Thinking"
  okimi --web "Busca info reciente sobre Kimi K2"
  okimi --heavy "Diseña arquitectura completa multi-agente"

{Colors.OKGREEN}Capacidades activadas:{Colors.ENDC}
  ✓ Contexto: 256K tokens
  ✓ Razonamiento extendido: 200-300 pasos
  ✓ Transparencia: cadenas de pensamiento visibles
  ✓ Provider: OpenRouter (acceso a 100+ modelos)

{Colors.OKGREEN}Modos disponibles:{Colors.ENDC}
  • Simple (--simple): Respuesta rápida sin razonamiento extendido
  • Normal (default): Razonamiento completo sin herramientas
  • Web (--web): Razonamiento + herramientas (1 trayectoria)
  • Heavy (--heavy): Razonamiento + herramientas (8 trayectorias)

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

        # Simple Mode
        if arg == '--simple' and len(sys.argv) > 2:
            print_banner()
            api_key = load_api_key()
            client = create_client(api_key)
            prompt = ' '.join(sys.argv[2:])
            query_kimi(client, prompt, simple_mode=True, api_key=api_key)
            sys.exit(0)

        # Web Mode (herramientas sin heavy)
        if arg == '--web' and len(sys.argv) > 2:
            print_banner()
            api_key = load_api_key()
            client = create_client(api_key)
            prompt = ' '.join(sys.argv[2:])
            query_kimi(client, prompt, web_mode=True, api_key=api_key)
            sys.exit(0)

        # Heavy Mode (8 trayectorias + herramientas)
        if arg == '--heavy' and len(sys.argv) > 2:
            print_banner()
            api_key = load_api_key()
            client = create_client(api_key)
            prompt = ' '.join(sys.argv[2:])
            query_kimi(client, prompt, heavy_mode=True, api_key=api_key)
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
