# Wisdom Ai

Wisdom Ai is a Bhagavad Gita–grounded assistant that explains teachings, answers questions, and offers practical interpretations. It fine-tunes Mistral-7B with LoRA (4-bit), adds lightweight retrieval (RAG), and provides both a Gradio web UI and a FastAPI backend for interactive use.

Current Phase: Phase 7 – Production Features | Training Target: 15 epochs (3 epochs completed on verses + ~3,500 QA)

## 🎯 Project Overview

### Phase/Status
- Current Phase: Phase 7 – Production Features (7A complete)
- Training Coverage: 3 epochs on verse dataset (630 train / 71 val) and ~3,500 QA pairs
- Target: Plan to extend training up to 15 epochs for higher quality

### Goal
Wisdom Ai fine-tunes `mistralai/Mistral-7B-Instruct-v0.2` with LoRA (4-bit) and adds light RAG, a Gradio web UI, and a FastAPI backend to explain teachings, answer questions, and provide practical interpretations.

### Dataset
- Source: `Bhagwad_Gita.csv` (701 verses with Sanskrit, transliteration, meanings)
- Training: 630 examples (`Bhagwad_Gita_train.jsonl`)
- Validation: 71 examples (`Bhagwad_Gita_val.jsonl`)
- Additional: ~3,500 Bhagavad Gita Question–Answer pairs (custom QA dataset)
- Token stats: min=220, max=387, mean=276, all fit in 512 tokens

### Training Setup
**Hardware:** RTX 4050 Laptop GPU (6-8 GB VRAM) + 16 GB system RAM  
**Method:** 4-bit quantization + LoRA (rank 8, alpha 32)  
**Base Model:** mistralai/Mistral-7B-Instruct-v0.2 (Apache 2.0, no gating)

### Current Phase
Phase 7 – Production Features
- 7A (Web UI + Batch Tool): ✅ Complete
- 7B–7F (Optimization, API & RAG hardening, deployment): ⏳ In progress
- Training status: Both core datasets (verses and 3,500 QA) fine-tuned for 3 epochs so far; planning extended training up to 15 epochs.

---

## 📁 Repository Contents

### Core Scripts
- `convert_csv_to_jsonl.py` - Convert CSV to instruction-tuning JSONL
- `train_lora.py` - LoRA fine-tuning with 4-bit quantization ⭐ **Enhanced**
- `run_inference.py` - Test model with queries ⭐ **Enhanced**
- `evaluate_model.py` - Systematic evaluation on validation set ⭐ **New**
- `analyze_dataset.py` - Token audit and train/val split utility
- `gradio_ui.py` - Gradio Web UI (Simple Q&A + Chat with streaming)
- `api_server.py` - FastAPI backend (`/health`, `/chat`, `/chat/stream`, admin)

### Data Files
- `Bhagwad_Gita.jsonl` - Full dataset (701 examples)
- `Bhagwad_Gita_train.jsonl` - Training split (630 examples)
- `Bhagwad_Gita_val.jsonl` - Validation split (71 examples)

### Documentation
- `README.md` - This file (project overview)
- `QUICK_START.md` - Complete usage guide with examples ⭐ **New**
- `TRAINING_CONFIGS.md` - 5 training recipes for different scenarios ⭐ **New**
- `STATUS.md` - Current project status and progress ⭐ **New**
- `STATUS_UPDATED.md` - Latest training/phase summary (Phase 6 complete, Phase 7A done)
- `README_WSL.md` - WSL2 + CUDA setup for Windows users
- `requirements.txt` - Python dependencies

### Model Artifacts
- `lora_mistral_bhagavad/` - Saved LoRA adapter and tokenizer (after training)
- `rag_index.pt` / `rag_index_meta.json` - Cached lightweight RAG index

### Backend & Database
- `db/` - SQLite + SQLAlchemy models and CRUD (query/response logs, retrievals, errors)

---

## 🚀 Quick Start

### 1) Environment Setup

```powershell
# In PowerShell, from the project root
cd <path-to-project>  # e.g., your Wisdom Ai folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Install CUDA-enabled PyTorch (cu121 for latest CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt
```

**Note:** If bitsandbytes fails on Windows, see `README_WSL.md` for WSL2 setup.

### 2) Test Inference (CLI)

```powershell
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?"
```

### 3) Launch Web UI (Gradio)

```powershell
.\.venv\Scripts\python.exe gradio_ui.py
# Then open http://localhost:7860
```

### 4) Start API Server (FastAPI)

```powershell
.\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
# Health check: http://localhost:8000/health
# Chat JSON: POST http://localhost:8000/chat
```

### 5) Run Evaluation (Validation Set)

```powershell
.\.venv\Scripts\python.exe evaluate_model.py
# Output: evaluation_results.csv
```

### 6) Train Additional Epochs (If Needed)

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_v2 \
  --num_train_epochs 5 \
  --learning_rate 2e-4
```

**For detailed instructions and all options, see `QUICK_START.md`**

---

## 📊 Current Status

### Training Progress
- **Initial 1-epoch run:** ✅ Complete (train loss: 0.698, val loss: 0.632)
- **3-epoch run:** ✅ Complete (best val loss: 0.590 @ checkpoint-158)
- **Model:** Functional and improved — coherent, fewer template echoes
- **Datasets covered:** Bhagavad Gita verse explanations + ~3,500 QA pairs
- **Planned:** Scale training to ~15 epochs for further quality gains

### Roadmap (Training)
- Now: Validate 3-epoch adapters and run evaluation on combined datasets
- Next: Incremental training toward 15 epochs with early-stopping
- Monitor: Validation loss, coherence, citation accuracy

### Phase Completion
- ✅ Phase 1: Environment setup
- ✅ Phase 2: Dataset preparation (701 examples, 630 train / 71 val)
- ✅ Phase 3: Initial training (1 epoch baseline)
- ✅ Phase 4: Quality improvements (output cleaning, better generation)
- ✅ Phase 5: Evaluation infrastructure (systematic testing)
- ✅ Phase 6: Extended training (3 epochs complete; best checkpoint identified)
- ✅ Phase 7A: Web UI + Batch tool
- ⏳ Phase 7B–7F: Optimization, API hardening, RAG improvements, deployment

### What's Working
- ✅ Model loads and generates responses
- ✅ Answers verse-specific questions
- ✅ Explains concepts like karma yoga, dharma, detachment
- ✅ Automatic output cleaning removes template artifacts
- ✅ Systematic evaluation on 71 validation examples

### What Needs Improvement
- ⚙️ Optimize latency and memory for broader devices
- 📦 Packaging/deployment (Docker/Spaces), auth/rate limits in API
- 🔎 Strengthen RAG sources and citation formatting

**See `STATUS.md` for detailed progress report.**

---

## 🛠️ Phase-by-Phase Guide

### Phase 1: Environment Setup ✅

Created Python 3.11 venv, installed CUDA PyTorch (cu121) and dependencies.

### Phase 2: Dataset Preparation ✅

**Converted CSV to JSONL format:**
```powershell
python convert_csv_to_jsonl.py "C:\Users\shash\Downloads\Bhagwad_Gita.csv"
```

**Analyzed token lengths and created splits:**
```powershell
python analyze_dataset.py Bhagwad_Gita.jsonl \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --train_out Bhagwad_Gita_train.jsonl \
  --val_out Bhagwad_Gita_val.jsonl
```

**Results:**
- 701 total examples → 630 train / 71 validation (90/10 split)
- Token lengths: min=220, max=387, mean=276, 95th percentile=326
- All examples fit within 512 tokens ✅

### Phase 3: Initial Training ✅

**1-epoch baseline run:**
```powershell
accelerate launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --num_train_epochs 1
```

**Results:**
- Train loss: 0.698
- Validation loss: 0.632
- Training time: ~35 minutes
- Model generates coherent responses ✅

### Phase 4: Quality Improvements ✅

**Enhanced `run_inference.py`:**
- Added automatic output cleaning (removes template artifacts)
- Better generation parameters (repetition_penalty, longer outputs)
- CLI flags: `--raw`, `--temperature`, `--top_p`, `--repetition_penalty`

**Usage:**
```powershell
# Clean output (default)
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?"

# Raw output (debugging)
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?" --raw

# Custom parameters
.\.venv\Scripts\python.exe run_inference.py "Explain Chapter 2 Verse 47" \
  --max_new_tokens 400 --temperature 0.8 --repetition_penalty 1.2
```

### Phase 5: Evaluation Infrastructure ✅

**Created `evaluate_model.py`:**
- Tests all 71 validation examples automatically
- Saves results to CSV with expected vs generated outputs
- Reports timing and statistics

**Usage:**
```powershell
# Full evaluation
.\.venv\Scripts\python.exe evaluate_model.py

# Quick test (first 10 examples)
.\.venv\Scripts\python.exe evaluate_model.py --limit 10
```

**Output:** `evaluation_results.csv` - Open in Excel to review quality

### Phase 6: Extended Training ✅ Complete

Best validation loss: 0.590 (epoch 2). See `STATUS_UPDATED.md` and `PHASE7A_COMPLETE.md`.

**Enhanced `train_lora.py` features:**
- ✅ Configurable LoRA parameters (`--lora_r`, `--lora_alpha`)
- ✅ Auto-resume from checkpoint
- ✅ Dataset caching (`--cache_dir`)
- ✅ Checkpoint management (`--save_total_limit`)
- ✅ Load best model at end

### Phase 7: Production Features ⏳ In Progress

**Next steps (documented in `TRAINING_CONFIGS.md`):**
1. Evaluate 3-epoch model quality
2. Choose next training config based on results:
   - Conservative (if overfitting)
   - Aggressive (if underfitting)
   - Polish (refinement)
   - Speed optimized (quick tests)
   - High rank (max quality)
3. Web UI (Gradio): ✅ Complete
4. API (FastAPI) + DB logging: ✅ Initial version
5. Package/deploy model (Docker/Spaces): ⏳ Pending

---

## 📚 Documentation Guide

| File | Purpose | When to Use |
|------|---------|-------------|
| `README.md` | Project overview & phase guide | Start here |
| `QUICK_START.md` | Complete usage guide with examples | Learn how to use everything |
| `TRAINING_CONFIGS.md` | 5 training recipes + decision tree | Choose next training config |
| `STATUS.md` | Detailed current status | Check what's done/pending |
| `README_WSL.md` | WSL2 + CUDA setup | If Windows setup fails |

---

## 🎯 Key Features

### Assistant & RAG ⭐
- **Gita-grounded answers:** Structured prompts that encourage verse citation
- **Lightweight RAG:** Sentence-transformers retrieval with cached index
- **Conversation mode:** Chat with short-term memory and streaming

### Evaluation System ⭐
- **Systematic testing:** All 71 validation examples
- **CSV export:** Easy review in Excel/Sheets
- **Timing stats:** Performance metrics
- **Quick tests:** `--limit` flag for fast checks

### Training Efficiency ⭐
- **Auto-resume:** Picks up from last checkpoint if interrupted
- **Dataset caching:** Tokenize once, reuse for multiple runs
- **Configurable LoRA:** Adjust rank, alpha, dropout via CLI
- **Checkpoint management:** Keep only best N checkpoints

### Web + API ⭐
- **Gradio UI:** Simple Q&A + Chat with streaming
- **FastAPI backend:** `/health`, `/chat`, `/chat/stream`, admin & analytics
- **SQLite logging:** SQLAlchemy models for queries/responses/retrievals/errors

### Configuration Library ⭐
- **5 training recipes:** Pre-configured for different scenarios
- **Decision tree:** Guides which config to use
- **Hyperparameter tables:** Learning rate and LoRA rank comparisons

## 🧰 Tech Stack

- **Core ML:** PyTorch (CUDA), Transformers, PEFT, bitsandbytes, Accelerate
- **Embeddings/RAG:** sentence-transformers (all-MiniLM-L6-v2)
- **Web/UI:** Gradio 4, FastAPI + Uvicorn
- **Data/DB:** Datasets, SQLAlchemy + SQLite
- **Ecosystem:** Hugging Face Hub, safetensors, tokenizers

---

## 💻 Hardware Requirements

**Minimum (Current Setup):**
- GPU: NVIDIA RTX 4050 (6-8 GB VRAM)
- RAM: 16 GB system memory
- Storage: ~20 GB (model cache + checkpoints)
- OS: Windows 10/11 or WSL2 Ubuntu

**Recommended:**
- GPU: RTX 4060 or better (8+ GB VRAM)
- RAM: 32 GB
- Storage: SSD for faster model loading

**Performance:**
- Inference: ~5-10 seconds per query
- Training: ~25-30 minutes per epoch (630 examples)
- Full evaluation: ~7-10 minutes (71 examples)

---

## 🧪 Example Usage

### Basic Q&A
```powershell
.\.venv\Scripts\python.exe run_inference.py "What is the main teaching of Bhagavad Gita?"
```

### Verse-Specific
```powershell
.\.venv\Scripts\python.exe run_inference.py "Explain Chapter 2 Verse 47 in simple terms"
```

### Concept Explanation
```powershell
.\.venv\Scripts\python.exe run_inference.py "What is the difference between karma yoga and bhakti yoga?"
```

### With Custom Parameters
```powershell
.\.venv\Scripts\python.exe run_inference.py \
  "Summarize the teaching of Chapter 3" \
  --max_new_tokens 500 \
  --temperature 0.6 \
  --repetition_penalty 1.3
```

---

## 🔧 Training Configuration Examples

### Continue Training (More Epochs)
```powershell
accelerate launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --num_train_epochs 5 \
  --cache_dir ./cache
```

### Higher Quality (Larger LoRA Rank)
```powershell
accelerate launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_highrank \
  --num_train_epochs 4 \
  --lora_r 16 \
  --lora_alpha 32
```

### Fine-Tuning Polish (Lower Learning Rate)
```powershell
accelerate launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_polished \
  --num_train_epochs 2 \
  --learning_rate 5e-5
```

**See `TRAINING_CONFIGS.md` for 5 complete recipes with explanations.**

---

## 📈 Results & Metrics

### Initial 1-Epoch Model
- Train loss: 0.698
- Validation loss: 0.632
- Output quality: Good, some template echoes
- Answer accuracy: Variable

### Current 3-Epoch Model (Complete)
- Best validation loss: 0.590 (checkpoint-158)
- Final validation loss: ~0.610
- Quality: Cohesive, reduced template echoes, verse-aware responses

### Evaluation Metrics
- Perplexity: TBD (run `evaluate_model.py`)
- Output length: ~276 tokens average
- Inference speed: ~5-10 seconds per query
- Accuracy: Manual review via CSV export

---

## 🐛 Troubleshooting

**Problem: Out of memory error**
- Reduce batch size: `--per_device_train_batch_size 1`
- Reduce sequence length: `--max_seq_length 384`
- Close other GPU applications

**Problem: Training interrupted**
- Training auto-resumes from last checkpoint
- Just run the same command again

**Problem: bitsandbytes errors on Windows**
- Follow `README_WSL.md` for WSL2 setup
- Or use a pre-built bitsandbytes wheel

**Problem: Inference outputs have template echoes**
- Increase repetition penalty: `--repetition_penalty 1.3`
- Use output cleaning (default in run_inference.py)
- Prefer best checkpoint (e.g., `checkpoint-158`)

**See `QUICK_START.md` for more troubleshooting tips.**

---

## 🎓 Next Steps

### After Current Training Completes

1. **Test improved model:**
   ```powershell
   .\.venv\Scripts\python.exe run_inference.py "Your question"
   ```

2. **Run full evaluation:**
   ```powershell
   .\.venv\Scripts\python.exe evaluate_model.py
   ```

3. **Review results:**
   ```powershell
   # Open evaluation_results.csv in Excel
   ```

4. **Decide next training step:**
   - See `TRAINING_CONFIGS.md` decision tree
   - Choose config based on evaluation results
   - Run additional training if needed

### Optional Enhancements

- [ ] Create Gradio web UI for easier testing
- [ ] Export to GGUF for llama.cpp (faster inference)
- [ ] Quantize to 8-bit or GPTQ (smaller size)
- [ ] Deploy as API endpoint (FastAPI)
- [ ] Add conversation memory for follow-ups

---

## 📝 Citation & Credits

**Dataset Source:** Bhagavad Gita verse database  
**Base Model:** Mistral AI - Mistral-7B-Instruct-v0.2 (Apache 2.0)  
**Libraries:** Hugging Face Transformers, PEFT, bitsandbytes, accelerate

---

## 📄 License

This project uses the Mistral-7B-Instruct-v0.2 model which is licensed under Apache 2.0.  
Training scripts and documentation are provided as-is for educational purposes.

---

**Project Status:** Active Development  
**Current Phase:** Phase 7 – Production Features (7A complete)  
**Last Updated:** After Phase 7A completion  
**For detailed status:** See `STATUS_UPDATED.md` and `PHASE7A_COMPLETE.md`


Tips:
- Reduce max_seq_length or increase gradient_accumulation_steps if you hit OOM on the RTX 4050.
- Use --max_steps for smoke tests before full training.

Phase 4: evaluation and inference

- After training, LoRA adapters live in output_dir. Load for inference:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base = "mistralai/Mistral-7B-Instruct-v0.2"
adapter_dir = "C:/Users/shash/Downloads/bhagavad_gita_finetune/lora_mistral_bhagavad"

tokenizer = AutoTokenizer.from_pretrained(base)
model = AutoModelForCausalLM.from_pretrained(base, load_in_4bit=True, device_map="auto")
model = PeftModel.from_pretrained(model, adapter_dir)

prompt = "Explain the key teaching of Chapter 2 verse 47 in simple English."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

- Review outputs qualitatively on multiple verses.
- Optional: compute perplexity or BLEU on a held-out validation split.

Phase 5 (optional): packaging and deployment

- Export adapters plus base model for 4-bit inference (local CLI or API).
- Consider text-generation-inference, AutoGPTQ, or llama.cpp conversions if you need CPU deployment.

Remaining work snapshot

- [x] Verify environment setup (Phase 1) and bitsandbytes support (CUDA torch 2.5.1+cu121 confirmed).
- [x] Token-length audit plus train/validation split (Phase 2) using Mistral tokenizer.
- [ ] Run full training job and monitor metrics (Phase 3).
- [ ] Evaluate quality and save inference helper script or notebook (Phase 4).
- [ ] Package deployment artefacts if required (Phase 5).

Ping me whenever you want help attacking the next checkbox (env setup, token audit, training launch, evaluation, or deployment).