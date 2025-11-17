# Wisdom-AI — Bhagavad Gita local pipeline (toy)

This scaffold prepares your provided Bhagavad Gita CSV for training, builds embeddings for retrieval, and contains a tiny fine-tune example (GPT-2 small) plus a minimal Flask chat server that: retrieves relevant verses, generates a short answer with the fine-tuned model, and logs sentiment + metadata for admin monitoring.

This is intentionally a lightweight, local-first setup for experimentation. For production / larger models see the section "Next steps" below.

Quick commands (macOS zsh)

1) Create a virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

2) Prepare data (assumes your CSV is at the same path you already have):

```bash
python scripts/data_prep.py \
  --csv /Users/abhishek/Desktop/wisdom-ai-main/Bhagwad_Gita.csv \
  --out_dir data
```

This creates `data/passages.jsonl` (one verse per line) and `data/instruct.jsonl` (simple prompt/completion pairs for toy fine-tuning).

3) Build embeddings + FAISS index

```bash
python scripts/embed_and_faiss.py --passages data/passages.jsonl --index_dir data
```

4) (Toy) fine-tune GPT-2 small — this is intentionally tiny so it runs on CPU (slow) or faster on GPU/Colab.

```bash
python scripts/train_toy.py --data data/instruct.jsonl --output_dir models/gpt2-bhagavad-toy --epochs 1
```

5) Run the minimal Flask chat server

```bash
python scripts/serve_chat.py --model_dir models/gpt2-bhagavad-toy --faiss_dir data --host 0.0.0.0 --port 7860
```

Then POST to `http://localhost:7860/chat` with JSON `{"user_id":"user1","message":"What is dharma?"}`.

What this scaffold includes
- `scripts/data_prep.py`: CSV -> passages + instruction tuning JSONL
- `scripts/embed_and_faiss.py`: builds sentence-transformers embeddings and FAISS index
- `scripts/train_toy.py`: tiny Hugging Face Trainer fine-tune loop for GPT-2
- `scripts/serve_chat.py`: Flask server with retrieval, generation, sentiment analysis and admin logging
- `requirements.txt` with pinned lightweight packages for local use

Important notes
- The Sanskrit original is public domain, but many modern English translations are copyrighted. Make sure you have rights for any translation included in your CSV. This scaffold will treat whatever is in your CSV as allowed data. If you did not provide a public-domain translation, get permission or remove the translation before training or distributing models.
- Fine-tuning larger models (Llama2, Mistral, 7B+) requires a GPU with substantial VRAM or cloud resources and different tooling (PEFT/LoRA). I can add that flow once you tell me available compute.

Next steps I can do for you
- Add LoRA/PEFT training recipes for a chosen open-weight base model (if you have a GPU)
- Create a nicer web UI (Streamlit / React) with per-user chat history and admin dashboard
- Add user authentication and a simple admin UI to view sentiment/time-series and flagged conversations

If you want me to proceed: tell me whether you have a GPU (and VRAM), and whether the CSV includes copyrighted translations or only public-domain Sanskrit.
# Wisdom AI — Development README

Short guide to get new contributors up and running with the Wisdom AI project (backend + frontend).

This repository includes:
- FastAPI backend (Python) with authentication, chat, RAG/embeddings, admin analytics, media serving.
- Next.js (App Router) frontend in `web/` (TypeScript + Tailwind + shadcn/ui) with cookie-based auth and a modern Chat UI.

---

## Prerequisites

- macOS / Linux / Windows WSL
- Python 3.11 (recommended)
- Node.js 18+ and npm (or pnpm/yarn)
- git
- (Optional) Docker & docker-compose for containerized runs

---

## Quick start (local dev)

1) Clone the repo

```bash
git clone <your-repo-url> wisdom-ai
cd wisdom-ai
```

2) Backend setup

- Create a Python virtual environment and activate it (example using venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Copy example env and edit values if needed:

```bash
cp env.example .env
# Edit .env to configure DB, secrets, or API keys
```

- Initialize or seed the database (if you plan to use the local DB helper scripts):

```bash
python3 database_init.py
# or run any project-specific seed scripts like: python3 setup_llm.py
```

- Start the backend:

```bash
# Option 1: run in-process
python3 start.py
# Option 2: use docker-compose (if configured)
# docker-compose up --build
```

- Backend health endpoint should be reachable at:

```
http://localhost:8000/health
```

3) Frontend setup (Next.js)

- Change to the `web` directory, install deps and start dev server:

```bash
cd web
npm install   # or pnpm install / yarn
npm run dev
```

- The frontend will proxy API calls under `/api/*` to the backend. Ensure the env var `NEXT_PUBLIC_API_BASE_URL` is set when running the frontend (defaults to `http://localhost:8000`). You can set it locally in `.env.local` inside `web/` or rely on the default.

- Open the app: http://localhost:3000

- Verify the proxy health endpoint works:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/health
# should return 200 when backend + frontend dev servers are running
```

---

## Environment variables

- Root `.env` (backend)
	- Configure your database URL, JWT secret, any LLM API keys, and other secrets. See `env.example` for keys used by the backend.

- Frontend `web/.env.local` (optional)
	- `NEXT_PUBLIC_API_BASE_URL` — the backend base URL (defaults to `http://localhost:8000` when not set).

---

## Auth & Security notes

- Auth flow uses the backend to issue JWT access tokens. The Next.js route handlers set an httpOnly cookie named `token` so the frontend does not store tokens in localStorage.
- The `/api/*` Next route proxies attach the `Authorization: Bearer <token>` header using that cookie when calling the backend.
- For production, review cookie `secure`, `sameSite`, `maxAge` and add CSRF protections and CSP headers.

---

## Project layout (important files)

- `main.py` — FastAPI backend entrypoint and routes.
- `requirements.txt` — backend Python deps.
- `web/` — Next.js frontend (TypeScript, Tailwind, shadcn/ui)
	- `web/app` — Next App Router pages and API route handlers that proxy to backend
	- `web/components` — UI components like AppShell, VerseCard, Chat renderer
	- `web/lib/api.ts` — frontend API client helper

- `embeddings/` — generated embeddings and verse metadata (local storage used by the backend).
- `media/` — static media (images / audio) served by the backend.

---

## Developer tips & known quirks

- Editor warnings about `@tailwind` or `@apply` in `web/styles/globals.css` are from plain CSS linters and are harmless when the Tailwind/PostCSS pipeline runs. Install the Tailwind CSS extension in VS Code to reduce false positives.
- The frontend avoids prefetching the heavy Admin bundle from the navbar to keep client JS small.
- We use server-side rendering (SSR) for protected pages (profile, saved, daily-verse, admin analytics) to avoid client fetch loops and speed up LCP.

---

## Running in production / Docker

- A docker-compose file exists for reference. To run in containers:

```bash
docker-compose up --build
```

- Production frontend: build and export within `web`:

```bash
cd web
npm run build
npm run start
```

(If you deploy on Vercel, set `NEXT_PUBLIC_API_BASE_URL` to your backend URL and make sure the backend is reachable.)

---

## Next actions and roadmap (short)

- Add app-level `error.tsx` and `not-found.tsx` for consistent UX.
- Implement email-based password reset flow (request + token + reset form) integrated with backend.
- Add tests (unit + component + E2E) and CI pipeline.
- Security quick wins: CSRF, request rate limiting on chat/admin, CSP headers, cookie review.

---

## Troubleshooting

- If frontend returns `502` from `/api/*` routes, check the backend is running and `NEXT_PUBLIC_API_BASE_URL` is correct.
- If login/signup shows errors, open the browser devtools network tab and check the proxied `/api/login` or `/api/signup` response body — it contains the backend error messages.

---

## Contributing

- Create a branch for your feature/fix and open a PR against `main`.
- Add unit tests for new logic where possible.
- Keep bundles small; dynamic import heavy libs like Recharts or Markdown plugins.

---

If you want, I can also:
- Add a `docs/` folder with developer conventions and a design tokens file.
- Create the `app/error.tsx` and `app/not-found.tsx` pages next.
