// ✅ CORRIGÉ - Chemin relatif qui fonctionne partout
const API_BASE = "/v1";

let currentProject = null;
let projects = JSON.parse(localStorage.getItem("ollama-pilot-projects") || "[]");
let models = [];
let a11yAnnouncer = null; // ARIA live region for screen readers

// Init
document.addEventListener("DOMContentLoaded", init);

async function init() {
  // Initialize accessibility announcer
  a11yAnnouncer = document.getElementById("a11y-announcer");

  await loadModels();
  loadProjects();
  checkGateway();
  setInterval(checkGateway, 5000);

  document.getElementById("new-project").onclick = createProject;
  document.getElementById("theme-toggle").onclick = toggleTheme;
  document.getElementById("input-area").onsubmit = sendMessage;
  document.getElementById("user-input").onkeydown = e => {
    if(e.key==="Enter" && !e.shiftKey && e.ctrlKey) {
      e.preventDefault();
      sendMessage(e);
    }
  };

  if(projects.length === 0) createProject();
  else switchProject(projects[0].id);
}

// ♿ Accessibility: Announce to screen readers (throttled, non-intrusive)
function announceToScreenReader(message) {
  if (!a11yAnnouncer) return;
  a11yAnnouncer.textContent = message;
  // Clear after announcement to allow repeated identical messages
  setTimeout(() => { a11yAnnouncer.textContent = ""; }, 1000);
}

async function loadModels() {
  try {
    const res = await fetch(`${API_BASE}/models`);
    const data = await res.json();
    models = data.data.map(m => m.id);
    const select = document.getElementById("model-select");
    select.innerHTML = "<option value='auto'>🎯 Auto (Smart Routing)</option>" +
      models.map(m => `<option value="${m}">${m.replace(':latest', '')}</option>`).join("");
    announceToScreenReader(`${models.length} modèles d'IA disponibles`);
  } catch(e) {
    console.error("Failed to load models:", e);
    document.getElementById("model-select").innerHTML = "<option>auto</option>";
    announceToScreenReader("Erreur de chargement des modèles");
  }
}

function loadProjects() {
  const list = document.getElementById("projects-list");
  list.innerHTML = projects.map(p => {
    const isActive = p.id === (currentProject?.id);
    return `
      <div
        class="project-item ${isActive ? 'active' : ''}"
        data-id="${p.id}"
        role="button"
        tabindex="0"
        aria-current="${isActive}"
        aria-label="Projet : ${escapeHtml(p.name)}${isActive ? ' (actif)' : ''}"
      >
        <div class="project-title">${escapeHtml(p.name)}</div>
        <div class="project-preview" aria-hidden="true">${escapeHtml(p.messages.slice(-1)[0]?.content?.slice(0,50) || "Nouveau projet")}...</div>
      </div>
    `;
  }).join("");

  // Add click and keyboard handlers
  list.querySelectorAll(".project-item").forEach(el => {
    el.onclick = () => switchProject(el.dataset.id);
    el.onkeydown = (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        switchProject(el.dataset.id);
      }
    };
  });
}

function createProject() {
  const name = prompt("Nom du projet ?", `Projet ${projects.length + 1}`);
  if(!name) return;
  const project = {
    id: Date.now().toString(),
    name,
    messages: [],
    preferredModel: "auto",
    created: new Date().toISOString()
  };
  projects.push(project);
  saveProjects();
  switchProject(project.id);
  announceToScreenReader(`Nouveau projet créé : ${name}`);
}

function switchProject(id) {
  currentProject = projects.find(p => p.id === id);
  if(!currentProject) return;
  document.getElementById("project-title").textContent = currentProject.name;
  document.getElementById("model-select").value = currentProject.preferredModel || "auto";
  renderMessages();
  loadProjects();
  announceToScreenReader(`Projet actif : ${currentProject.name}`);
}

function saveProjects() {
  localStorage.setItem("ollama-pilot-projects", JSON.stringify(projects));
  loadProjects();
}

function renderMessages() {
  const container = document.getElementById("messages");
  container.innerHTML = currentProject.messages.map((msg, idx) => `
    <div class="message ${msg.role}" role="article" aria-label="${msg.role === 'user' ? 'Vous' : 'Assistant'} : message ${idx + 1}">
      <div class="bubble">${msg.role==="assistant" ? marked.parse(msg.content) : escapeHtml(msg.content)}</div>
    </div>
  `).join("");
  container.scrollTop = container.scrollHeight;
}

async function sendMessage(e) {
  e.preventDefault();
  const input = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const text = input.value.trim();
  if(!text) return;

  // Disable input during generation
  input.disabled = true;
  sendBtn.disabled = true;
  sendBtn.setAttribute("aria-label", "Envoi en cours…");

  currentProject.messages.push({role:"user", content:text});
  renderMessages();
  input.value = "";

  const model = document.getElementById("model-select").value;
  currentProject.preferredModel = model;

  const messages = currentProject.messages.map(m => ({role:m.role, content:m.content}));

  const body = {
    model: model === "auto" ? "auto" : model,
    messages,
    stream: true
  };

  // ♿ Announce start of response (once, not on every chunk)
  const modelName = model === "auto" ? "modèle intelligent" : model.replace(':latest', '');
  announceToScreenReader(`L'assistant ${modelName} répond…`);

  try {
    const response = await fetch(`${API_BASE}/chat/completions`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });

    if(!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    let assistantMsg = "";
    currentProject.messages.push({role:"assistant", content:""});
    renderMessages();

    while(true) {
      const {value, done} = await reader.read();
      if(done) break;

      const lines = value.split("\n");
      for(const line of lines) {
        if(line.startsWith("data: ") && line !== "data: [DONE]") {
          try {
            const json = JSON.parse(line.slice(6));
            const delta = json.choices[0]?.delta?.content || "";
            assistantMsg += delta;
            currentProject.messages[currentProject.messages.length-1].content = assistantMsg;
            renderMessages();
            // ♿ NO announcement here - avoid spam
          } catch(e) {
            console.error("Parse error:", e);
          }
        }
      }
    }

    // ♿ Announce completion (once at end)
    announceToScreenReader(`Réponse complète reçue de ${modelName}`);
    saveProjects();
  } catch(error) {
    console.error("Send message error:", error);
    currentProject.messages.push({
      role:"assistant",
      content:`❌ Erreur: ${error.message}\n\nVérifiez que le gateway est démarré et accessible.`
    });
    renderMessages();
    announceToScreenReader(`Erreur : ${error.message}`);
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    sendBtn.setAttribute("aria-label", "Envoyer le message");
    input.focus();
  }
}

async function checkGateway() {
  const statusEl = document.getElementById("status");
  try {
    const res = await fetch(`${API_BASE}/models`);
    if(res.ok) {
      const wasOffline = statusEl.className !== "online";
      statusEl.className = "online";
      statusEl.textContent = "●";
      statusEl.setAttribute("aria-label", "Statut du gateway : en ligne");
      if (wasOffline) {
        announceToScreenReader("Gateway Ollama connecté");
      }
    } else {
      statusEl.className = "";
      statusEl.textContent = "●";
      statusEl.setAttribute("aria-label", "Statut du gateway : hors ligne");
    }
  } catch(e) {
    statusEl.className = "";
    statusEl.textContent = "●";
    statusEl.setAttribute("aria-label", "Statut du gateway : hors ligne");
  }
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme;
  const newTheme = current === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = newTheme;

  const btn = document.getElementById("theme-toggle");
  btn.textContent = current === "dark" ? "🌙" : "☀️";
  btn.setAttribute("aria-label",
    newTheme === "dark"
      ? "Basculer en mode clair"
      : "Basculer en mode sombre"
  );

  announceToScreenReader(`Thème ${newTheme === "dark" ? "sombre" : "clair"} activé`);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
