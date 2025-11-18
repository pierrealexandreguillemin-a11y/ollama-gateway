// ✅ CORRIGÉ - Chemin relatif qui fonctionne partout
const API_BASE = "/v1";

let currentProject = null;
let projects = JSON.parse(localStorage.getItem("ollama-pilot-projects") || "[]");
let models = [];

// Init
document.addEventListener("DOMContentLoaded", init);

async function init() {
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

async function loadModels() {
  try {
    const res = await fetch(`${API_BASE}/models`);
    const data = await res.json();
    models = data.data.map(m => m.id);
    const select = document.getElementById("model-select");
    select.innerHTML = "<option value='auto'>🎯 Auto (Smart Routing)</option>" +
      models.map(m => `<option value="${m}">${m.replace(':latest', '')}</option>`).join("");
  } catch(e) {
    console.error("Failed to load models:", e);
    document.getElementById("model-select").innerHTML = "<option>auto</option>";
  }
}

function loadProjects() {
  const list = document.getElementById("projects-list");
  list.innerHTML = projects.map(p => `
    <div class="project-item ${p.id===(currentProject?.id)?'active':''}" data-id="${p.id}">
      <div class="project-title">${escapeHtml(p.name)}</div>
      <div class="project-preview">${escapeHtml(p.messages.slice(-1)[0]?.content?.slice(0,50) || "Nouveau projet")}...</div>
    </div>
  `).join("");
  list.querySelectorAll(".project-item").forEach(el => el.onclick = () => switchProject(el.dataset.id));
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
}

function switchProject(id) {
  currentProject = projects.find(p => p.id === id);
  if(!currentProject) return;
  document.getElementById("project-title").textContent = currentProject.name;
  document.getElementById("model-select").value = currentProject.preferredModel || "auto";
  renderMessages();
  loadProjects();
}

function saveProjects() {
  localStorage.setItem("ollama-pilot-projects", JSON.stringify(projects));
  loadProjects();
}

function renderMessages() {
  const container = document.getElementById("messages");
  container.innerHTML = currentProject.messages.map(msg => `
    <div class="message ${msg.role}">
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
          } catch(e) {
            console.error("Parse error:", e);
          }
        }
      }
    }
    saveProjects();
  } catch(error) {
    console.error("Send message error:", error);
    currentProject.messages.push({
      role:"assistant",
      content:`❌ Erreur: ${error.message}\n\nVérifiez que le gateway est démarré et accessible.`
    });
    renderMessages();
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

async function checkGateway() {
  try {
    const res = await fetch(`${API_BASE}/models`);
    if(res.ok) {
      document.getElementById("status").className = "online";
      document.getElementById("status").textContent = "●";
    } else {
      document.getElementById("status").className = "";
      document.getElementById("status").textContent = "●";
    }
  } catch(e) {
    document.getElementById("status").className = "";
    document.getElementById("status").textContent = "●";
  }
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme;
  document.documentElement.dataset.theme = current === "dark" ? "light" : "dark";
  document.getElementById("theme-toggle").textContent = current === "dark" ? "🌙" : "☀️";
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
