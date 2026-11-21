Edited README.md

### 🛠️ Tecnologías Utilizadas en este Proyecto

El proyecto fue desarrollado con una arquitectura ligera de **cero dependencias externas obligatorias** (funciona al 100% con Python nativo):

1. **Lenguaje Principal:**
   * **Python 3.12+**: Controla la lógica del servidor, la base de datos y la conexión con la API de Google.
2. **Inteligencia Artificial:**
   * **API REST oficial de Google Gemini (`v1beta`)**: Integración directa con soporte para modelos `gemini-2.5-flash` (rápido y recomendado), `gemini-2.5-pro` (diagnóstico botánico avanzado), `gemini-2.0-flash` y `gemini-1.5-flash`.
3. **Base de Datos & Arquitectura RAG:**
   * **SQLite3 (`plantas.db`)**: Motor de base de datos relacional local que almacena fichas botánicas completas (riego, luz, sustrato, toxicidad para mascotas y diagnóstico de hojas).
   * **RAG (Retrieval-Augmented Generation)**: Algoritmo de búsqueda que extrae los datos de la base de datos según la pregunta del usuario y se los suministra a Gemini para fundamentar sus respuestas.
4. **Servidor Backend:**
   * **`http.server` y `urllib.request` nativos de Python**: No necesitas hacer `pip install` de ningún framework pesado para ponerlo en marcha.
5. **Frontend Web:**
   * **HTML5 Semántico**: Interfaz accesible con modal de catálogo y panel de configuración.
   * **CSS3 Moderno**: Diseño adaptable (*responsive*), efectos *glassmorphism*, paleta botánica en verde esmeralda y alternancia entre **Tema Oscuro y Claro**.
   * **JavaScript Vanilla (ES6+)**: Renderizador de Markdown con soporte de bloques de código y botón de copiado en un clic, consumo de APIs y guardado en `localStorage`.
6. **Modo Consola / Terminal (CLI):**
   * **Python CLI interactivo**: Formato con secuencias de colores ANSI y comandos especiales (`/plantas`, `/ficha`, `/modelo`, `/limpiar`).

---

### ⚠️ Aviso Importante para quienes descarguen este proyecto

> **Cada persona que descargue, clone o ejecute este proyecto debe utilizar su propia API Key de Google Gemini.**
>
> Por razones de seguridad y privacidad, **el proyecto no incluye claves predeterminadas ni compartidas**. Cada usuario debe generar su propia clave gratuita desde su cuenta de Google en:
> 👉 **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**

Una vez obtenida la clave personal (que empieza con `AIzaSy...`), la pueden usar de dos formas:
* Pegándola en el recuadro **"Gemini API Key"** en la barra lateral de la página web (se guarda localmente en el navegador).
* O creando un archivo `.env` en la carpeta del proyecto con:
  ```env
  GEMINI_API_KEY=AIzaSy_tu_clave_personal_aqui
  ```

*(Este aviso y la lista de tecnologías ya quedaron también documentados en el archivo [README.md](file:///C:/Users/joser/.gemini/antigravity/scratch/gemini-chatbot/README.md) del proyecto).*
