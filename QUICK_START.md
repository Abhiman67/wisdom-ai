# Quick Start Guide: Using All Improvements

## 1. Improved Inference (Better Output Quality)

### Basic Usage
```powershell
# Clean output (default)
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?"

# Show raw output (for debugging)
.\.venv\Scripts\python.exe run_inference.py "What is karma yoga?" --raw
```

### Advanced Parameters
```powershell
.\.venv\Scripts\python.exe run_inference.py "Explain Chapter 2 Verse 47" \
  --max_new_tokens 400 \
  --temperature 0.8 \
  --top_p 0.95 \
  --repetition_penalty 1.2
```

**New Features:**
- ✅ Automatic output cleaning (removes template artifacts)
- ✅ Better generation parameters (reduced repetition)
- ✅ Longer responses (300 tokens default vs 256)
- ✅ `--raw` flag to see unprocessed output

---

## 2. Systematic Evaluation

### Run Full Evaluation on All 71 Validation Examples
```powershell
.\.venv\Scripts\python.exe evaluate_model.py
```

Output: `evaluation_results.csv` with all generated responses

### Quick Test (First 10 Examples)
```powershell
.\.venv\Scripts\python.exe evaluate_model.py --limit 10
```

### Custom Settings
```powershell
.\.venv\Scripts\python.exe evaluate_model.py \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_csv my_results.csv \
  --max_new_tokens 400 \
  --temperature 0.7
```

**What It Does:**
- Tests model on all validation examples
- Saves results to CSV (expected vs generated outputs)
- Reports timing statistics
- Easy to review in Excel/Sheets

---

## 3. Alternative Training Configurations

All configs are documented in `TRAINING_CONFIGS.md`. Here are the most useful:

### After Current 3-Epoch Run Finishes

**If model needs more training:**
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_v2 \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 5 \
  --learning_rate 2e-4 \
  --lora_r 16
```
*(Higher LoRA rank for more capacity)*

**If model needs gentle refinement:**
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_polished \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 2 \
  --learning_rate 5e-5
```
*(Lower LR for fine-tuning polish)*

---

## 4. Training Efficiency Features

### Resume from Checkpoint (Auto)
If training is interrupted, it will auto-resume:
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad
```
*(Automatically detects and resumes from last checkpoint)*

### Manual Checkpoint Resume
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --resume_from_checkpoint ./lora_mistral_bhagavad/checkpoint-158
```

### Dataset Caching (Speed Up Re-runs)
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_v2 \
  --cache_dir ./dataset_cache \
  --num_train_epochs 5
```
*(Tokenizes once, reuses for subsequent runs - saves ~2-3 seconds)*

### Control Checkpoint Storage
```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --save_total_limit 3
```
*(Keeps only best 3 checkpoints to save disk space)*

---

## Complete Workflow Example

### Step 1: Wait for Current Training (3 epochs)
Check status:
```powershell
# Training should finish in ~60-90 minutes from start
# Look for "Training completed" or check terminal output
```

### Step 2: Test with Improved Inference
```powershell
# Quick test
.\.venv\Scripts\python.exe run_inference.py "What is the essence of Bhagavad Gita?"

# Compare with raw output
.\.venv\Scripts\python.exe run_inference.py "What is the essence of Bhagavad Gita?" --raw
```

### Step 3: Run Full Evaluation
```powershell
# Test on all 71 validation examples
.\.venv\Scripts\python.exe evaluate_model.py

# Review results
# Open evaluation_results.csv in Excel or text editor
```

### Step 4: Decide Next Training Step

**Check the evaluation CSV:**
- Are answers accurate and coherent? → Model is good, maybe do 2 epochs of polishing
- Are answers vague or generic? → Do 2-3 more epochs with same settings
- Are answers completely wrong? → Increase LoRA rank and do 5 epochs

### Step 5: Run Additional Training (if needed)
```powershell
# Example: 2 more epochs with cached dataset
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --num_train_epochs 5 \
  --cache_dir ./dataset_cache
```
*(Will resume from epoch 3 and train to epoch 5)*

---

## New Command-Line Arguments Reference

### run_inference.py
- `--max_new_tokens` (default: 300) - Max response length
- `--temperature` (default: 0.7) - Sampling temperature (higher = more creative)
- `--top_p` (default: 0.9) - Nucleus sampling threshold
- `--repetition_penalty` (default: 1.1) - Penalize repetitive text
- `--raw` - Show unprocessed output (no cleaning)

### train_lora.py (New)
- `--lora_r` (default: 8) - LoRA rank (8, 16, 32)
- `--lora_alpha` (default: 32) - LoRA alpha scaling
- `--lora_dropout` (default: 0.05) - LoRA dropout rate
- `--resume_from_checkpoint` - Path to checkpoint to resume
- `--save_total_limit` (default: 2) - Max checkpoints to keep
- `--cache_dir` - Cache preprocessed datasets here

### evaluate_model.py
- `--val_data` (default: Bhagwad_Gita_val.jsonl) - Validation file
- `--output_csv` (default: evaluation_results.csv) - Output file
- `--limit` - Test only N examples (for quick checks)
- All inference parameters (temperature, top_p, etc.)

---

## Performance Expectations

### Inference Speed
- Load model: ~30 seconds (one-time per session)
- Generate answer: ~5-10 seconds per query
- Full 71-example evaluation: ~7-10 minutes

### Training Speed
- 1 epoch: ~25-30 minutes
- 3 epochs: ~75-90 minutes
- 5 epochs: ~125-150 minutes

### Disk Space
- Base model (cached): ~14 GB
- LoRA adapter: ~50-200 MB (depending on rank)
- Checkpoints (x2): ~100-400 MB
- Dataset cache: ~10 MB

---

## Troubleshooting

**Problem: "Out of memory" error during evaluation**
```powershell
# Use smaller batch for evaluation
.\.venv\Scripts\python.exe evaluate_model.py --limit 20
```

**Problem: Training interrupted, how to resume?**
```powershell
# Just run same command again - it auto-resumes
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py [same args]
```

**Problem: Inference outputs still have template echoes**
```powershell
# Try higher repetition penalty
.\.venv\Scripts\python.exe run_inference.py "..." --repetition_penalty 1.3
```

**Problem: Model generates too short answers**
```powershell
# Increase max tokens
.\.venv\Scripts\python.exe run_inference.py "..." --max_new_tokens 500
```

---

## What Changed?

### run_inference.py
✅ Added output cleaning function  
✅ Increased default max_new_tokens (256→300)  
✅ Added repetition_penalty parameter  
✅ Added `--raw` flag for debugging  

### train_lora.py
✅ Added LoRA config arguments (r, alpha, dropout)  
✅ Added auto-checkpoint resume  
✅ Added dataset caching support  
✅ Added save_total_limit to manage disk space  
✅ Added load_best_model_at_end for validation  

### New Files
✅ `evaluate_model.py` - Full validation testing  
✅ `TRAINING_CONFIGS.md` - 5 pre-configured training recipes  
✅ `QUICK_START.md` - This guide  
