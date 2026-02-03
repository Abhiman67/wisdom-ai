# Bhagavad Gita AI Assistant — Project Report

**Date:** November 19, 2025
**Prepared by:** Development Team
**File:** `PROJECT_REPORT.md`

---

## Executive Summary

This project builds a Bhagavad Gita–focused AI assistant that combines a fine-tuned large language model (Mistral-7B-Instruct) with a Retrieval-Augmented Generation (RAG) pipeline. The aim is to provide spiritually-grounded, traceable, and helpful responses to user questions while minimizing hallucinations. We developed a full-stack application (FastAPI backend + Next.js frontend) that supports token-streaming responses, admin analytics, and comparison tools.

Key accomplishments
- Fine-tuned `mistralai/Mistral-7B-Instruct-v0.2` using LoRA adapters (3 epochs).
- Built a RAG index of Bhagavad Gita passages and integrated retrieval into the prompt flow.
- Implemented a production-style API server with SSE streaming (`/chat/stream`) and a modern Next.js UI with 19 pages.
- Admin dashboard with RAG ON/OFF comparison, global RAG toggle in settings, and analytics.
- Improved UX: loading states, retry flows, accessibility, and keyboard shortcuts.

Status: MVP functional — training and evaluation completed; productization and UX refinements largely done.

---

## Purpose & Scope

Purpose: Produce a domain-specific assistant that answers questions using Bhagavad Gita teachings with grounded citations and human-friendly explanations.

Scope delivered:
- Dataset preparation (JSONL), LoRA training, evaluation script, RAG pipeline, API server, Next.js frontend, admin tools, and UX polish.

Out of scope (for this phase): persistent production DB, email/notification delivery, multi-user production auth, Dockerized CI/CD pipeline.

---

## Technical Summary

Architecture overview
- Data: JSONL training dataset (instruction-style). RAG uses `sentence-transformers/all-MiniLM-L6-v2` embeddings and an in-memory vector index persisted as `rag_index.pt` and metadata `rag_index_meta.json`.
- Model: `mistralai/Mistral-7B-Instruct-v0.2` with LoRA adapters; inference via Hugging Face Transformers and BitsAndBytes (4-bit load where applicable).
- Backend: FastAPI exposes `/chat`, `/chat/stream`, `/admin/*`, `/health` and other utility routes. RAG and embedder load at startup to avoid cold-call overhead.
- Frontend: Next.js 14 with TailwindCSS; SSE streaming support, admin pages, and client-side RAG toggle persisted in localStorage.

Key files
- `train_lora.py` — training harness, LoRA config, auto-resume, CLI flags.
- `evaluate_model.py` — runs validation set, writes `evaluation_results.csv`.
- `api_server.py` — FastAPI application (model load, RAG integration, endpoints).
- `web/` — Next.js web client with pages and components.

---

## Dataset & Training

Dataset
- Current dataset size: **701 examples** (630 train / 71 validation). Format: JSONL with fields `instruction`, `input`, `output`.
- Domain coverage: verse explanation, short Q&A, persona prompts, and short contextual passages.

Training summary
- Training strategy: LoRA adapter training on top of Mistral-7B-Instruct with gradient accumulation to account for limited GPU RAM.
- Hyperparameters (used for the 3-epoch run):
  - Learning rate: `2e-4`
  - LoRA rank (r): `8`
  - LoRA alpha: `16`
  - Batch size effective: `4` (accumulated)
  - Max sequence length: 512

Results
- Training loss: decreased from ~0.87 → 0.37 (end of epoch 3).
- Validation loss: stabilized at **0.59** (balanced generalization).

Notes: Additional dataset expansion to 2–3k examples is recommended for robust coverage before production rollout.

---

## RAG (Retrieval) Implementation

- Embedder: `sentence-transformers/all-MiniLM-L6-v2`.
- Index: Built at startup; saved/loaded from `rag_index.pt` and `rag_index_meta.json`.
- Retrieval: `retrieve_contexts()` returns top-k contexts which are injected into prompt templates.
- Benefit: Dramatically reduces verse hallucination; admin RAG comparison shows improved citation accuracy.

Performance
- Cold-start: initial index + model load ~30–40s.
- Warm queries (after startup): ~2–5s depending on response length and RAG size.

---

## Backend & API

Endpoints of interest
- `GET /health` — health check
- `POST /chat` — synchronous chat (returns full reply)
- `POST /chat/stream` — SSE streaming endpoint using `TextIteratorStreamer`
- Admin endpoints: `/admin/analytics`, `/admin/analytics/engagement`, `/admin/analytics/verse-popularity`, `/admin/system-health`, `/admin/recent-activity`

Runtime notes
- The server preloads embedder and model at startup to minimize per-request latency.
- In-memory stores are used for sessions and user data (suitable for demo/MVP); we recommend migrating to PostgreSQL or SQLite for persistent storage.

---

## Frontend (UX) Summary

- Framework: Next.js 14 (React) + Tailwind CSS.
- Pages: 19+ pages, including Chat, Daily Verse, Saved Verses, Collections, Reading Plans, Admin dashboard, RAG comparison tool, and Auth flows.
- Improvements added:
  - Loading skeletons and retry flows
  - SSE streaming support (server-side)
  - Admin RAG comparison and RAG toggle (localStorage)
  - Accessibility: ARIA labels, keyboard support (Enter/Escape)

UX considerations: further polish recommended — toast notifications, mobile breakpoints, and optimistic UI for saves.

---

## Evaluation & Testing

- Evaluation dataset: 71 validation examples.
- Tools: `evaluate_model.py` produces `evaluation_results.csv` with expected vs generated outputs and timing.
- Observed behavior: With RAG ON, the assistant cites verses and is more factual. Without RAG, model is more fluent but may misattribute citations.

Suggested tests prior to supervisor demo
1. Run 20 targeted queries comparing RAG vs non-RAG and capture differences.
2. Run `evaluate_model.py --limit 71` and open `evaluation_results.csv` for review.

---

## Known Issues & Risks

- Persistence: user data and saved verses are currently in-memory (volatile on restart).
- Cold-start latency: first start takes 30–40 seconds (model + index load). Consider checkpoint warmers or container warm starts.
- Security: authentication is minimal; production should implement JWT + HTTPS + password hashing.
- Dataset quality: current dataset size limits coverage; some edge-case queries may still hallucinate.

---

## Deployment & Run Instructions

Local dev (Windows PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8='1'
$env:PYTHONWARNINGS='ignore'
.\.venv\Scripts\python.exe -m uvicorn api_server:app --port 8000 --log-level info
```

Frontend (in project `web/` folder):
```powershell
# from web/
# set API base if needed
#$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Quick checks
- Health: `curl http://localhost:8000/health` → `{ "ok": true }`
- Chat (non-stream):
```powershell
Invoke-RestMethod -Uri http://localhost:8000/chat -Method POST -Body (ConvertTo-Json @{ message = "Give me a calming verse about detachment." }) -ContentType 'application/json'
```

---

## Recommendations & Next Steps (to present to supervisor)

High priority (2–7 days)
- Migrate in-memory stores to SQLite/Postgres (user data persistence).
- Add simple JWT-based auth and secure cookies for sessions.
- Expand dataset to 2–3k curated examples and retrain (or fine-tune further with low LR).

Medium priority (2–4 weeks)
- Dockerize backend and frontend; add a minimal CI workflow for deployment.
- Add automated integration tests (Playwright) for core flows: login, chat, save verse, admin toggles.
- Provide an admin-configurable RAG index rebuild endpoint and job monitoring.

Low priority / Nice-to-have
- PWA or mobile wrapper, GGUF export for CPU-only inference, offline evaluation dashboard, user study and UX telemetry.

---

## Appendix

Artifacts produced (important files)
- `train_lora.py` — LoRA training script
- `evaluate_model.py` — evaluation harness
- `api_server.py` — FastAPI backend
- `web/` — Next.js frontend
- `lora_mistral_bhagavad/` — output LoRA adapters (model artifacts)
- `evaluation_results.csv` — latest evaluation outputs

Contact / support
- For any questions or to run an extended demo for your supervisor, I can prepare a 10–15 minute walkthrough showing RAG vs non-RAG comparisons, evaluation results, and sample prompts.

---

**Prepared on**: November 19, 2025

# Bhagavad Gita AI Assistant: Project Report

**Date:** November 19, 2025  
**Project Status:** Phase 7 (MVP Complete / Refinement)  
**Model:** Fine-tuned Mistral-7B-Instruct-v0.2 + RAG  

---

## 1. Executive Summary

This project aimed to build a domain-specific AI assistant capable of answering life questions and philosophical queries based on the teachings of the *Bhagavad Gita*. Unlike generic LLMs, which often hallucinate verses or provide superficial answers, this system uses a hybrid approach combining **Parameter-Efficient Fine-Tuning (PEFT/LoRA)** with **Retrieval-Augmented Generation (RAG)**.

**Key Achievements:**
- Successfully fine-tuned `Mistral-7B-Instruct-v0.2` on 701 Gita-specific examples.
- Achieved a validation loss of **0.59** after 3 epochs.
- Developed a full-stack application (FastAPI backend + Next.js frontend) with 19+ pages.
- Implemented a "Gita-only" persona that cites specific chapters and verses.
- Built an Admin Dashboard with analytics, moderation, and RAG comparison tools.

---

## 2. Project Objectives

1.  **Domain Adaptation:** Adapt a general-purpose LLM to the specific linguistic style and philosophical content of the Bhagavad Gita.
2.  **Hallucination Reduction:** Ensure the model cites actual verses rather than inventing them.
3.  **Contextual Grounding:** Use RAG to retrieve exact verse text to support the model's generation.
4.  **User Experience:** Create a modern, accessible web interface for users to seek guidance (e.g., "I am feeling sad").

---

## 3. System Architecture

The system employs a **Hybrid Neuro-Symbolic Architecture**:

1.  **Data Layer:**
    *   Source: CSV dataset converted to JSONL (Instruction/Input/Response format).
    *   Size: 701 total examples (630 Train / 71 Validation).
    *   Vector Store: In-memory tensor cache using `sentence-transformers/all-MiniLM-L6-v2` embeddings.

2.  **Model Layer:**
    *   **Base Model:** `mistralai/Mistral-7B-Instruct-v0.2` (4-bit quantized).
    *   **Adapter:** LoRA (Low-Rank Adaptation) weights trained for 3 epochs.
    *   **Inference Engine:** Hugging Face Transformers + BitsAndBytes.

3.  **Application Layer:**
    *   **Backend:** Python FastAPI (handling `/chat`, `/health`, `/admin` routes).
    *   **Frontend:** Next.js 14 (React) with Tailwind CSS.
    *   **Communication:** REST API (with SSE streaming capability).

---

## 4. Implementation Phases & Status

| Phase | Objective | Status | Key Outcomes |
| :--- | :--- | :--- | :--- |
| **0** | **Environment Setup** | ✅ Complete | Virtual env, CUDA setup, dataset cleaning. |
| **1** | **Optimization** | ✅ Complete | Inference scripts, memory optimization (4-bit loading). |
| **2** | **Baseline Training** | ✅ Complete | 1-epoch LoRA run to establish baseline performance. |
| **3** | **Extended Training** | ✅ Complete | 3-epoch training run. Loss dropped from 0.87 to 0.37. |
| **4** | **Evaluation** | ✅ Complete | Validation on 71 examples. Avg response time ~9s (GPU). |
| **5** | **Documentation** | ✅ Complete | Implementation plans, status logs, and recipes. |
| **6** | **Productization** | ✅ Complete | Gradio UI, RAG integration, Persona enforcement. |
| **7** | **Full-Stack Web App** | 🔄 In Progress | Next.js frontend, Admin Dashboard, User Auth flows. |

---

## 5. Technical Performance

### 5.1 Training Metrics
*   **Training Loss:** Decreased consistently from **0.87** (start) to **0.37** (end of Epoch 3).
*   **Validation Loss:** Stabilized at **0.59**, indicating good generalization without overfitting.
*   **Hyperparameters:**
    *   Learning Rate: `2e-4`
    *   LoRA Rank (r): `8`
    *   LoRA Alpha: `16`
    *   Batch Size: `4` (with gradient accumulation)

### 5.2 Inference Latency (RAG ON)
*   **Cold Start:** ~30-40s (Model load + Index build).
*   **Warm Query:** ~2-4s (depending on output length).
*   **Optimization:** Implemented LRU caching for query embeddings to speed up repeated questions.

### 5.3 RAG vs. Non-RAG Comparison
*   **Without RAG:** Model captures the "vibe" of the Gita but occasionally misattributes verse numbers.
*   **With RAG:** Model consistently cites the correct verse provided in the context window.
*   **Admin Tool:** Built a "RAG Comparison" tool in the dashboard to visualize this difference side-by-side.

---

## 6. Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **Hallucinations** | Enforced a "System Persona" in the prompt and enabled RAG by default to ground answers in retrieved text. |
| **Latency (50s+)** | Identified cold-start overhead in RAG. Moved embedder initialization to server startup (pre-loading), reducing query time to <5s. |
| **Environment Hell** | Resolved conflicts between `unsloth`, `torch`, and `transformers` by pinning stable versions (`torch 2.5.1`, `transformers 4.46`). |
| **Frontend Integration** | Built a FastAPI middleware to bridge the Python ML backend with the Next.js React frontend. |

---

## 7. Future Roadmap

1.  **Dataset Expansion:**
    *   Current dataset (701 rows) is small. Plan to scrape 2,000+ verses with commentary to improve coverage.
2.  **Database Integration:**
    *   Migrate from in-memory storage to PostgreSQL/SQLite for persistent user profiles and saved verses.
3.  **Quantization for Deployment:**
    *   Export model to GGUF format to run on lower-resource hardware (or CPU-only environments).
4.  **Mobile App:**
    *   Adapt the Next.js frontend into a PWA (Progressive Web App) for mobile access.

---

## 8. Conclusion

The Bhagavad Gita AI Assistant has successfully graduated from a research experiment to a functional MVP. By combining fine-tuning with retrieval-augmented generation, we have created a system that is both **fluent** (thanks to Mistral-7B) and **faithful** (thanks to RAG). The project is ready for user testing and further data scaling.