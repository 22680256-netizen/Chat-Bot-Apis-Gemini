"""
Servidor Web para el Chatbot Botánico (FloraBot) conectado con Gemini y Base de Datos SQLite.
Funciona con el módulo estándar http.server de Python.
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from gemini_client import call_gemini, get_default_api_key, AVAILABLE_MODELS, DEFAULT_BOTANICAL_PROMPT
from db import get_all_plants, get_plant_by_id, search_plants, add_plant, init_db

# Asegurar que la base de datos esté lista
init_db()

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

class GeminiChatHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        """Envía una respuesta JSON."""
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        """Manejo de pre-flight requests CORS."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Ruta para servir archivos estáticos, base de datos de plantas y estado."""
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # Estado del servidor y modelos
        if path == "/api/status":
            plants = get_all_plants()
            self._send_json(200, {
                "hasEnvKey": bool(get_default_api_key()),
                "models": AVAILABLE_MODELS,
                "totalPlants": len(plants),
                "defaultPrompt": DEFAULT_BOTANICAL_PROMPT
            })
            return

        # Consultar la base de datos de plantas
        if path == "/api/plants":
            search_q = query_params.get("q", [""])[0]
            if search_q:
                results = search_plants(search_q, limit=10)
            else:
                results = get_all_plants()
            self._send_json(200, {"success": True, "plants": results, "total": len(results)})
            return

        # Servir archivos estáticos
        if path == "/" or path == "/index.html":
            filename = "index.html"
        else:
            filename = path.lstrip("/")

        file_path = os.path.join(STATIC_DIR, filename)

        # Seguridad contra Directory Traversal
        if not os.path.abspath(file_path).startswith(STATIC_DIR):
            self.send_error(403, "Acceso denegado")
            return

        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", f"{content_type}; charset=utf-8" if "text" in content_type or "javascript" in content_type else content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error al leer archivo: {e}")
        else:
            self.send_error(404, "Archivo no encontrado")

    def do_POST(self):
        """Procesa peticiones de chat y adición de plantas."""
        parsed = urlparse(self.path)

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"success": False, "error": "Cuerpo de petición vacío."})
            return

        try:
            body_str = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body_str)
        except Exception as e:
            self._send_json(400, {"success": False, "error": f"JSON inválido: {str(e)}"})
            return

        # Endpoint del chat enriquecido con la base de datos
        if parsed.path == "/api/chat":
            messages = payload.get("messages", [])
            api_key = payload.get("apiKey")
            model = payload.get("model", "gemini-2.5-flash")
            system_instruction = payload.get("systemInstruction")
            temperature = payload.get("temperature", 0.7)
            use_database = payload.get("useDatabase", True)

            if not messages:
                self._send_json(400, {"success": False, "error": "Debes proporcionar al menos un mensaje."})
                return

            try:
                result = call_gemini(
                    messages=messages,
                    api_key=api_key,
                    model=model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    use_database=use_database
                )
                self._send_json(200, {
                    "success": True,
                    "reply": result["reply"],
                    "matched_plants": result.get("matched_plants", []),
                    "model": model
                })
            except Exception as e:
                self._send_json(500, {
                    "success": False,
                    "error": str(e)
                })

        # Endpoint para agregar una nueva planta a la base de datos
        elif parsed.path == "/api/plants":
            nombre_comun = payload.get("nombre_comun")
            if not nombre_comun:
                self._send_json(400, {"success": False, "error": "El campo 'nombre_comun' es obligatorio."})
                return

            try:
                new_id = add_plant(payload)
                self._send_json(201, {
                    "success": True,
                    "message": "Planta agregada con éxito a la base de datos.",
                    "plant_id": new_id
                })
            except Exception as e:
                self._send_json(500, {"success": False, "error": f"Error al insertar planta: {e}"})

        else:
            self.send_error(404, "Endpoint no encontrado")

def run(port=5000):
    env_port = os.environ.get("PORT")
    if env_port and env_port.isdigit():
        port = int(env_port)

    server_address = ("127.0.0.1", port)
    try:
        httpd = HTTPServer(server_address, GeminiChatHandler)
    except OSError as e:
        if "Address already in use" in str(e) or e.errno in (98, 10048):
            port += 1
            server_address = ("127.0.0.1", port)
            httpd = HTTPServer(server_address, GeminiChatHandler)
        else:
            raise e

    print("=" * 65)
    print("🌿 SERVIDOR FLORABOT (GEMINI + BASE DE DATOS BOTÁNICA SQLITE)")
    print(f"👉 Abre tu navegador en: http://localhost:{port}")
    total = len(get_all_plants())
    print(f"📚 Base de datos: {total} fichas botánicas cargadas en 'plantas.db'")
    if get_default_api_key():
        print("🔑 GEMINI_API_KEY detectada en el entorno o archivo .env")
    else:
        print("💡 Nota: Puedes ingresar tu API Key directamente en la web")
    print("=" * 65)
    print("Presiona Ctrl + C en esta terminal para detener el servidor.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")
        httpd.server_close()
        print("Servidor detenido.")

if __name__ == "__main__":
    port_arg = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])
    run(port_arg)
