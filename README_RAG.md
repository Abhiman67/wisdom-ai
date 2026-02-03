# ⚡ Wisdom AI - RAG Edition (Fast Deployment)

This version replaces the fine-tuned model with a high-speed RAG architecture using **ChromaDB** and **Google Gemini / OpenAI**.

## 🚀 Quick Start

### 1. Install Dependencies (If not already done)
```bash
pip install -r requirements_rag.txt
```

### 2. Run the App
```bash
python app.py
```
*   Open `http://localhost:7860` in your browser.
*   Enter your **Gemini API Key** or **OpenAI API Key** in the UI.
*   Ask questions!

---

## 🐳 Docker Deployment (The "Fastest" Way)

To deploy the whole site quickly:

1.  **Build**
    ```bash
    docker build -t wisdom-ai .
    ```

2.  **Run**
    ```bash
    docker run -p 7860:7860 -e GEMINI_API_KEY="your-key" wisdom-ai
    ```

## 🧠 Architecture
- **App**: `app.py` (Gradio + RAG Logic)
- **Database**: `./chroma_db` (Contains 701 Gita verses)
- **Indexer**: `build_index.py` (Re-run if you change data)
- **Model**: External API (No local GPU needed!)
