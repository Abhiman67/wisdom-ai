# RAG-Only Logic & Fast Deployment Plan

## 🎯 Objective
Transition Wisdom AI from a complex fine-tuned Local LLM to a high-speed, lightweight **RAG (Retrieval-Augmented Generation)** architecture.
**Goal**: Deploy a working Bhagavad Gita AI site immediately.

## ⚡ Strategy: "Travel Light"
1.  **Remove Weights**: Stop loading the 7B model locally.
2.  **RAG Engine**: Use `Chromadb` to index verses from `Bhagwad_Gita.jsonl`.
3.  **Brain**: Switch to a fast Cloud API (Gemini 1.5 Flash or GPT-4o-mini). This removes the need for GPUs and 16GB RAM.
4.  **Interface**: Polished Gradio Web App.

---

## 🛠️ Implementation Steps

### 1. Data Indexing (`build_index.py`)
- **Source**: `Bhagwad_Gita.jsonl`
- **Action**:
    - Extract Sanskrit, Transliteration, and English Translation.
    - Create embeddings (using `sentence-transformers/all-MiniLM-L6-v2` - small, free, local).
    - Store in `./chroma_db`.

### 2. The Application (`app.py`)
Replaces `gradio_ui.py` with a lighter version:
- **Startup**: Loads ChromaDB (instant).
- **Query**:
    - Embed user question.
    - Retrieve top 3 relevant verses.
    - **Prompt**: "You are a Krishna-like guide. Answer based on these verses: [Context]. Question: [Query]"
    - **Generate**: Call LLM API.
- **UI**: Clean chat interface with "Reference Verses" expandable section.

### 3. Deployment (`Dockerfile`)
Since we removed the 15GB model, we can verify easily:
- Docker Image size: ~2GB (vs 10GB+ before).
- Startup time: ~5 seconds (vs 60s before).
- Deployable on: HuggingFace Spaces (Free Tier compatible!), Render, Railway.

---

## 📝 Configuration Requirements
You will need **ONE** of these API keys:
- **Google Gemini API Key** (Free tier available, recommended for speed/cost).
- **OpenAI API Key**.

## 🚀 Execution Order
1.  [ ] **Archive** old model files (cleanup).
2.  [ ] **Create** `build_index.py` and run it (builds the brain).
3.  [ ] **Create** `app.py` (the new interface).
4.  [ ] **Create** `Dockerfile`.
5.  [ ] **Deploy**.
