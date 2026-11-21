"""
Chatbot botánico interactivo por consola (CLI) conectado a Gemini y SQLite.
Ejecución: python chat_cli.py
"""

import sys
import time
from gemini_client import call_gemini, get_default_api_key, AVAILABLE_MODELS, load_dotenv, DEFAULT_BOTANICAL_PROMPT
from db import get_all_plants, search_plants, get_plant_by_id, init_db

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

def print_banner():
    init_db()
    total = len(get_all_plants())
    print(f"\n{GREEN}{BOLD}================================================================{RESET}")
    print(f"{GREEN}{BOLD}       🌿 FLORABOT: ASISTENTE BOTÁNICO (GEMINI + SQLITE) 🌿{RESET}")
    print(f"{GREEN}{BOLD}================================================================{RESET}")
    print(f"📚 {YELLOW}Base de datos local activa:{RESET} {total} fichas de plantas registradas")
    print(f"{CYAN}Comandos especiales:{RESET}")
    print(f"  {BOLD}/plantas{RESET}     - Ver catálogo completo de la base de datos")
    print(f"  {BOLD}/ficha <nombre>{RESET} - Consultar ficha técnica directa de la BD")
    print(f"  {BOLD}/limpiar{RESET}     - Reiniciar la conversación actual")
    print(f"  {BOLD}/modelo{RESET}      - Cambiar modelo de Gemini")
    print(f"  {BOLD}/salir{RESET}       - Salir del programa")
    print(f"{GREEN}----------------------------------------------------------------{RESET}\n")

def request_api_key():
    key = get_default_api_key()
    if key:
        return key

    print(f"{YELLOW}⚠️  No se detectó GEMINI_API_KEY en tu entorno o archivo .env.{RESET}")
    print(f"Consigue una gratis en: {CYAN}https://aistudio.google.com/app/apikey{RESET}\n")

    while True:
        user_key = input(f"{BOLD}Pega tu Gemini API Key aquí: {RESET}").strip()
        if user_key:
            save_env = input("¿Deseas guardarla en .env para futuras sesiones? (s/n): ").strip().lower()
            if save_env in ["s", "si", "sí", "y", "yes"]:
                try:
                    with open(".env", "a", encoding="utf-8") as f:
                        f.write(f"\nGEMINI_API_KEY={user_key}\n")
                    print(f"{GREEN}✓ Clave guardada en .env{RESET}\n")
                except Exception as e:
                    print(f"{RED}No se pudo guardar en .env: {e}{RESET}\n")
            return user_key
        print(f"{RED}La clave no puede estar vacía.{RESET}")

def print_plant_card(p):
    print(f"\n{BLUE}┌─────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{BLUE}│{RESET} {GREEN}{BOLD}{p.get('icono', '🌿')} {p['nombre_comun']}{RESET}")
    print(f"{BLUE}│{RESET} {CYAN}Científico:{RESET} {p['nombre_cientifico']}  |  {CYAN}Tipo:{RESET} {p['tipo']}")
    print(f"{BLUE}│{RESET} {YELLOW}☀️ Luz:{RESET} {p['luz'][:55]}...")
    print(f"{BLUE}│{RESET} {CYAN}💧 Riego:{RESET} {p['riego'][:55]}...")
    print(f"{BLUE}│{RESET} {RED}⚠️ Toxicidad:{RESET} {p['toxicidad']}")
    print(f"{BLUE}│{RESET} {MAGENTA}✨ Propiedades:{RESET} {p['propiedades'][:50]}...")
    print(f"{BLUE}└─────────────────────────────────────────────────────────────┘{RESET}\n")

def main():
    load_dotenv()
    api_key = request_api_key()
    print_banner()

    current_model = "gemini-2.5-flash"
    system_instruction = DEFAULT_BOTANICAL_PROMPT
    history = []

    print(f"{GREEN}Modelo actual:{RESET} {BOLD}{current_model}{RESET}")
    print(f"{CYAN}¡Pregúntame sobre cualquier planta, riego, luz o problemas de hojas!{RESET}\n")

    while True:
        try:
            user_input = input(f"{CYAN}{BOLD}Tú > {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{YELLOW}¡Hasta luego! Cuida tus plantas 🌱{RESET}")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ["/salir", "/exit", "/quit"]:
                print(f"{YELLOW}¡Hasta luego! Cuida tus plantas 🌱{RESET}")
                break

            elif cmd in ["/plantas", "/catalogo"]:
                plants = get_all_plants()
                print(f"\n{GREEN}{BOLD}=== CATÁLOGO BOTÁNICO EN BASE DE DATOS ({len(plants)} plantas) ==={RESET}")
                for idx, p in enumerate(plants, 1):
                    print(f" {idx:2d}. {p['icono']} {BOLD}{p['nombre_comun']}{RESET} ({p['nombre_cientifico']}) - {p['tipo']}")
                print(f"\nPara ver detalles usa: {YELLOW}/ficha <nombre>{RESET}\n")
                continue

            elif cmd in ["/ficha"]:
                if not arg:
                    print(f"{YELLOW}Uso: /ficha <nombre o palabra clave>{RESET}\n")
                    continue
                matches = search_plants(arg, limit=1)
                if matches:
                    p = matches[0]
                    print_plant_card(p)
                    print(f"{BOLD}Cuidados detallados:{RESET}\n{p['cuidados']}")
                    print(f"\n{BOLD}Problemas comunes / plagas:{RESET}\n{p['problemas_comunes']}\n")
                else:
                    print(f"{RED}No se encontró ninguna planta con '{arg}' en la base de datos.{RESET}\n")
                continue

            elif cmd in ["/limpiar", "/clear"]:
                history.clear()
                print(f"{GREEN}✓ Historial de chat reiniciado.{RESET}\n")
                continue

            elif cmd in ["/modelo", "/model"]:
                print(f"\n{YELLOW}Modelos disponibles:{RESET}")
                for idx, m in enumerate(AVAILABLE_MODELS, 1):
                    prefix = "👉" if m["id"] == current_model else "  "
                    print(f" {prefix} {idx}. {m['name']} ({CYAN}{m['id']}{RESET})")
                sel = input("\nElige el número de modelo: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(AVAILABLE_MODELS):
                    current_model = AVAILABLE_MODELS[int(sel) - 1]["id"]
                    print(f"{GREEN}✓ Modelo cambiado a: {current_model}{RESET}\n")
                continue

            elif cmd in ["/ayuda", "/help"]:
                print_banner()
                continue

            else:
                print(f"{RED}Comando no reconocido. Escribe /ayuda para ver los disponibles.{RESET}\n")
                continue

        # Chat con Gemini enriquecido por la Base de Datos
        history.append({"role": "user", "text": user_input})
        print(f"{MAGENTA}Consultando base de datos botánica y pensando con Gemini... ✨{RESET}", end="\r", flush=True)

        start_time = time.time()
        try:
            result = call_gemini(
                messages=history,
                api_key=api_key,
                model=current_model,
                system_instruction=system_instruction,
                use_database=True
            )
            elapsed = time.time() - start_time
            print(" " * 65, end="\r")

            # Mostrar ficha de la base de datos si hubo coincidencia
            matched = result.get("matched_plants", [])
            if matched:
                top_p = matched[0]
                print(f"{GREEN}🌿 [Base de Datos: Coincidencia encontrada con '{top_p['nombre_comun']}']{RESET}")

            print(f"{GREEN}{BOLD}FloraBot ({current_model}) [{elapsed:.1f}s]:{RESET}")
            print(f"{result['reply']}\n")

            history.append({"role": "model", "text": result["reply"]})

        except Exception as e:
            print(" " * 65, end="\r")
            print(f"{RED}Error: {e}{RESET}\n")
            if history and history[-1]["role"] == "user":
                history.pop()

if __name__ == "__main__":
    main()
