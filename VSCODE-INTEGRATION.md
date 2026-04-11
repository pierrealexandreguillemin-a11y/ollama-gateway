# 🔌 Intégration VSCode - Ollama Gateway

Utilisez vos 5 modèles Ollama locaux directement dans VSCode avec l'orchestration multi-modèle !

## Extensions Supportées

### 1. Continue.dev (Recommandé) ⭐

**Installation** :

1. Installez l'extension : [Continue - VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
2. Ouvrez les paramètres : `Ctrl+Shift+P` → "Continue: Open config.json"

**Configuration** :

```json
{
  "models": [
    {
      "title": "🤖 Orchestrate (Multi-AI)",
      "provider": "openai",
      "model": "orchestrate",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "🎯 Auto Routing",
      "provider": "openai",
      "model": "auto",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "💻 Qwen Coder",
      "provider": "openai",
      "model": "qwen2.5-coder:7b",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "🌍 Multilingual (Qwen3)",
      "provider": "openai",
      "model": "huihui_ai/qwen3-abliterated:latest",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "✍️ Creative Writer",
      "provider": "openai",
      "model": "gemma2:latest",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "⚡ Fast (Llama3.2)",
      "provider": "openai",
      "model": "llama3.2:latest",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Autocomplete",
    "provider": "openai",
    "model": "qwen2.5-coder:7b",
    "apiBase": "http://localhost:4000/v1",
    "apiKey": "not-needed"
  }
}
```

**Utilisation** :

- `Ctrl+L` : Chat avec le modèle sélectionné
- `Ctrl+I` : Edit inline avec suggestions
- Sélectionnez "🤖 Orchestrate" pour les tâches complexes
- Sélectionnez "💻 Qwen Coder" pour le code pur

---

### 2. Cline (Claude Code) 🔧

**Installation** :

1. Installez : [Cline - VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Paramètres : `Ctrl+Shift+P` → "Cline: Open Settings"

**Configuration** :

```json
{
  "apiProvider": "openai-compatible",
  "openAiCompatibleEndpoint": "http://localhost:4000/v1",
  "openAiCompatibleApiKey": "not-needed",
  "openAiCompatibleModelId": "orchestrate"
}
```

**Pour changer de modèle** :

- `orchestrate` - Orchestration multi-modèle
- `auto` - Routing intelligent
- `qwen2.5-coder:7b` - Code spécialisé

---

### 3. Cody by Sourcegraph 🦉

**Installation** :

1. Installez : [Cody AI - VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=sourcegraph.cody-ai)
2. Settings → Extensions → Cody

**Configuration** :

```json
{
  "cody.serverEndpoint": "http://localhost:4000/v1",
  "cody.customHeaders": {
    "Authorization": "Bearer not-needed"
  },
  "cody.experimental.chatModel": "orchestrate"
}
```

---

### 4. Tabnine (Autocomplete) 📝

**Installation** :

1. Installez : [Tabnine - VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=TabNine.tabnine-vscode)
2. Tabnine Settings → Custom Endpoint

**Configuration** :

- Custom endpoint: `http://localhost:4000/v1`
- Model: `deepseek-coder-v2:latest`
- API Key: `not-needed`

---

## Workflow Recommandés

### Pour le développement général

```
Continue.dev avec "🎯 Auto Routing"
↓
Le gateway route automatiquement vers le bon modèle
```

### Pour les tâches complexes

```
Continue.dev avec "🤖 Orchestrate (Multi-AI)"
↓
Exemple: "Refactor this code and add tests"
↓
deepseek-coder analyse + gemma2 documente + qwen2.5 traduit
```

### Pour le code pur

```
Continue.dev avec "💻 Qwen Coder"
↓
Coding spécialisé sans routing
```

---

## Exemples de Prompts

### Avec Orchestration (model: orchestrate)

**Prompt** :

```
Compare Python async/await vs JavaScript promises,
then refactor this code to use async patterns in both languages.
```

**Résultat** :

- qwen2.5-coder explique Python async
- qwen2.5-coder explique JS promises
- qwen2.5-coder refactorise les deux versions
- huihui_ai/qwen3-abliterated synthétise la comparaison

### Avec Auto Routing (model: auto)

**Prompt** :

```
Translate this error message to French
```

**Résultat** :

- Gateway détecte "translate" → route vers huihui_ai/qwen3-abliterated
- Réponse multilingue spécialisée

---

## Configuration Avancée

### Utiliser différents modèles par contexte

**Continue.dev - config.json** :

```json
{
  "contextProviders": [
    {
      "name": "code",
      "params": {
        "model": "qwen2.5-coder:7b"
      }
    },
    {
      "name": "docs",
      "params": {
        "model": "qwen2.5:latest"
      }
    }
  ]
}
```

### Ajouter des instructions système personnalisées

```json
{
  "models": [
    {
      "title": "Code Reviewer",
      "provider": "openai",
      "model": "orchestrate",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed",
      "systemMessage": "You are a senior code reviewer. Focus on: 1) Security 2) Performance 3) Best practices"
    }
  ]
}
```

---

## Démarrage Rapide

### 1. Démarrer le gateway

```bash
cd C:\Dev\ollama-gateway
python main.py
```

### 2. Vérifier la connexion

```bash
curl http://localhost:4000/health
```

### 3. Installer Continue.dev

- Ouvrir VSCode
- Extensions → Rechercher "Continue"
- Installer
- Copier la config ci-dessus dans config.json

### 4. Tester

- `Ctrl+L` dans VSCode
- Sélectionner "🤖 Orchestrate (Multi-AI)"
- Poser une question complexe

---

## Troubleshooting

### "Connection refused"

```bash
# Vérifier que le gateway tourne
curl http://localhost:4000/health

# Redémarrer si nécessaire
python main.py
```

### "Model not found"

- Vérifier que Ollama tourne : `ollama list`
- Vérifier config.json correspond à vos modèles installés

### "Slow response"

- Les modèles lourds (qwen2.5-coder:7b) prennent 5-10s
- Utilisez "⚡ Fast (Llama3.2)" pour des réponses rapides
- L'orchestration prend 20-60s (multiple modèles)

---

## Comparaison Extensions

| Extension    | Autocomplete | Chat | Edit | Orchestration |
| ------------ | ------------ | ---- | ---- | ------------- |
| Continue.dev | ✅           | ✅   | ✅   | ✅            |
| Cline        | ❌           | ✅   | ✅   | ✅            |
| Cody         | ✅           | ✅   | ✅   | ✅            |
| Tabnine      | ✅           | ❌   | ❌   | ❌            |

**Recommandation** : Continue.dev pour fonctionnalités complètes

---

## Roadmap

- [ ] Support streaming dans Continue.dev
- [ ] Presets de configuration pour différents langages
- [ ] Intégration avec GitHub Copilot Chat
- [ ] Dashboard VSCode intégré
- [ ] Statistiques d'utilisation par extension

---

## Support

**Gateway ne répond pas** :

1. Vérifier `python main.py` est actif
2. Tester `curl http://localhost:4000/health`
3. Vérifier les logs du gateway

**Extension ne se connecte pas** :

1. Vérifier l'URL est `http://localhost:4000/v1` (avec /v1)
2. Vérifier apiKey est `"not-needed"` (requis même si vide)
3. Redémarrer VSCode après changement de config

---

**Créé pour une intégration transparente de vos 5 modèles Ollama locaux dans VSCode** 🚀
