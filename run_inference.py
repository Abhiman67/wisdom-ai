"""Quick inference script for the LoRA-adapted Mistral model."""
import argparse
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel


def clean_output(text):
    """Remove template artifacts and clean up model output."""
    # Extract only the response section
    if "### Response:" in text:
        text = text.split("### Response:")[-1].strip()
    
    # Stop at any subsequent template markers
    for marker in ["### Instruction:", "### Input:", "### Explanation:", "### 2.", "### Question:"]:
        if marker in text:
            text = text.split(marker)[0].strip()
    
    # Remove trailing incomplete sentences (ending with incomplete words or punctuation)
    text = re.sub(r'\n\n.*$', '', text, flags=re.DOTALL) if text.count('\n\n') > 1 else text
    
    return text.strip()


SYSTEM_PERSONA = (
    "You are a Bhagavad Gita assistant. Always ground answers in the Bhagavad Gita's teachings. "
    "Prefer citing chapter and verse when applicable, and relate advice back to concepts like dharma, "
    "karma yoga, bhakti, and detachment from results."
)


parser = argparse.ArgumentParser(description="Run single-prompt inference against LoRA-adapted model")
parser.add_argument("prompt", help="Instruction or question to feed the model")
parser.add_argument("--context", default="", help="Optional additional input context")
parser.add_argument("--base_model", default="mistralai/Mistral-7B-Instruct-v0.2")
parser.add_argument("--adapter_dir", default="./lora_mistral_bhagavad")
parser.add_argument("--max_new_tokens", type=int, default=300)
parser.add_argument("--temperature", type=float, default=0.7)
parser.add_argument("--top_p", type=float, default=0.9)
parser.add_argument("--repetition_penalty", type=float, default=1.1)
parser.add_argument("--do_sample", action="store_true", help="Enable sampling (otherwise greedy)")
parser.add_argument("--gita_persona", action="store_true", help="Prepend Bhagavad Gita system persona")
parser.add_argument("--raw", action="store_true", help="Show raw output without cleaning")
args = parser.parse_args()

tokenizer = AutoTokenizer.from_pretrained(args.base_model)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Use BitsAndBytesConfig instead of deprecated load_in_4bit
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

# Build prompt with optional system persona
prefix = f"### System:\n{SYSTEM_PERSONA}\n\n" if args.gita_persona else ""
prompt_text = (
    prefix +
    "### Instruction:\n" + args.prompt.strip() +
    "\n\n### Input:\n" + args.context.strip() +
    "\n\n### Response:\n"
)

inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
gen_kwargs = dict(
    **inputs,
    max_new_tokens=args.max_new_tokens,
    do_sample=bool(args.do_sample),
    temperature=args.temperature,
    top_p=args.top_p,
    repetition_penalty=args.repetition_penalty,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
)

with torch.no_grad():
    output = model.generate(**gen_kwargs)

decoded = tokenizer.decode(output[0], skip_special_tokens=True)

if args.raw:
    print(decoded)
else:
    cleaned = clean_output(decoded)
    print(cleaned)
