/**
 * Lógica del Frontend para FloraBot (Gemini + Base de Datos SQLite)
 */

document.addEventListener("DOMContentLoaded", () => {
  // ELEMENTOS DOM
  const messagesContainer = document.getElementById("messagesContainer");
  const messagesList = document.getElementById("messagesList");
  const welcomeScreen = document.getElementById("welcomeScreen");
  const typingIndicator = document.getElementById("typingIndicator");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const newChatBtn = document.getElementById("newChatBtn");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const exportChatBtn = document.getElementById("exportChatBtn");

  // CONFIGURACIÓN DOM
  const sidebar = document.getElementById("sidebar");
  const openSidebarBtn = document.getElementById("openSidebarBtn");
  const closeSidebarBtn = document.getElementById("closeSidebarBtn");
  const modelSelect = document.getElementById("modelSelect");
  const activeModelLabel = document.getElementById("activeModelLabel");
  const temperatureSlider = document.getElementById("temperatureSlider");
  const tempValue = document.getElementById("tempValue");
  const systemInstructionInput = document.getElementById("systemInstructionInput");
  const apiKeyInput = document.getElementById("apiKeyInput");
  const toggleKeyVisibility = document.getElementById("toggleKeyVisibility");
  const keyStatus = document.getElementById("keyStatus");
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const useDbToggle = document.getElementById("useDbToggle");
  const dbTotalBadge = document.getElementById("dbTotalBadge");

  // MODAL CATÁLOGO BOTÁNICO
  const catalogModal = document.getElementById("catalogModal");
  const openCatalogBtn = document.getElementById("openCatalogBtn");
  const headerCatalogBtn = document.getElementById("headerCatalogBtn");
  const closeCatalogBtn = document.getElementById("closeCatalogBtn");
  const catalogSearchInput = document.getElementById("catalogSearchInput");
  const catalogList = document.getElementById("catalogList");

  // ESTADO DE LA APLICACIÓN
  let messages = []; // [{role: 'user'|'model', text: '...'}]
  let isThinking = false;
  let hasServerEnvKey = false;
  let allCatalogPlants = [];

  // INICIALIZACIÓN
  initTheme();
  loadSavedSettings();
  checkServerStatus();
  loadPlantCatalog();
  setupEventListeners();

  // =========================================================================
  // GESTIÓN DE ESTADO Y SERVIDOR
  // =========================================================================
  async function checkServerStatus() {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        hasServerEnvKey = data.hasEnvKey;

        if (data.totalPlants !== undefined) {
          dbTotalBadge.textContent = `${data.totalPlants} Plantas`;
        }

        if (data.defaultPrompt && !systemInstructionInput.value.trim()) {
          systemInstructionInput.value = data.defaultPrompt;
        }

        updateKeyStatus();
      }
    } catch (e) {
      console.warn("No se pudo verificar estado del servidor:", e);
      updateKeyStatus();
    }
  }

  function updateKeyStatus() {
    const userKey = apiKeyInput.value.trim();
    if (userKey) {
      keyStatus.textContent = "● Clave personalizada";
      keyStatus.className = "status-indicator ready";
    } else if (hasServerEnvKey) {
      keyStatus.textContent = "● Clave en .env";
      keyStatus.className = "status-indicator ready";
    } else {
      keyStatus.textContent = "● Sin clave";
      keyStatus.className = "status-indicator missing";
    }
  }

  function loadSavedSettings() {
    const savedKey = localStorage.getItem("flora_gemini_key") || localStorage.getItem("gemini_user_api_key");
    if (savedKey) apiKeyInput.value = savedKey;

    const savedModel = localStorage.getItem("flora_gemini_model") || localStorage.getItem("gemini_model");
    if (savedModel && Array.from(modelSelect.options).some(o => o.value === savedModel)) {
      modelSelect.value = savedModel;
      activeModelLabel.textContent = savedModel;
    }

    const savedTemp = localStorage.getItem("flora_gemini_temp");
    if (savedTemp) {
      temperatureSlider.value = savedTemp;
      tempValue.textContent = savedTemp;
    }

    const savedSys = localStorage.getItem("flora_system_instruction");
    if (savedSys) systemInstructionInput.value = savedSys;
  }

  function saveSettings() {
    localStorage.setItem("flora_gemini_key", apiKeyInput.value.trim());
    localStorage.setItem("flora_gemini_model", modelSelect.value);
    localStorage.setItem("flora_gemini_temp", temperatureSlider.value);
    localStorage.setItem("flora_system_instruction", systemInstructionInput.value);
    activeModelLabel.textContent = modelSelect.value;
    updateKeyStatus();
  }

  // =========================================================================
  // GESTIÓN DE TEMAS
  // =========================================================================
  function initTheme() {
    const savedTheme = localStorage.getItem("flora_theme") || "theme-dark";
    document.body.className = savedTheme;
    updateThemeButton(savedTheme);
  }

  function toggleTheme() {
    const isDark = document.body.classList.contains("theme-dark");
    const newTheme = isDark ? "theme-light" : "theme-dark";
    document.body.className = newTheme;
    localStorage.setItem("flora_theme", newTheme);
    updateThemeButton(newTheme);
  }

  function updateThemeButton(theme) {
    const isDark = theme === "theme-dark";
    themeToggleBtn.querySelector(".theme-icon").textContent = isDark ? "🌙" : "☀️";
    themeToggleBtn.querySelector(".theme-text").textContent = isDark ? "Modo oscuro" : "Modo claro";
  }

  // =========================================================================
  // CATÁLOGO DE PLANTAS (BASE DE DATOS SQLITE)
  // =========================================================================
  async function loadPlantCatalog() {
    try {
      const res = await fetch("/api/plants");
      if (res.ok) {
        const data = await res.json();
        allCatalogPlants = data.plants || [];
        renderCatalogCards(allCatalogPlants);
      }
    } catch (e) {
      console.warn("Error cargando catálogo de plantas:", e);
    }
  }

  function renderCatalogCards(plants) {
    catalogList.innerHTML = "";
    if (plants.length === 0) {
      catalogList.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 2rem;">No se encontraron plantas en la base de datos con ese criterio.</div>`;
      return;
    }

    plants.forEach(p => {
      const card = document.createElement("div");
      card.className = "plant-catalog-item";

      const isPetFriendly = p.toxicidad && p.toxicidad.toLowerCase().includes("no tóxica");
      const toxTagClass = isPetFriendly ? "tag-pill tag-success" : "tag-pill tag-warning";
      const toxText = isPetFriendly ? "🐾 Pet Friendly" : "⚠️ Tóxica p/mascotas";

      card.innerHTML = `
        <div class="catalog-item-header">
          <div class="catalog-item-icon">${p.icono || "🌿"}</div>
          <div class="catalog-item-info">
            <h4>${escapeHtml(p.nombre_comun)}</h4>
            <em>${escapeHtml(p.nombre_cientifico)}</em>
          </div>
        </div>
        <div class="plant-tags-row">
          <span class="tag-pill">${escapeHtml(p.tipo)}</span>
          <span class="tag-pill">⭐ ${escapeHtml(p.dificultad)}</span>
          <span class="${toxTagClass}">${toxText}</span>
        </div>
        <div class="catalog-detail-row">
          <strong>☀️ Luz:</strong> ${escapeHtml(p.luz)}
        </div>
        <div class="catalog-detail-row">
          <strong>💧 Riego:</strong> ${escapeHtml(p.riego)}
        </div>
        <div class="catalog-detail-row">
          <strong>🪴 Suelo:</strong> ${escapeHtml(p.suelo)}
        </div>
        <button class="ask-about-btn" type="button" data-plant="${escapeHtml(p.nombre_comun)}">
          💬 Consultar a FloraBot
        </button>
      `;

      card.querySelector(".ask-about-btn").addEventListener("click", () => {
        closeCatalog();
        chatInput.value = `¿Cuáles son los cuidados esenciales, riego y requerimientos de la ${p.nombre_comun}?`;
        handleSendMessage();
      });

      catalogList.appendChild(card);
    });
  }

  function openCatalog() {
    catalogModal.style.display = "flex";
    catalogSearchInput.focus();
  }

  function closeCatalog() {
    catalogModal.style.display = "none";
  }

  // =========================================================================
  // EVENT LISTENERS
  // =========================================================================
  function setupEventListeners() {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      handleSendMessage();
    });

    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    chatInput.addEventListener("input", () => {
      chatInput.style.height = "auto";
      chatInput.style.height = Math.min(chatInput.scrollHeight, 180) + "px";
    });

    apiKeyInput.addEventListener("input", saveSettings);
    modelSelect.addEventListener("change", saveSettings);
    systemInstructionInput.addEventListener("input", saveSettings);
    temperatureSlider.addEventListener("input", () => {
      tempValue.textContent = temperatureSlider.value;
      saveSettings();
    });

    toggleKeyVisibility.addEventListener("click", () => {
      const isPwd = apiKeyInput.type === "password";
      apiKeyInput.type = isPwd ? "text" : "password";
      toggleKeyVisibility.textContent = isPwd ? "🙈" : "👁️";
    });

    newChatBtn.addEventListener("click", startNewChat);
    clearChatBtn.addEventListener("click", startNewChat);
    exportChatBtn.addEventListener("click", exportConversation);
    themeToggleBtn.addEventListener("click", toggleTheme);

    // Modal Catálogo
    openCatalogBtn.addEventListener("click", openCatalog);
    if (headerCatalogBtn) headerCatalogBtn.addEventListener("click", openCatalog);
    closeCatalogBtn.addEventListener("click", closeCatalog);
    catalogModal.addEventListener("click", (e) => {
      if (e.target === catalogModal) closeCatalog();
    });

    catalogSearchInput.addEventListener("input", () => {
      const q = catalogSearchInput.value.toLowerCase().trim();
      if (!q) {
        renderCatalogCards(allCatalogPlants);
      } else {
        const filtered = allCatalogPlants.filter(p => {
          return (p.nombre_comun && p.nombre_comun.toLowerCase().includes(q)) ||
                 (p.nombre_cientifico && p.nombre_cientifico.toLowerCase().includes(q)) ||
                 (p.tipo && p.tipo.toLowerCase().includes(q)) ||
                 (p.toxicidad && p.toxicidad.toLowerCase().includes(q));
        });
        renderCatalogCards(filtered);
      }
    });

    // Sidebar móvil
    openSidebarBtn.addEventListener("click", () => sidebar.classList.add("open"));
    closeSidebarBtn.addEventListener("click", () => sidebar.classList.remove("open"));

    // Tarjetas sugeridas
    document.querySelectorAll(".suggestion-card").forEach(card => {
      card.addEventListener("click", () => {
        const prompt = card.getAttribute("data-prompt");
        chatInput.value = prompt;
        handleSendMessage();
      });
    });
  }

  // =========================================================================
  // GESTIÓN DE MENSAJES Y RAG CON LA BASE DE DATOS
  // =========================================================================
  async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text || isThinking) return;

    if (welcomeScreen) welcomeScreen.style.display = "none";

    // Mostrar mensaje del usuario
    addMessageToUI("user", text);
    messages.push({ role: "user", text: text });

    chatInput.value = "";
    chatInput.style.height = "auto";
    chatInput.focus();

    setThinking(true);

    try {
      const payload = {
        messages: messages,
        apiKey: apiKeyInput.value.trim() || undefined,
        model: modelSelect.value,
        systemInstruction: systemInstructionInput.value.trim() || undefined,
        temperature: parseFloat(temperatureSlider.value),
        useDatabase: useDbToggle.checked
      };

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        const errorMsg = data.error || `Error ${res.status}: No se pudo procesar la respuesta.`;
        addErrorMessage(errorMsg);
        messages.pop();
      } else {
        const reply = data.reply || "";
        const matchedPlants = data.matched_plants || [];

        // Agregar mensaje del bot con la ficha de la base de datos si existe
        addMessageToUI("bot", reply, matchedPlants);
        messages.push({ role: "model", text: reply });
      }
    } catch (err) {
      addErrorMessage(`Error de conexión con el servidor: ${err.message}`);
      messages.pop();
    } finally {
      setThinking(false);
      scrollToBottom();
    }
  }

  function setThinking(thinking) {
    isThinking = thinking;
    sendBtn.disabled = thinking;
    typingIndicator.style.display = thinking ? "flex" : "none";
    if (thinking) scrollToBottom();
  }

  function startNewChat() {
    messages = [];
    messagesList.innerHTML = "";
    if (welcomeScreen) welcomeScreen.style.display = "flex";
    if (window.innerWidth <= 768) sidebar.classList.remove("open");
    chatInput.focus();
  }

  function scrollToBottom() {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 50);
  }

  // =========================================================================
  // RENDERIZADO VISUAL Y TARJETAS BOTÁNICAS
  // =========================================================================
  function addMessageToUI(role, rawText, matchedPlants = []) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${role}-avatar`;
    avatar.textContent = role === "bot" ? "🌿" : "👤";

    const contentWrapper = document.createElement("div");
    contentWrapper.className = "message-content-wrapper";

    // Si es respuesta del bot y la base de datos encontró plantas relevantes, mostrar la tarjeta botánica
    if (role === "bot" && matchedPlants && matchedPlants.length > 0) {
      const topPlant = matchedPlants[0];
      const plantCard = document.createElement("div");
      plantCard.className = "plant-badge-card";

      const isPetFriendly = topPlant.toxicidad && topPlant.toxicidad.toLowerCase().includes("no tóxica");
      const toxTagClass = isPetFriendly ? "tag-pill tag-success" : "tag-pill tag-warning";
      const toxText = isPetFriendly ? "🐾 Pet Friendly" : "⚠️ Tóxica";

      plantCard.innerHTML = `
        <div class="plant-badge-header">
          <div class="plant-badge-title">
            <span>${topPlant.icono || "🌱"}</span>
            <strong>${escapeHtml(topPlant.nombre_comun)}</strong>
          </div>
          <span class="plant-badge-sci">${escapeHtml(topPlant.nombre_cientifico)}</span>
        </div>
        <div class="plant-tags-row">
          <span class="tag-pill">☀️ ${escapeHtml(topPlant.luz.substring(0, 30))}...</span>
          <span class="tag-pill">💧 ${escapeHtml(topPlant.riego.substring(0, 30))}...</span>
          <span class="${toxTagClass}">${toxText}</span>
        </div>
      `;
      contentWrapper.appendChild(plantCard);
    }

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (role === "user") {
      bubble.textContent = rawText;
    } else {
      bubble.innerHTML = renderMarkdown(rawText);
      attachCodeCopyButtons(bubble);
    }

    contentWrapper.appendChild(bubble);

    if (role === "user") {
      row.appendChild(contentWrapper);
      row.appendChild(avatar);
    } else {
      row.appendChild(avatar);
      row.appendChild(contentWrapper);
    }

    messagesList.appendChild(row);
    scrollToBottom();
  }

  function addErrorMessage(errorText) {
    const row = document.createElement("div");
    row.className = "message-row bot";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot-avatar";
    avatar.textContent = "⚠️";

    const contentWrapper = document.createElement("div");
    contentWrapper.className = "message-content-wrapper";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble error-bubble";
    bubble.innerHTML = `<strong>Error en la consulta:</strong><p>${escapeHtml(errorText)}</p>`;

    contentWrapper.appendChild(bubble);
    row.appendChild(avatar);
    row.appendChild(contentWrapper);
    messagesList.appendChild(row);
    scrollToBottom();
  }

  function renderMarkdown(md) {
    if (!md) return "";

    const codeBlocks = [];
    let text = md.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
      const id = `__CODE_BLOCK_${codeBlocks.length}__`;
      codeBlocks.push({ lang: lang || "codigo", code: code.trim() });
      return id;
    });

    text = escapeHtml(text);

    text = text.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    text = text.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    text = text.replace(/^# (.*$)/gim, "<h1>$1</h1>");
    text = text.replace(/^\> (.*$)/gim, "<blockquote>$1</blockquote>");

    text = text.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
    text = text.replace(/___(.*?)___/g, "<strong><em>$1</em></strong>");
    text = text.replace(/__(.*?)__/g, "<strong>$1</strong>");
    text = text.replace(/_(.*?)_/g, "<em>$1</em>");

    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

    text = text.replace(/^\s*[-*]\s+(.*)$/gim, "<li>$1</li>");
    text = text.replace(/(<li>.*<\/li>)/gims, "<ul>$1</ul>");
    text = text.replace(/<\/ul>\s*<ul>/g, "");

    text = text.split(/\n{2,}/).map(paragraph => {
      paragraph = paragraph.trim();
      if (!paragraph) return "";
      if (paragraph.startsWith("<h") || paragraph.startsWith("<ul") || paragraph.startsWith("<block") || paragraph.startsWith("__CODE_BLOCK")) {
        return paragraph;
      }
      return `<p>${paragraph.replace(/\n/g, "<br>")}</p>`;
    }).join("");

    codeBlocks.forEach((block, idx) => {
      const token = `__CODE_BLOCK_${idx}__`;
      const escapedCode = escapeHtml(block.code);
      const replacement = `
        <div class="code-block-wrapper">
          <div class="code-block-header">
            <span>${block.lang}</span>
            <button class="copy-code-btn" type="button">Copiar</button>
          </div>
          <pre><code>${escapedCode}</code></pre>
        </div>
      `;
      text = text.replace(token, replacement);
    });

    return text;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function attachCodeCopyButtons(container) {
    container.querySelectorAll(".copy-code-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const pre = btn.closest(".code-block-wrapper").querySelector("code");
        if (pre) {
          navigator.clipboard.writeText(pre.innerText).then(() => {
            const original = btn.textContent;
            btn.textContent = "¡Copiado! ✓";
            btn.style.color = "#10b981";
            setTimeout(() => {
              btn.textContent = original;
              btn.style.color = "";
            }, 2000);
          });
        }
      });
    });
  }

  function exportConversation() {
    if (messages.length === 0) {
      alert("No hay consultas en la conversación para exportar.");
      return;
    }

    let markdown = `# Consultas Botánicas con FloraBot (Gemini + SQLite)\n`;
    markdown += `*Fecha: ${new Date().toLocaleString()}*\n`;
    markdown += `*Modelo: ${modelSelect.value}*\n\n---\n\n`;

    messages.forEach(m => {
      const sender = m.role === "user" ? "👤 **Tú**" : "🌿 **FloraBot**";
      markdown += `${sender}:\n\n${m.text}\n\n---\n\n`;
    });

    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `florabot-chat-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
});
