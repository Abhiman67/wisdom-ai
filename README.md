# Wisdom AI

Wisdom AI is a Bhagavad Gita assistant built to answer questions, explain verses, and turn the teachings into practical guidance.

It combines a fine-tuned Mistral-7B model, lightweight retrieval over Gita passages, and a Next.js frontend with a FastAPI backend.

## What this repo contains

- A fine-tuned chat model with LoRA adapters
- A lightweight RAG setup for verse grounding
- A FastAPI backend for chat, logging, and admin endpoints
- A Next.js web app for chat, daily verses, saved verses, reading plans, and admin pages
- Training, evaluation, and dataset utilities

## The data behind it

- Source dataset: `Bhagwad_Gita.csv`
- Full instruction set: 701 examples
- Train split: 630 examples
- Validation split: 71 examples
- Extra QA set: about 3,500 Bhagavad Gita Q&A pairs

The goal is not just to generate spiritual-sounding text. The goal is to stay grounded in the verses and answer in a way that feels useful in everyday life.

## How it is built

- Base model: `mistralai/Mistral-7B-Instruct-v0.2`
- Fine-tuning: LoRA with 4-bit quantization
- Retrieval: sentence-transformer embeddings over Bhagavad Gita passages
- Backend: FastAPI + SQLite logging
- Frontend: Next.js + TypeScript + Tailwind

## What the app currently does

- Ask spiritual or practical questions in chat
- Read a daily verse
- Save verses and browse saved items
- Organize verses into collections
- Follow reading plans
- View a simple admin area

## Repo layout

```text
README.md
QUICK_START.md
STATUS.md
TRAINING_CONFIGS.md
TESTING_GUIDE.md
web/
api_server.py
gradio_ui.py
run_inference.py
evaluate_model.py
train_lora.py
db/
```

## Quick start

### 1) Set up Python

```powershell
cd <path-to-project>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you need CUDA PyTorch, install the matching wheel for your machine first, then install the rest of the requirements.

### 2) Try the model from the command line

```powershell
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?"
```

### 3) Start the FastAPI backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Health check:

```text
http://localhost:8000/health
```

### 4) Run the Gradio UI

```powershell
.\.venv\Scripts\python.exe gradio_ui.py
```

Then open:

```text
http://localhost:7860
```

### 5) Run the web app

```powershell
cd web
npm install
npm run dev
```

If the web app talks to a local backend, set:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Useful scripts

- `run_inference.py` - single prompt inference
- `evaluate_model.py` - run the validation set and export results
- `train_lora.py` - continue or restart LoRA training
- `analyze_dataset.py` - inspect token lengths and splits
- `convert_csv_to_jsonl.py` - convert the source CSV into instruction format
- `batch_process.py` - generate answers for a CSV of questions

## What to expect

The product surface is intentionally broad:

- Chat with the assistant
- Read a verse of the day
- Save verses
- Browse collections
- Follow reading plans
- Open admin views for analytics and moderation

The current implementation is still a mix of polished UI and mock/demo-style backend pieces, so treat it as an active product build rather than a finished production system.

## A few honest notes

- Some auth flows are still mock-based.
- Some admin and analytics endpoints return seeded or simplified data.
- There are multiple assistant paths in the repo, so the codebase is still being consolidated.
- The model and RAG layers are the most serious parts of the system; the surrounding product layer is still catching up.

## Recommended docs

- `QUICK_START.md` for commands and setup
- `STATUS.md` for the current state of the project
- `TRAINING_CONFIGS.md` for training recipes
- `TESTING_GUIDE.md` for verification steps
- `web/README.md` for the frontend-specific setup

## Hardware expectations

- GPU: RTX 4050 class or better is ideal
- RAM: 16 GB minimum, 32 GB is more comfortable
- Storage: plan for model caches and checkpoints

## License and credits

- Base model: Mistral-7B-Instruct-v0.2, Apache 2.0
- Dataset: Bhagavad Gita verse dataset used for instruction tuning and evaluation

If you want, I can also rewrite `QUICK_START.md` and `STATUS.md` so the whole doc set feels consistent in the same voice.
