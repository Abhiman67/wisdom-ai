"""Utility to inspect token lengths and optionally create train/validation splits."""
import argparse
import json
import statistics
import random
from pathlib import Path

from transformers import AutoTokenizer

PROMPT_TEMPLATE = """### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"""


def load_examples(jsonl_path: Path):
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path, help="Path to JSONL dataset")
    parser.add_argument("--model", default="meta-llama/Llama-2-7b-chat-hf", help="Tokenizer name to use")
    parser.add_argument("--max_seq_length", type=int, default=512, help="Reference max length for overflow count")
    parser.add_argument("--train_out", type=Path, help="Optional path to write training split JSONL")
    parser.add_argument("--val_out", type=Path, help="Optional path to write validation split JSONL")
    parser.add_argument("--train_ratio", type=float, default=0.9, help="Train ratio when writing splits")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffling")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    examples = list(load_examples(args.jsonl))
    print(f"Loaded {len(examples)} examples from {args.jsonl}")

    lengths = []
    overflow_count = 0
    for ex in examples:
        text = PROMPT_TEMPLATE.format(
            instruction=ex.get("instruction", ""),
            input=ex.get("input", ""),
            output=ex.get("output", "")
        )
        tokenized = tokenizer(text, truncation=False)
        seq_len = len(tokenized["input_ids"])
        lengths.append(seq_len)
        if seq_len > args.max_seq_length:
            overflow_count += 1

    print("Token length stats (prompt + response combined):")
    print(f"  min: {min(lengths)}")
    print(f"  max: {max(lengths)}")
    print(f"  mean: {statistics.mean(lengths):.2f}")
    print(f"  median: {statistics.median(lengths):.2f}")
    print(f"  95th percentile: {statistics.quantiles(lengths, n=100)[94]:.2f}")
    print(f"  > {args.max_seq_length} tokens: {overflow_count} ({overflow_count/len(lengths)*100:.2f}% of dataset)")

    if args.train_out and args.val_out:
        rng = random.Random(args.seed)
        shuffled = examples[:]
        rng.shuffle(shuffled)
        split_idx = int(len(shuffled) * args.train_ratio)
        train_split = shuffled[:split_idx]
        val_split = shuffled[split_idx:]

        def write_jsonl(path: Path, records):
            with path.open("w", encoding="utf-8") as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        write_jsonl(args.train_out, train_split)
        write_jsonl(args.val_out, val_split)
        print(f"Wrote {len(train_split)} train examples to {args.train_out}")
        print(f"Wrote {len(val_split)} validation examples to {args.val_out}")


if __name__ == "__main__":
    main()
