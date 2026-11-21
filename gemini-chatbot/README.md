# 🌿 FloraBot: Chatbot Botánico con Gemini y Base de Datos (SQLite)

**FloraBot** es un asistente botánico inteligente conectado a la **API de Google Gemini** y respaldado por una **Base de Datos SQLite local (`plantas.db`)**. Utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** para ofrecer respuestas verificadas sobre cuidados de plantas, frecuencias de riego, niveles de luz, sustratos adecuados, soluciones a plagas y advertencias cruciales de toxicidad para mascotas (perros y gatos).

---

## 🌟 Novedades Botánicas y Base de Datos

- **Base de Datos SQLite Integrada (`plantas.db`)**: Cuenta con 16 fichas botánicas detalladas (Monstera, Sansevieria, Pothos, Cuna de Moisés, Aloe Vera, Ficus Lyrata, Lavanda, Romero, Calathea, Tomate, Orquídea, Cinta, Menta, Árbol de Jade, etc.).
- **Búsqueda Inteligente RAG**: Cuando un usuario pregunta (por ejemplo *"¿Cada cuánto riego mi monstera?"* o *"¿Qué planta no es tóxica para gatos?"*), el sistema consulta la base de datos local y le suministra la ficha técnica oficial a Gemini para fundamentar su respuesta.
- **Tarjetas Botánicas Interactivas**: La interfaz web muestra una ficha técnica de la planta consultada con etiquetas de luz ☀️, riego 💧 y alerta de toxicidad 🐾.
- **Catálogo Botánico Explorador**: Botón integrado en la web para buscar y explorar todas las plantas almacenadas en la base de datos SQLite.
- **Comandos de Consola Ampliados**: En el modo CLI puedes usar `/plantas` para listar la base de datos o `/ficha <nombre>` para consultar información directa sin gastar cuota de la API.

---

## 🚀 Inicio Rápido

### 1. Obtener tu clave de API de Gemini (Gratis)
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Haz clic en **"Create API Key"** y copia tu clave.

---

### 2. Opción A: Ejecutar la Interfaz Web (Recomendado)

En tu terminal o PowerShell:

```powershell
cd "C:\Users\joser\.gemini\antigravity\scratch\gemini-chatbot"
python app.py
```

Luego abre en tu navegador:
👉 **[http://localhost:5000](http://localhost:5000)**

*Puedes ingresar tu API Key en la barra lateral de la web o colocarla en un archivo `.env` (`GEMINI_API_KEY=tu_clave`).*

---

### 3. Opción B: Modo Terminal / Consola (CLI)

```powershell
cd "C:\Users\joser\.gemini\antigravity\scratch\gemini-chatbot"
python chat_cli.py
```

#### Comandos en consola:
- `/plantas`: Muestra todas las plantas en la base de datos SQLite.
- `/ficha <nombre>`: Muestra la ficha técnica detallada directa de la base de datos.
- `/limpiar`: Reinicia el historial de la conversación.
- `/modelo`: Cambia el modelo de Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`, etc.).
- `/salir`: Finaliza el chat.

---

## 🗄️ Esquema de la Base de Datos SQLite (`plantas.db`)

La tabla `plantas` contiene los siguientes campos estructurados:

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER | Clave primaria autoincremental |
| `nombre_comun` | TEXT | Nombre popular (ej. *Monstera Deliciosa (Costilla de Adán)*) |
| `nombre_cientifico` | TEXT | Nombre taxonómico en latín (ej. *Monstera deliciosa*) |
| `tipo` | TEXT | Interior, Exterior, Suculenta, Aromática, Huerto |
| `luz` | TEXT | Requerimientos de sol directo, indirecto o sombra |
| `riego` | TEXT | Frecuencia estacional y pautas de secado |
| `humedad` | TEXT | Porcentaje de humedad ambiental recomendada |
| `temperatura` | TEXT | Rango térmico ideal |
| `suelo` | TEXT | Mezcla de sustrato, drenaje y pH |
| `toxicidad` | TEXT | Nivel de toxicidad para perros, gatos y niños |
| `dificultad` | TEXT | Fácil, Moderada, Exigente |
| `cuidados` | TEXT | Consejos de poda, limpieza y tutores |
| `problemas_comunes` | TEXT | Diagnóstico de hojas amarillas, manchas y plagas |
| `propiedades` | TEXT | Purificadora de aire, medicinal, culinaria |
| `icono` | TEXT | Emoji representativo (🪴, 🌿, 🌸, 🌵) |

---

## 📁 Estructura del Código

```
gemini-chatbot/
│
├── app.py              # Servidor HTTP web con endpoints /api/chat y /api/plants
├── db.py               # Gestión de base de datos SQLite (búsqueda y contexto RAG)
├── gemini_client.py    # Cliente Gemini con inyección de contexto botánico
├── chat_cli.py         # Consola interactiva con soporte de fichas botánicas
├── plantas.db          # Base de datos SQLite local
├── .env.example        # Plantilla para la API Key
├── requirements.txt    # Dependencias opcionales
├── README.md           # Documentación completa
│
└── static/
    ├── index.html      # Interfaz con catálogo de plantas y chat
    ├── style.css       # Estilos botánicos (verde esmeralda, tarjetas y modales)
    └── app.js          # Lógica del cliente web, buscador y renderizado
```
