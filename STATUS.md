# Status

This file is a quick snapshot of where Wisdom AI stands right now.

## What the project is aiming for

Wisdom AI is a Bhagavad Gita assistant that should feel helpful, grounded, and practical. The main focus is:

- grounded answers from the verses
- a usable chat experience
- a lightweight RAG layer
- a frontend that feels like a real product

## What is in the repo

- fine-tuning scripts for Mistral-7B
- inference and evaluation tools
- a FastAPI backend
- a Next.js frontend
- a small SQLite logging layer

## Data summary

- source dataset: `Bhagwad_Gita.csv`
- total examples: 701
- train split: 630
- validation split: 71
- extra QA pairs: about 3,500

## Training snapshot

- model: `mistralai/Mistral-7B-Instruct-v0.2`
- fine-tuning: LoRA with 4-bit quantization
- current adapter checkpoints exist in the repo history
- best validation loss reported in the docs: `0.590`

## What works today

- single-prompt inference from the CLI
- FastAPI chat endpoint
- Gradio UI
- verse retrieval for grounding
- evaluation on the validation split
- basic logging for chat queries and responses

## What still feels unfinished

- auth is still intentionally lightweight
- some backend data is seeded or simplified
- the frontend and backend still have a few overlapping product paths
- deployment hardening is still a future step

## Docs that matter

- `README.md` for the overview
- `QUICK_START.md` for setup
- `TRAINING_CONFIGS.md` for training options
- `TESTING_GUIDE.md` for UI and batch checks
- `web/README.md` for the frontend

## The honest version

This is a solid prototype that already does useful things, but it is still being consolidated into one clean product. The model layer is the strongest part. The app layer is promising, but it still has some demo-style behavior mixed in.
