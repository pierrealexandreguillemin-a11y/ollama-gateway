# 🚀 Ollama Gateway - P0

**OpenAI-compatible API gateway for local Ollama models with intelligent routing**

## Objectif

Permettre à Claude-Code, Continue.dev, Cursor, et tout outil compatible OpenAI d'utiliser **vos modèles Ollama locaux** avec routing automatique intelligent.

## Architecture

```
Claude-Code/Continue → Gateway (localhost:4000) → Routing Intelligent → Modèles Ollama
```

## Installation (3 commandes)

```bash
cd C:\Dev\ollama-gateway

# Installer les dépendances
pip install -r requirements.txt

# Lancer le gateway
python main.py
```

Le gateway démarre sur **http://localhost:4000**

## Configuration

### Models configurés (config.json)

| Modèle                      | Rôle         | Tags                                   | Priorité |
| --------------------------- | ------------ | -------------------------------------- | -------- |
| qwen2.5-coder:7b            | coding       | code, python, javascript, debug, etc.  | 1        |
| gemma2                      | creative     | creative, story, write, poem           | 2        |
| huihui_ai/qwen3-abliterated | multilingual | translate, français, english, language | 2        |
| llama3.2                    | fast         | quick, fast, short, simple             | 3        |
| mistral                     | general      | (défaut)                               | 1        |

### Routing Intelligent

Le gateway analyse votre prompt et route automatiquement :

- **"Write a Python function"** → qwen2.5-coder:7b
- **"Translate to French"** → huihui_ai/qwen3-abliterated
- **"Write a story"** → gemma2
- **"Quick answer"** → llama3.2
- **Autre** → mistral

## Utilisation

### 1. Avec Claude-Code / Continue.dev

Dans votre configuration VSCode (Continue ou Claude-Code) :

```json
{
  "models": [
    {
      "title": "Ollama Local (Auto-Routing)",
      "provider": "openai",
      "model": "auto",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "not-needed"
    }
  ]
}
```

### 2. Avec Cursor

Settings → Models → Add Custom Model :

- Provider: OpenAI Compatible
- Base URL: `http://localhost:4000/v1`
- Model: `auto`

### 3. Avec curl (test)

```bash
# Test simple
curl http://localhost:4000/health

# Chat completion (auto-routing)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Write a Python function to reverse a string"}
    ]
  }'
```

### 4. Test de routing

```bash
curl -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain the Sicilian Defense in chess"}'
```

Réponse :

```json
{
  "prompt": "Write a recursive fibonacci in Python",
  "selected_model": "qwen2.5-coder:7b",
  "reason": "Best for coding (matched: python)"
}
```

## Endpoints

### OpenAI-Compatible

- `POST /v1/chat/completions` - Chat completion (avec routing automatique)
- `GET /v1/models` - Liste des modèles disponibles

### Gateway-Specific

- `GET /health` - État de santé
- `GET /gateway/models` - Configuration des modèles
- `POST /gateway/route` - Tester le routing

## Avantages

✅ **Compatible OpenAI** - Fonctionne avec tous les outils existants
✅ **Routing automatique** - Choisit le meilleur modèle selon le prompt
✅ **100% local** - Aucune donnée envoyée au cloud
✅ **Streaming supporté** - Réponses en temps réel
✅ **Économie tokens Claude** - Claude délègue aux modèles locaux
✅ **Phase 2 ready** - Peut fonctionner 100% sans Claude

## Workflow Typique

**Avant** (sans Gateway) :

```
Vous → Question → Claude → Réponse Claude (coûteux en tokens)
```

**Maintenant** (avec Gateway) :

```
Vous → Question code → Claude-Code → Gateway → qwen2.5-coder → Réponse
Vous → Question créative → Claude-Code → Gateway → gemma2 → Réponse
```

**Économie** : ~10-20x moins de tokens Claude consommés

## Logs

Le gateway log toutes les décisions de routing :

```
2025-01-18 10:30:15 - INFO - Received chat completion request
2025-01-18 10:30:15 - INFO - Routing: qwen2.5-coder:7b - Best for coding (matched: code, python)
```

## Prochaines Étapes (P1)

- Dashboard autonome avec conversation
- Visualisation temps réel
- Statistiques d'utilisation
- Historique des conversations
- Export/Import de configurations

## Troubleshooting

**Gateway ne démarre pas** :

- Vérifier que Python 3.9+ est installé
- Vérifier que Ollama tourne (`ollama serve`)

**Modèle non trouvé** :

- Lister vos modèles : `ollama list`
- Vérifier config.json correspond à vos modèles installés

**Pas de réponse** :

- Vérifier logs du gateway
- Tester Ollama directement : `ollama run mistral "Hello"`

## Support

- Gateway créé pour usage avec vos 5 modèles Ollama locaux
- Configuration adaptée à vos modèles spécifiques
- Prêt pour intégration Claude-Code / Continue / Cursor
