# Alternative Training Configurations

This document provides pre-tested configurations for different training scenarios.

## Current Baseline (3-epoch run in progress)
```bash
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 3 \
  --learning_rate 2e-4
```

**Expected results:** Train loss ~0.6-0.7, Eval loss ~0.6-0.65

---

## Config 1: More Conservative (If Overfitting)
**Use if:** Training loss drops but validation loss increases

```bash
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_conservative \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 2 \
  --learning_rate 1e-4 \
  --lora_r 8 \
  --lora_alpha 16
```

**Key changes:**
- Lower learning rate (1e-4 vs 2e-4) = more stable
- Fewer epochs (2 vs 3) = less overfitting risk
- Lower LoRA alpha (16 vs 32) = stronger regularization

---

## Config 2: More Aggressive (If Underfitting)
**Use if:** Both train and validation loss are still high after 3 epochs

```bash
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_aggressive \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 5 \
  --learning_rate 3e-4 \
  --lora_r 16 \
  --lora_alpha 32
```

**Key changes:**
- Higher learning rate (3e-4) = faster convergence
- More epochs (5 vs 3) = more training
- Higher LoRA rank (16 vs 8) = more model capacity

**Note:** Requires adding `--lora_r` and `--lora_alpha` arguments to `train_lora.py` (see implementation below)

---

## Config 3: Fine-Tuning Polish (After Initial Training)
**Use if:** Model works but needs refinement

```bash
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

**Key changes:**
- Very low learning rate (5e-5) = gentle refinement
- 2 epochs = avoid overfitting
- Resume from existing checkpoint if available

---

## Config 4: Speed Optimized (Faster Iteration)
**Use if:** Need quick experiments

```bash
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_fast \
  --max_seq_length 384 \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 4 \
  --num_train_epochs 2 \
  --learning_rate 2e-4
```

**Key changes:**
- Shorter max sequence (384 vs 512) = faster processing
- Larger batch size (2 vs 1) = fewer steps
- Fewer gradient accumulation steps (4 vs 8) = faster feedback
- **Trade-off:** Slightly lower quality, 30-40% faster training

---

## Config 5: Higher LoRA Rank (Maximum Quality)
**Use if:** You have time and want best possible results

```bash
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --data Bhagwad_Gita_train.jsonl \
  --val_data Bhagwad_Gita_val.jsonl \
  --output_dir lora_mistral_bhagavad_highrank \
  --max_seq_length 512 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 4 \
  --learning_rate 2e-4 \
  --lora_r 32 \
  --lora_alpha 64
```

**Key changes:**
- LoRA rank 32 (vs 8) = 4x more trainable parameters
- LoRA alpha 64 (vs 32) = stronger adaptation
- 4 epochs = sufficient training for higher capacity
- **Trade-off:** ~50% slower training, larger adapter size (~200MB vs ~50MB)

---

## Implementation: Adding LoRA Config Arguments

To enable `--lora_r` and `--lora_alpha` in `train_lora.py`, add these lines:

```python
# In argument parser section:
parser.add_argument("--lora_r", type=int, default=8, help="LoRA rank")
parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha")

# In LoraConfig section:
lora_config = LoraConfig(
    r=args.lora_r,  # Changed from hardcoded 8
    lora_alpha=args.lora_alpha,  # Changed from hardcoded 32
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

---

## Hyperparameter Decision Tree

```
Start here: Did 3-epoch baseline complete?
│
├─ NO → Wait for current training to finish
│
└─ YES → Check validation loss:
    │
    ├─ Val loss < 0.6 → Model is good!
    │   └─ Use Config 3 (Fine-Tuning Polish) for refinement
    │
    ├─ Val loss 0.6-0.7 → Model is okay
    │   ├─ If train loss much lower → Try Config 1 (Conservative)
    │   └─ If train loss similar → Try Config 2 (Aggressive)
    │
    └─ Val loss > 0.7 → Model needs more training
        ├─ Quick test needed → Use Config 4 (Speed Optimized)
        └─ Best quality needed → Use Config 5 (High Rank)
```

---

## Quick Reference: Learning Rate Effects

| Learning Rate | Effect | When to Use |
|--------------|--------|-------------|
| 5e-5 | Very stable, slow | Final polishing, avoid overfitting |
| 1e-4 | Stable, moderate | Default safe choice |
| 2e-4 | Standard, efficient | Good starting point (current) |
| 3e-4 | Fast, less stable | When underfitting persists |
| 5e-4+ | Very fast, risky | Not recommended for fine-tuning |

---

## LoRA Rank Trade-offs

| Rank | Parameters | Speed | Quality | Adapter Size |
|------|-----------|-------|---------|--------------|
| 4 | ~6M | Fastest | Lower | ~25 MB |
| 8 | ~12M | Fast | Good | ~50 MB (current) |
| 16 | ~24M | Moderate | Better | ~100 MB |
| 32 | ~48M | Slower | Best | ~200 MB |
| 64 | ~96M | Slowest | Overkill | ~400 MB |

**Recommendation:** Rank 8-16 is the sweet spot for most tasks.
