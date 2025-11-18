# Configuration Claude-Code / Continue.dev

## Gateway opérationnel ✅

Votre gateway tourne sur **http://localhost:4000** avec routing intelligent automatique.

## Configuration Continue.dev (VSCode)

### 1. Ouvrir la configuration

`Ctrl+Shift+P` → "Continue: Open config.json"

### 2. Ajouter le modèle

```json
{
  "models": [
    {
      "title": "🤖 Ollama Local (Auto-Routing)",
      "provider": "openai",
      "model": "auto",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    }
  ]
}
```

### 3. Utiliser

`Ctrl+L` → Sélectionner "🤖 Ollama Local (Auto-Routing)" → Posez vos questions !

---

## Configuration Cursor

### Settings → Models → Add Custom Model

- **Provider**: OpenAI Compatible
- **Base URL**: `http://localhost:4000/v1`
- **Model**: `auto`
- **API Key**: laissez vide ou `not-needed`

---

## Test Direct

### Depuis un terminal

```bash
# Question de code
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Write a Python function to calculate factorial"}
    ]
  }'
```

**Résultat** : Route automatiquement vers **deepseek-coder-v2**

```bash
# Question d'échecs
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "What is the best response to 1.e4?"}
    ]
  }'
```

**Résultat** : Route automatiquement vers **deepseek-chess**

---

## Endpoints Disponibles

### OpenAI-Compatible

- `POST /v1/chat/completions` - Chat avec routing auto
- `GET /v1/models` - Liste des modèles

### Gateway-Specific

- `GET /health` - État de santé
- `GET /gateway/models` - Configuration
- `POST /gateway/route` - Tester le routing

---

## Workflow Optimal

**Avant** :
```
Vous → Question → Claude API → $$$ tokens
```

**Maintenant** :
```
Vous → Question code → Continue/Claude-Code → Gateway → deepseek-coder → Réponse
```

**Économie** : ~10-20x moins de tokens Claude

---

## Exemples de Routing

| Prompt | Modèle Sélectionné | Raison |
|--------|-------------------|---------|
| "Write Python code" | deepseek-coder-v2 | Matched: python, code |
| "Explain chess opening" | deepseek-chess | Matched: chess, opening |
| "Translate to French" | qwen2.5 | Matched: translate |
| "Write a story" | gemma2 | Matched: creative, write |
| "Quick answer" | llama3.2 | Matched: quick, fast |
| Autre | mistral | Default |

---

## Logs en Temps Réel

Le gateway affiche les décisions de routing :

```
2025-01-18 10:30:15 - INFO - Routing: deepseek-coder-v2:latest - Best for coding (matched: python, code)
```

---

## Arrêt du Gateway

```bash
# Trouver le processus
ps aux | grep "python main.py"

# Arrêter
kill <PID>

# Ou Ctrl+C dans le terminal si lancé en premier plan
```

---

## Redémarrage

```bash
cd C:\Dev\ollama-gateway
python main.py
```

---

## Prochaines Étapes (P1)

Dashboard autonome avec :
- Interface conversationnelle
- Visualisation temps réel
- Statistiques d'utilisation
- Historique conversations
- Lancement double-clic

À définir ensemble !
