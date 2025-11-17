#!/usr/bin/env python3
"""Tiny example to fine-tune GPT-2 on instruction-style JSONL.
This is intentionally small: default epochs=1, small batch, CPU-friendly where possible.
"""
import argparse
import os
import json
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


def make_prompt(example):
    prompt = example["prompt"] + " "
    return prompt + example["completion"]


def main(data, output_dir, model_name="gpt2", epochs=1):
    os.makedirs(output_dir, exist_ok=True)
    ds = load_dataset("json", data_files=data, split="train")

    ds = ds.map(lambda x: {"text": x["prompt"] + " " + x["completion"]})

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})

    def tok(x):
        return tokenizer(x["text"], truncation=True, max_length=256)

    tok_ds = ds.map(tok, batched=True, remove_columns=ds.column_names)

    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.resize_token_embeddings(len(tokenizer))

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        num_train_epochs=int(epochs),
        save_strategy="epoch",
        logging_steps=10,
        fp16=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tok_ds,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Saved model to", output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--model_name", default="gpt2")
    parser.add_argument("--epochs", default=1)
    args = parser.parse_args()
    main(args.data, args.output_dir, args.model_name, args.epochs)
