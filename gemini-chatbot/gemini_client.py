"""
Módulo cliente para la API de Google Gemini integrado con la Base de Datos Botánica (SQLite).
Combina las respuestas generativas de Gemini con datos botánicos verificados (RAG).
"""

import os
import json
import urllib.request
import urllib.error

from db import get_botanical_context_for_prompt

def load_dotenv(filepath=".env"):
    """Carga variables de entorno desde un archivo .env si existe."""
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass

load_dotenv()

AVAILABLE_MODELS = [
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash (Recomendado - Rápido y muy inteligente)"},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro (Razonamiento botánico profundo y diagnóstico)"},
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash (Velocidad ultrarrápida)"},
    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Versión estable)"},
    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Contexto largo)"}
]

DEFAULT_BOTANICAL_PROMPT = (
    "Eres FloraBot, un asistente botánico experto y cordial especialista en plantas de interior, "
    "jardines, huertos, suculentas y cuidado vegetal. Tu misión es ayudar a los usuarios a cuidar "
    "sus plantas, solucionar problemas de hojas amarillas, plagas, riego y luz, y avisar siempre sobre "
    "toxicidad para mascotas (perros y gatos). "
    "Si se te proporcionan datos de la base de datos botánica, básate estrictamente en ellos para dar "
    "consejos precisos y confiables. Responde en español de forma estructurada, amena y con emojis pertinentes."
)

def get_default_api_key():
    """Obtiene la clave configurada en las variables de entorno."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

def call_gemini(messages, api_key=None, model="gemini-2.5-flash", system_instruction=None, temperature=0.7, use_database=True):
    """
    Envía la conversación a Gemini enriquecida con información de la base de datos botánica.

    Args:
        messages (list): [{'role': 'user'|'model', 'text': '...'}]
        api_key (str): Clave de API de Gemini.
        model (str): ID del modelo.
        system_instruction (str): Instrucción de sistema (usa DEFAULT_BOTANICAL_PROMPT si no se pasa).
        temperature (float): Creatividad (0.0 a 1.0).
        use_database (bool): Si es True, consulta SQLite para inyectar datos reales de la planta.

    Returns:
        dict: {
            "reply": str,
            "matched_plants": list (fichas de la base de datos)
        }
    """
    key = (api_key or "").strip() or get_default_api_key().strip()
    if not key:
        raise ValueError(
            "No se encontró una clave de API de Gemini. "
            "Por favor proporciona tu API Key en la interfaz o configúrala en el archivo .env."
        )

    model_name = (model or "gemini-2.5-flash").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

    # Extraer la última consulta del usuario para buscar en la base de datos
    last_user_query = ""
    for msg in reversed(messages):
        if msg.get("role") in ["user", "usuario"]:
            last_user_query = msg.get("text", "")
            break

    db_context = ""
    matched_plants = []
    if use_database and last_user_query:
        try:
            db_context, matched_plants = get_botanical_context_for_prompt(last_user_query)
        except Exception as e:
            print(f"Aviso: Error consultando la base de datos: {e}")

    # Formatear el historial
    formatted_contents = []
    for idx, msg in enumerate(messages):
        raw_role = msg.get("role", "user").lower()
        role = "model" if raw_role in ["model", "assistant", "bot", "gemini"] else "user"
        text = msg.get("text", "")

        # Si es el último mensaje del usuario y tenemos datos de la base de datos, inyectarlos
        if role == "user" and idx == len(messages) - 1 and db_context:
            augmented_text = f"{text}\n\n[CONTEXTO DE LA BASE DE DATOS LOCAL]:\n{db_context}"
            formatted_contents.append({
                "role": "user",
                "parts": [{"text": augmented_text}]
            })
        else:
            if text.strip():
                formatted_contents.append({
                    "role": role,
                    "parts": [{"text": text}]
                })

    if not formatted_contents:
        raise ValueError("No hay mensajes válidos para enviar a Gemini.")

    # Instrucción de sistema
    sys_prompt = system_instruction if (system_instruction and system_instruction.strip()) else DEFAULT_BOTANICAL_PROMPT
    if db_context and db_context not in sys_prompt:
        sys_prompt += "\nCuentas con acceso a la base de datos botánica local SQLite. Menciona los datos clave (riego, luz, toxicidad) de forma natural en tu respuesta."

    payload = {
        "contents": formatted_contents,
        "systemInstruction": {
            "parts": [{"text": sys_prompt}]
        },
        "generationConfig": {
            "temperature": max(0.0, min(2.0, float(temperature if temperature is not None else 0.7))),
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-FloraBot/2.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            resp_bytes = response.read()
            resp_data = json.loads(resp_bytes.decode("utf-8"))

            candidates = resp_data.get("candidates", [])
            if not candidates:
                prompt_feedback = resp_data.get("promptFeedback", {})
                block_reason = prompt_feedback.get("blockReason")
                if block_reason:
                    reply_text = f"⚠️ La consulta fue bloqueada por filtros de seguridad: {block_reason}."
                else:
                    reply_text = "⚠️ No se recibió respuesta del modelo."
            else:
                candidate = candidates[0]
                parts = candidate.get("content", {}).get("parts", [])
                if parts:
                    reply_text = "".join(part.get("text", "") for part in parts)
                else:
                    finish_reason = candidate.get("finishReason", "DESCONOCIDO")
                    reply_text = f"⚠️ [Respuesta vacía - Motivo: {finish_reason}]"

            return {
                "reply": reply_text,
                "matched_plants": matched_plants
            }

    except urllib.error.HTTPError as e:
        error_details = ""
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            error_details = err_json.get("error", {}).get("message", "")
        except Exception:
            error_details = str(e)

        if e.code in (401, 403):
            raise RuntimeError(
                f"Clave de API inválida o sin permisos (HTTP {e.code}). "
                f"Verifica tu GEMINI_API_KEY en Google AI Studio (https://aistudio.google.com/). Detalle: {error_details}"
            )
        elif e.code == 404:
            raise RuntimeError(
                f"El modelo '{model_name}' no existe o no está disponible (HTTP 404). "
                f"Prueba seleccionando 'gemini-2.5-flash'. Detalle: {error_details}"
            )
        elif e.code == 429:
            raise RuntimeError(
                f"Has alcanzado el límite de cuota de la API de Gemini (HTTP 429). "
                f"Por favor espera unos segundos antes de enviar otro mensaje. Detalle: {error_details}"
            )
        else:
            raise RuntimeError(f"Error de la API de Gemini (HTTP {e.code}): {error_details or e.reason}")

    except urllib.error.URLError as e:
        raise RuntimeError(f"Error de conexión de red con Google Gemini: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado al comunicarse con Gemini: {str(e)}")
