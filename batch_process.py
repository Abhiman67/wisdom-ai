"""
Batch Processing Tool for Bhagavad Gita AI Assistant
Process multiple questions from CSV and save answers with timing stats
"""
import argparse
import csv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import re
import time
from tqdm import tqdm
from datetime import datetime

def clean_output(text):
    """Remove template artifacts and clean up model output."""
    if "### Response:" in text:
        text = text.split("### Response:")[-1].strip()
    
    for marker in ["### Instruction:", "### Input:", "### Explanation:", "### 2.", "### Question:"]:
        if marker in text:
            text = text.split(marker)[0].strip()
    
    text = re.sub(r'\n\n.*$', '', text, flags=re.DOTALL) if text.count('\n\n') > 1 else text
    return text.strip()

def load_model(base_model, adapter_dir):
    """Load model and tokenizer"""
    print("Loading model...")
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_4bit=True,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16
    )
    
    model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()
    
    print("✓ Model loaded successfully!")
    return tokenizer, model

def generate_answer(model, tokenizer, question, temperature=0.7, max_tokens=300, repetition_penalty=1.1):
    """Generate answer for a single question"""
    prompt = f"### Instruction:\n{question}\n\n### Input:\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    start_time = time.time()
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=int(max_tokens),
            temperature=float(temperature),
            top_p=0.9,
            repetition_penalty=float(repetition_penalty),
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    inference_time = time.time() - start_time
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    cleaned_response = clean_output(response)
    
    return cleaned_response, inference_time

def process_batch(input_file, output_file, base_model, adapter_dir, temperature, max_tokens, repetition_penalty):
    """Process batch of questions from CSV"""
    
    # Load model
    tokenizer, model = load_model(base_model, adapter_dir)
    
    # Read input CSV
    questions = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Support both "question" and "Question" column names
            question = row.get('question') or row.get('Question') or row.get('QUESTION')
            if question:
                questions.append(question.strip())
    
    if not questions:
        print(f"❌ No questions found in {input_file}")
        print("   Expected CSV with 'question' column header")
        return
    
    print(f"\n📊 Processing {len(questions)} questions...")
    print(f"{'='*60}")
    
    # Process questions with progress bar
    results = []
    total_time = 0
    
    for i, question in enumerate(tqdm(questions, desc="Generating answers"), 1):
        try:
            answer, inference_time = generate_answer(
                model, tokenizer, question, 
                temperature, max_tokens, repetition_penalty
            )
            
            results.append({
                'question_id': i,
                'question': question,
                'answer': answer,
                'inference_time_seconds': round(inference_time, 2),
                'answer_length_chars': len(answer),
                'timestamp': datetime.now().isoformat()
            })
            
            total_time += inference_time
            
        except Exception as e:
            print(f"\n⚠️  Error processing question {i}: {str(e)}")
            results.append({
                'question_id': i,
                'question': question,
                'answer': f"ERROR: {str(e)}",
                'inference_time_seconds': 0,
                'answer_length_chars': 0,
                'timestamp': datetime.now().isoformat()
            })
    
    # Write output CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['question_id', 'question', 'answer', 'inference_time_seconds', 
                     'answer_length_chars', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print(f"✓ Batch processing complete!")
    print(f"{'='*60}")
    print(f"📁 Output saved to: {output_file}")
    print(f"📊 Summary Statistics:")
    print(f"   • Total questions: {len(questions)}")
    print(f"   • Successful: {len([r for r in results if not r['answer'].startswith('ERROR')])}")
    print(f"   • Failed: {len([r for r in results if r['answer'].startswith('ERROR')])}")
    print(f"   • Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"   • Average time per question: {total_time/len(questions):.2f}s")
    print(f"   • Average answer length: {sum(r['answer_length_chars'] for r in results)/len(results):.0f} chars")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Batch process questions from CSV using Bhagavad Gita AI model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_process.py --input questions.csv --output answers.csv
  python batch_process.py -i questions.csv -o answers.csv --temperature 0.5
  
Input CSV format:
  question
  "What is karma yoga?"
  "Explain Chapter 2 Verse 47"
  
Output CSV format:
  question_id,question,answer,inference_time_seconds,answer_length_chars,timestamp
  1,"What is karma yoga?","Karma Yoga is...",2.34,156,2024-01-15T10:30:00
        """
    )
    
    parser.add_argument("-i", "--input", required=True, help="Input CSV file with questions")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file for answers")
    parser.add_argument("--base_model", default="mistralai/Mistral-7B-Instruct-v0.2", 
                       help="Base model name (default: mistralai/Mistral-7B-Instruct-v0.2)")
    parser.add_argument("--adapter_dir", default="./lora_mistral_bhagavad", 
                       help="LoRA adapter directory (default: ./lora_mistral_bhagavad)")
    parser.add_argument("--temperature", type=float, default=0.7, 
                       help="Temperature for generation (default: 0.7)")
    parser.add_argument("--max_tokens", type=int, default=300, 
                       help="Max tokens to generate (default: 300)")
    parser.add_argument("--repetition_penalty", type=float, default=1.1, 
                       help="Repetition penalty (default: 1.1)")
    
    args = parser.parse_args()
    
    # Validate input file
    try:
        with open(args.input, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: Input file '{args.input}' not found")
        return
    
    # Process batch
    process_batch(
        args.input,
        args.output,
        args.base_model,
        args.adapter_dir,
        args.temperature,
        args.max_tokens,
        args.repetition_penalty
    )

if __name__ == "__main__":
    main()
