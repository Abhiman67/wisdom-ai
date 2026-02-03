"""
Systematic evaluation script for the fine-tuned model.
Tests all validation examples and saves results to CSV.
"""
import argparse
import json
import csv
import time
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from tqdm import tqdm


def clean_output(text):
    """Remove template artifacts and clean up model output."""
    import re
    
    # Extract only the response section
    if "### Response:" in text:
        text = text.split("### Response:")[-1].strip()
    
    # Stop at any subsequent template markers
    for marker in ["### Instruction:", "### Input:", "### Explanation:", "### 2.", "### Question:"]:
        if marker in text:
            text = text.split(marker)[0].strip()
    
    # Remove trailing incomplete sentences
    text = re.sub(r'\n\n.*$', '', text, flags=re.DOTALL) if text.count('\n\n') > 1 else text
    
    return text.strip()


def generate_response(model, tokenizer, instruction, input_text="", max_new_tokens=300, temperature=0.7, top_p=0.9, repetition_penalty=1.1):
    """Generate a response for a given instruction."""
    prompt_text = (
        "### System:\nYou are a Bhagavad Gita assistant. Ground answers in the scripture, cite chapter and verse when relevant.\n\n"
        "### Instruction:\n" + instruction.strip() +
        "\n\n### Input:\n" + input_text.strip() +
        "\n\n### Response:\n"
    )
    
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return clean_output(decoded)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val_data", default="Bhagwad_Gita_val.jsonl", help="Validation JSONL file")
    parser.add_argument("--base_model", default="mistralai/Mistral-7B-Instruct-v0.2")
    parser.add_argument("--adapter_dir", default="./lora_mistral_bhagavad")
    parser.add_argument("--output_csv", default="evaluation_results.csv", help="Output CSV file")
    parser.add_argument("--max_new_tokens", type=int, default=300)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--repetition_penalty", type=float, default=1.1)
    parser.add_argument("--limit", type=int, help="Limit number of examples to test")
    args = parser.parse_args()
    
    print("Loading validation data...")
    examples = []
    with open(args.val_data, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    
    if args.limit:
        examples = examples[:args.limit]
    
    print(f"Loaded {len(examples)} validation examples")
    
    print("Loading model and adapter...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map={"": 0},
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(model, args.adapter_dir)
    model.eval()
    
    print("Running inference on validation set...")
    results = []
    total_time = 0
    
    for i, example in enumerate(tqdm(examples, desc="Evaluating")):
        instruction = example.get('instruction', '')
        input_text = example.get('input', '')
        expected_output = example.get('output', '')
        metadata = example.get('metadata', {})
        
        start_time = time.time()
        generated_output = generate_response(
            model, tokenizer, instruction, input_text,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            repetition_penalty=args.repetition_penalty
        )
        inference_time = time.time() - start_time
        total_time += inference_time
        
        results.append({
            'example_id': i + 1,
            'chapter': metadata.get('Chapter', ''),
            'verse': metadata.get('Verse', ''),
            'instruction': instruction,
            'input': input_text,
            'expected_output': expected_output,
            'generated_output': generated_output,
            'inference_time_sec': round(inference_time, 2),
            'output_length': len(generated_output.split())
        })
    
    print(f"\nSaving results to {args.output_csv}...")
    with open(args.output_csv, 'w', encoding='utf-8', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total examples tested: {len(results)}")
    print(f"Total inference time: {total_time:.2f} seconds")
    print(f"Average time per example: {total_time/len(results):.2f} seconds")
    print(f"Average output length: {sum(r['output_length'] for r in results)/len(results):.1f} words")
    print(f"\nResults saved to: {args.output_csv}")
    print(f"Review the CSV to manually assess quality and accuracy.")


if __name__ == "__main__":
    main()
