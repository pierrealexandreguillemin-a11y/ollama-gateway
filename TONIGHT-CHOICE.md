# 🌙 CE SOIR - Quelle Feature On Lance ?

**Statut Actuel**: v1.3.0 ✅ (Gateway + Studio + A11y 100% + Code Quality)

---

## 🎯 Option A: **IndexedDB Migration** (v2.0.0-alpha)

**Temps**: 2-3 heures
**Difficulté**: ⭐⭐⭐ Moyenne
**Impact**: 🚀 10x capacité stockage

### Ce qu'on fait:
```javascript
✅ Schema IndexedDB (projects, messages, settings)
✅ Migration automatique depuis LocalStorage
✅ Fallback gracieux si IndexedDB indisponible
✅ UI: Indicator "42 messages / 1000 max"
✅ Tests basiques
```

### Stack:
```bash
npm install idb  # IndexedDB wrapper (Jake Archibald)
```

### Files Modifiés:
- `studio/app.js` (add DB layer)
- `studio/db.js` (NEW - IndexedDB wrapper)
- `studio/index.html` (add capacity indicator)

### Résultat:
```
v1.3.0: ~50-200 messages/projet (LocalStorage)
      ↓
v2.0.0-alpha: ~1000 messages/projet (IndexedDB)
```

**Tag**: `v2.0.0-alpha`

---

## 🎯 Option B: **Storage Complete** (v2.0.0-beta)

**Temps**: 4-6 heures
**Difficulté**: ⭐⭐⭐⭐ Avancée
**Impact**: 🚀🚀 10x stockage + Export/Import

### Ce qu'on fait:
```javascript
✅ TOUT de l'Option A +
✅ Compression LZ-String (60% gain)
✅ Export projet → JSON
✅ Import projet ← JSON validation
✅ Settings panel (gear icon)
```

### Stack:
```bash
npm install idb lz-string file-saver
```

### Files Modifiés:
- Option A +
- `studio/storage.js` (NEW - compression utils)
- `studio/export.js` (NEW - export/import logic)
- `studio/index.html` (add settings panel)
- `studio/style.css` (settings modal styling)

### Résultat:
```
v1.3.0: ~50-200 messages, pas d'export
      ↓
v2.0.0-beta: ~2000-3000 messages (compressed), export/import JSON
```

**Tag**: `v2.0.0-beta`

---

## 🎯 Option C: **RAG Preview** (v2.1.0-alpha)

**Temps**: Full night (8-10h)
**Difficulté**: ⭐⭐⭐⭐⭐ Expert
**Impact**: 🚀🚀🚀 Game changer

### Ce qu'on fait:
```javascript
✅ TOUT de l'Option B +
✅ Drag & drop files (.txt, .pdf, .py)
✅ Text extraction (pdf.js pour PDFs)
✅ Ollama embeddings (nomic-embed-text)
✅ Vector search basique (cosine similarity)
✅ @attach command dans chat
```

### Stack:
```bash
npm install idb lz-string file-saver pdfjs-dist papaparse
ollama pull nomic-embed-text  # 137M
```

### Files Modifiés:
- Option B +
- `studio/rag.js` (NEW - RAG pipeline)
- `studio/embeddings.js` (NEW - vector ops)
- `studio/attachments.js` (NEW - file handling)
- `studio/index.html` (drag & drop zone)
- Update `studio/app.js` (inject context)

### Résultat:
```
v1.3.0: Simple chat
      ↓
v2.1.0-alpha: Chat + RAG local sur tes documents
              "Explique-moi le Glicko-2" → cherche dans glicko2-spec.pdf uploadé
```

**Tag**: `v2.1.0-alpha`

---

## 🎯 Recommendation Claude

**Pour ce soir, je recommande Option A ou B**:

### ✅ Option A si:
- Tu veux un quick win solide
- Test rapide d'IndexedDB
- Commit avant minuit
- Repos demain

### ✅ Option B si:
- Tu veux une feature complète utilisable
- Export/Import = super pratique quotidiennement
- Motivation pour 4-6h focus
- Repos demain après-midi

### ⚠️ Option C seulement si:
- Tu es ultra motivé
- Full night coding session
- Week-end libre demain
- Tu veux impressionner tout le monde avec RAG local 😎

---

## 🚀 Ma Suggestion Perso

**Option B (v2.0.0-beta)** parce que:

1. **Fondation solide**: IndexedDB + Compression = base pour tout le reste
2. **Feature killer**: Export/Import = utilisable immédiatement
3. **Temps raisonnable**: 4-6h = faisable ce soir
4. **Milestone propre**: v2.0.0-beta = tag clean pour demain matin

**Planning**:
```
22h00 - 23h30 → IndexedDB schema + migration (1.5h)
23h30 - 01h00 → LZ-String compression (1.5h)
01h00 - 02h30 → Export/Import logic (1.5h)
02h30 - 03h30 → Settings UI + tests (1h)
03h30 - 04h00 → Commit + tag + docs (30min)

Total: ~6h → v2.0.0-beta DONE 🎉
```

---

## 📝 Ton Choix ?

**Réponds juste**:
- `A` → IndexedDB migration (2-3h)
- `B` → Storage complete (4-6h) ← RECOMMENDED
- `C` → RAG preview (8-10h)
- `ROADMAP` → Finir le ROADMAP.md d'abord
- `DEMAIN` → On se repose ce soir, on attaque demain

**Je suis prêt quand tu l'es** 💪🔥
