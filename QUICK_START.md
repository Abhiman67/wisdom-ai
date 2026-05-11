# Quick Start

This guide is the fastest way to get Wisdom AI running locally.

## 1) Set up the Python environment

```powershell
cd <path-to-project>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you need GPU acceleration, install a CUDA-enabled PyTorch wheel that matches your machine before the rest of the requirements.

## 2) Try a prompt in the terminal

```powershell
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?"
```

Useful flags:

- `--raw` to see the uncleaned model output
- `--temperature 0.8` to make answers a little more creative
- `--top_p 0.95` to widen sampling
- `--repetition_penalty 1.2` to reduce looping

## 3) Start the API server

```powershell
.\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Health check:

```text
http://localhost:8000/health
```

Main chat endpoint:

```text
POST http://localhost:8000/chat
```

## 4) Open the Gradio UI

```powershell
.\.venv\Scripts\python.exe gradio_ui.py
```

Then open:

```text
http://localhost:7860
```

## 5) Run the web app

```powershell
cd web
npm install
npm run dev
```

If the frontend should talk to a local backend, set:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 6) Evaluate the model

```powershell
.\.venv\Scripts\python.exe evaluate_model.py
```

To run a small sample instead of the full validation set:

```powershell
.\.venv\Scripts\python.exe evaluate_model.py --limit 10
```

## 7) Continue training

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_v2 ^
  --num_train_epochs 5 ^
  --learning_rate 2e-4
```

## Common training flags

- `--lora_r` controls LoRA rank
- `--lora_alpha` controls LoRA scaling
- `--lora_dropout` adds regularization
- `--resume_from_checkpoint` continues from a saved checkpoint
- `--cache_dir` speeds up repeated runs
- `--save_total_limit` keeps the checkpoint folder tidy

## Troubleshooting

- If the model feels repetitive, raise `--repetition_penalty`.
- If you hit OOM, lower `--max_seq_length` or batch size.
- If Windows CUDA bitsandbytes is painful, use WSL2.
- If evaluation is too slow, use `--limit`.

## Where to read next

- `README.md` for the big picture
- `STATUS.md` for the current project state
- `TRAINING_CONFIGS.md` for training recipes
- `TESTING_GUIDE.md` for sanity checks
- `web/README.md` for the frontend setup
