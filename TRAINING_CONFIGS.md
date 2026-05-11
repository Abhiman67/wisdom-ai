# Training Configs

This file collects the training setups that make sense for Wisdom AI today.

The short version:

- use the baseline if you want to continue the current run
- use a conservative config if validation starts getting worse
- use a more aggressive config if the model still feels underfit
- use polish if the model is already good and just needs refinement

## Baseline

This is the current style of run the repo documents:

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad ^
  --max_seq_length 512 ^
  --per_device_train_batch_size 1 ^
  --gradient_accumulation_steps 8 ^
  --num_train_epochs 3 ^
  --learning_rate 2e-4
```

## 1) Conservative

Use this when training is improving but validation starts to drift.

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_conservative ^
  --max_seq_length 512 ^
  --per_device_train_batch_size 1 ^
  --gradient_accumulation_steps 8 ^
  --num_train_epochs 2 ^
  --learning_rate 1e-4 ^
  --lora_r 8 ^
  --lora_alpha 16
```

## 2) Aggressive

Use this when the model still feels too weak after the baseline.

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_aggressive ^
  --max_seq_length 512 ^
  --per_device_train_batch_size 1 ^
  --gradient_accumulation_steps 8 ^
  --num_train_epochs 5 ^
  --learning_rate 3e-4 ^
  --lora_r 16 ^
  --lora_alpha 32
```

## 3) Polish

Use this when the model is already decent and you want smaller improvements.

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_polished ^
  --max_seq_length 512 ^
  --per_device_train_batch_size 1 ^
  --gradient_accumulation_steps 8 ^
  --num_train_epochs 2 ^
  --learning_rate 5e-5
```

## 4) Speed run

Use this when you want faster iteration and can live with a small quality tradeoff.

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_fast ^
  --max_seq_length 384 ^
  --per_device_train_batch_size 2 ^
  --gradient_accumulation_steps 4 ^
  --num_train_epochs 2 ^
  --learning_rate 2e-4
```

## 5) High-rank

Use this when you want the adapter to have more capacity.

```powershell
.\.venv\Scripts\python.exe -m accelerate.commands.launch train_lora.py ^
  --model_name mistralai/Mistral-7B-Instruct-v0.2 ^
  --data Bhagwad_Gita_train.jsonl ^
  --val_data Bhagwad_Gita_val.jsonl ^
  --output_dir lora_mistral_bhagavad_highrank ^
  --max_seq_length 512 ^
  --per_device_train_batch_size 1 ^
  --gradient_accumulation_steps 8 ^
  --num_train_epochs 4 ^
  --learning_rate 2e-4 ^
  --lora_r 32 ^
  --lora_alpha 64
```

## A simple way to choose

- validation loss creeping up: choose conservative
- answers still too vague: choose aggressive
- answers already good: choose polish
- need quick iteration: choose speed run
- want the largest adapter: choose high-rank

## Useful training flags

- `--resume_from_checkpoint` continues from a checkpoint
- `--cache_dir` speeds up repeated runs
- `--save_total_limit` keeps the checkpoint folder manageable
- `--lora_dropout` adds regularization

## Keep in mind

These are not laws. They are practical starting points for the current repo and hardware setup.
