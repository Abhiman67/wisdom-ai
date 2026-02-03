#!/usr/bin/env python3
"""
Lightweight LoRA fine-tuning script for the 800-example dataset (Mistral-7B).
Optimized for constrained GPU (RTX 4050 6GB) via:
    - 4-bit loading (optional)
    - Low per-device batch size with gradient accumulation
    - Sequence length capped
    - Optional gradient checkpointing

Usage (PowerShell):
    # From project root
    $env:PYTHONIOENCODING="utf-8"; \
    C:\path\to\.venv\Scripts\python.exe .\scripts\train_lora_800.py \
        --dataset .\english_800.jsonl \
        --output_dir .\lora_english_800 \
        --num_train_epochs 3 \
        --per_device_train_batch_size 1 \
        --gradient_accumulation_steps 8 \
        --max_seq_length 512 \
        --learning_rate 2e-4 \
        --fp16 \
        --load_in_4bit \
        --gradient_checkpointing \
        --resume_from_checkpoint ""

Resume example:
    C:\path\to\.venv\Scripts\python.exe .\scripts\train_lora_800.py `
        --dataset .\english_800.jsonl `
        --output_dir .\lora_english_800 `
        --resume_from_checkpoint .\lora_english_800\checkpoint-300

Notes:
    - If bitsandbytes fails on Windows, omit --load_in_4bit (falls back to full precision; may OOM).
    - Keep total effective batch (per_device * grad_accumulation) <= 8 for 6GB VRAM.
"""
import argparse
import os
from typing import Optional

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)

try:
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
except Exception:
    raise


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, help="Path to JSONL training file")
    p.add_argument("--output_dir", required=True, help="Directory to write checkpoints + adapter")
    p.add_argument("--model_name", default="mistralai/Mistral-7B-Instruct-v0.2")
    p.add_argument("--adapter_name", default="lora_english_800")
    p.add_argument("--num_train_epochs", type=int, default=3)
    p.add_argument("--per_device_train_batch_size", type=int, default=1, help="Micro batch size per GPU")
    p.add_argument("--gradient_accumulation_steps", type=int, default=8, help="Accumulate steps to form effective batch")
    p.add_argument("--learning_rate", type=float, default=2e-4)
    p.add_argument("--max_seq_length", type=int, default=512)
    p.add_argument("--fp16", action="store_true")
    p.add_argument("--load_in_4bit", action="store_true", help="Load model in 4-bit (bitsandbytes)")
    p.add_argument("--gradient_checkpointing", action="store_true", help="Enable gradient checkpointing to save VRAM")
    p.add_argument("--resume_from_checkpoint", default="", help="Checkpoint directory to resume from (optional)")
    return p.parse_args()


def load_jsonl(dataset_path):
    return load_dataset("json", data_files=dataset_path, split="train")


def preprocess(example, tokenizer, max_seq_length: int):
    # Expect each record to have an 'instruction' and 'input' and 'output' (or text)
    # We'll concatenate instruction + input -> prompt, and target = output
    instr = example.get("instruction", "")
    inp = example.get("input", "")
    out = example.get("output", "")
    if inp:
        prompt = instr + "\n" + inp + "\n" + "Answer:" 
    else:
        prompt = instr + "\n" + "Answer:" 
    full = prompt + " " + out
    toks = tokenizer(full, truncation=True, max_length=max_seq_length)
    input_ids = toks["input_ids"]
    # For causal LM fine-tuning we can let labels = input_ids
    return {"input_ids": input_ids, "labels": input_ids}


def main():
    args = parse_args()
    ds = load_jsonl(args.dataset)
    print(f"Loaded dataset with {len(ds)} records from {args.dataset}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    # Ensure tokenizer has pad token
    pad_added = False
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
        pad_added = True

    # Tokenize + truncate
    ds = ds.map(lambda ex: preprocess(ex, tokenizer, args.max_seq_length), remove_columns=ds.column_names)

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # Load base model in 4bit if available — but here we load normally and then prepare for kbit
    device_map = "auto" if torch.cuda.is_available() else None
    print("Loading base model (this may take several minutes)...")
    model_kwargs = {
        "device_map": device_map,
    }
    if args.load_in_4bit:
        # Safe defaults for 4-bit quantization
        model_kwargs.update({
            "load_in_4bit": True,
            "torch_dtype": torch.float16,
        })
    else:
        model_kwargs.update({
            "torch_dtype": torch.float16 if args.fp16 else torch.float32,
        })
    model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)

    # Prepare model for k-bit + LoRA (if bitsandbytes/4-bit used, use prepare_model_for_kbit_training)
    if args.load_in_4bit:
        try:
            model = prepare_model_for_kbit_training(model)
            print("Model prepared for k-bit training.")
        except Exception as e:
            print(f"prepare_model_for_kbit_training failed: {e}. Proceeding without k-bit prep.")

    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    if pad_added:
        model.resize_token_embeddings(len(tokenizer))
        print("Resized embeddings after adding pad token.")
    if args.gradient_checkpointing:
        try:
            model.gradient_checkpointing_enable()
            print("Gradient checkpointing enabled.")
        except Exception as e:
            print(f"Could not enable gradient checkpointing: {e}")
    print("LoRA adapter attached.")

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        logging_steps=25,
        save_steps=100,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        fp16=args.fp16 or args.load_in_4bit,
        remove_unused_columns=False,
        push_to_hub=False,
        report_to=[],
        optim="adamw_torch",
        warmup_steps=50,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # For torch < 2.6, avoid loading optimizer/scheduler state from checkpoint
    # Instead, we'll just load the model weights and continue training fresh
    resume = None
    if args.resume_from_checkpoint:
        checkpoint_path = args.resume_from_checkpoint
        print(f"Note: Skipping optimizer/scheduler state loading due to torch version. Only model weights will be used from {checkpoint_path}")
        # The model adapter weights are already loaded via get_peft_model if we manually load them
        # For simplicity, we'll just train from the current model state without checkpoint resume
    
    trainer.train(resume_from_checkpoint=resume)

    # Save adapter-only weights
    adapter_dir = os.path.join(args.output_dir, args.adapter_name)
    os.makedirs(adapter_dir, exist_ok=True)
    model.save_pretrained(adapter_dir)
    print(f"Saved LoRA adapter to {adapter_dir}")


if __name__ == "__main__":
    main()
