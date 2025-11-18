# 🗺️ Ollama Gateway - Roadmap v2.0 → v3.0

**Vision**: Le dashboard Ollama le plus puissant ET accessible au monde
**Timeline**: Q1-Q2 2025
**Philosophy**: Local-first, Privacy-first, Accessibility-first

---

## 📊 État Actuel - v1.3.0 ✅

| Feature | Status | Notes |
|---------|--------|-------|
| Gateway OpenAI-compatible | ✅ 100% | 9 modèles locaux |
| Studio Dashboard | ✅ 100% | Chat, projects, streaming |
| Accessibilité WCAG 2.1 AA | ✅ 100% | Seul dashboard Ollama certifié |
| Code Quality (3 niveaux) | ✅ 100% | Black, Flake8, pre-commit |
| LocalStorage persistence | ✅ 100% | ~50-200 messages/projet |

**Limitations actuelles**:
- ❌ Pas de contexte partagé entre projets
- ❌ Pas de fichiers joints
- ❌ Pas de graphiques/visualisations
- ❌ Limite LocalStorage (~5-50 Mo)
- ❌ Pas de RAG local

---

## 🎯 v2.0 - Storage & Performance (Prio 1)

**ETA**: Ce soir → 3 jours
**Objectif**: 10x capacité de stockage + export/import

### Features

#### 1. Migration IndexedDB
**Why**: LocalStorage = 5-10 MB max, IndexedDB = 50-100 MB (10-20x)

```javascript
// Nouvelle architecture
- LocalStorage (v1.x) → IndexedDB (v2.0)
- Schéma: projects, messages, attachments, settings
- Migration automatique depuis LocalStorage
- Fallback graceful si IndexedDB indisponible
```

**Gains**:
- ✅ 1000+ messages par projet (vs 50-200 actuellement)
- ✅ Recherche full-text dans IndexedDB
- ✅ Transactions ACID
- ✅ Support multi-onglets (SharedWorker)

#### 2. Compression LZ-String
**Why**: Réduire empreinte mémoire ~60%

```javascript
import LZString from 'lz-string';

// Compression des messages longs
compressedContent = LZString.compressToUTF16(message.content);
// Décompression à la lecture
originalContent = LZString.decompressFromUTF16(compressedContent);
```

**Gains**:
- ✅ 2-3x plus de messages stockables
- ✅ Réponses longues (code, documents) compressées
- ✅ Transparent pour l'utilisateur

#### 3. Export/Import JSON
**Why**: Portabilité, backup, partage

```javascript
// Export
exportProject(projectId) → project-chess-2025-11-18.json

// Import
importProject(file) → Merge intelligent ou création nouveau projet
```

**Features**:
- ✅ Export d'un projet → JSON
- ✅ Export ALL projects → ZIP
- ✅ Import avec détection de doublons
- ✅ Validation schema avant import

#### 4. UI Improvements
- ✅ Barre de progression "X messages / capacité max"
- ✅ Bouton "Export projet" dans menu projet
- ✅ Settings panel (gear icon) → Import/Export/Clear
- ✅ Notification si proche de la limite

### Technical Stack

```javascript
// Dependencies à ajouter
{
  "idb": "^8.0.0",              // IndexedDB wrapper (Jake Archibald)
  "lz-string": "^1.5.0",        // Compression
  "file-saver": "^2.0.5"        // Export fichiers
}
```

### Migration Strategy

```javascript
// Auto-migration au chargement
1. Détection version actuelle (localStorage.getItem('version'))
2. Si v1.x → Migration vers IndexedDB
3. LocalStorage → archive (backup)
4. Set version = v2.0
```

---

## 🧠 v2.1 - RAG & Knowledge Base (Prio 2)

**ETA**: J+4 → J+10
**Objectif**: Contexte riche + attachments

### Features

#### 1. @Attachments System

**Drag & Drop Interface**:
```html
<div id="attachment-zone">
  📎 Drop files here or click to browse
  Supported: .txt, .py, .js, .md, .pdf, .csv, .png, .jpg
</div>
```

**Formats Supportés**:
| Type | Extensions | Processing |
|------|-----------|------------|
| Text | .txt, .md, .py, .js, .json | Direct UTF-8 |
| PDF | .pdf | pdf.js → text extraction |
| CSV | .csv | Parse → JSON table |
| Images | .png, .jpg, .svg | OCR (tesseract.js) + base64 |

**Storage**:
```javascript
// IndexedDB schema
attachments: {
  id: UUID,
  projectId: string,
  filename: string,
  type: 'text' | 'pdf' | 'csv' | 'image',
  content: string | ArrayBuffer,
  size: number,
  uploadedAt: timestamp,
  embedding: Float32Array  // Pour RAG
}
```

#### 2. Local RAG (Retrieval-Augmented Generation)

**Pipeline**:
```
1. User uploads document.pdf
2. Extract text → Chunk (512 tokens)
3. Generate embeddings (nomic-embed-text via Ollama)
4. Store chunks + embeddings dans IndexedDB
5. User query → Embed query → Cosine similarity search
6. Inject top-K chunks dans contexte LLM
```

**Ollama Embedding Models**:
```bash
# Télécharger embedding model local
ollama pull nomic-embed-text       # 137M, très rapide
# ou
ollama pull bge-m3                 # Multilingual
```

**JavaScript Implementation**:
```javascript
async function embedText(text) {
  const response = await fetch(`${OLLAMA_URL}/api/embeddings`, {
    method: 'POST',
    body: JSON.stringify({
      model: 'nomic-embed-text',
      prompt: text
    })
  });
  const { embedding } = await response.json();
  return embedding; // Float32Array
}

async function semanticSearch(query, topK = 3) {
  const queryEmbed = await embedText(query);
  const allChunks = await db.chunks.toArray();

  // Cosine similarity
  const scores = allChunks.map(chunk => ({
    chunk,
    score: cosineSimilarity(queryEmbed, chunk.embedding)
  }));

  return scores.sort((a, b) => b.score - a.score).slice(0, topK);
}
```

#### 3. @Knowledge-Base

**Concept**: Projet spécial "📚 Library" partageable

```javascript
// Projet type "knowledge-base"
{
  id: 'kb-global',
  name: '📚 Knowledge Base',
  type: 'library',
  shared: true,  // Accessible par tous les autres projets
  attachments: [...],
  chunks: [...],
  embeddings: [...]
}
```

**Usage**:
```
User dans "Chess Project":
"@library Cherche dans ma knowledge base comment implémenter Glicko-2"

→ RAG search dans projet "📚 Library"
→ Inject résultats dans contexte
→ LLM répond avec contexte enrichi
```

#### 4. UI Enhancements

```html
<!-- Attachment panel in chat -->
<div id="attachments-panel">
  <h3>📎 Attachments (3)</h3>
  <div class="attachment-item">
    <span>📄 glicko2-spec.pdf</span>
    <button aria-label="Remove">❌</button>
    <span class="size">1.2 MB</span>
  </div>
</div>

<!-- Knowledge base selector -->
<select id="kb-select">
  <option value="">No knowledge base</option>
  <option value="kb-global">📚 Global Library</option>
  <option value="kb-chess">♟️ Chess Resources</option>
</select>
```

### Technical Stack

```javascript
{
  "pdf.js": "^4.0.0",           // PDF parsing
  "papaparse": "^5.4.1",        // CSV parsing
  "tesseract.js": "^5.0.0",     // OCR (optionnel)
  "vector-db-js": "^1.0.0"      // Local vector DB (optionnel)
}
```

---

## 📊 v2.5 - Charts & Visualizations (Prio 3)

**ETA**: J+11 → J+15
**Objectif**: Graphiques interactifs dans les réponses

### Features

#### 1. Chart.js + ApexCharts Integration

**Auto-detection dans markdown**:
```markdown
User: "Analyse ce CSV de mes parties d'échecs"