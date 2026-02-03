"""Minimal terminal inference for Bhagavad Gita LoRA model.

Usage (PowerShell):
  .\.venv\Scripts\python.exe smoke_infer.py --question "Explain Chapter 2 Verse 47" --sample

Flags:
  --sample          Enable sampling (temperature/top_p); otherwise greedy.
  --persona         Include Gita grounding system prompt.
  --rag             Use cached RAG index if available (will build if missing).
  --rag_k           Number of contexts to retrieve (default 3).
  --rag_max_chars   Max chars per context snippet.
"""
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import os, json

SYSTEM_PERSONA = (
    "You are a Bhagavad Gita assistant. Always ground answers in the Bhagavad Gita's teachings. "
    "Cite chapter and verse when relevant and relate advice to dharma, karma yoga, bhakti, and detachment." )

# RAG support (reuse existing index files if present)
RAG_EMB_PATH = "rag_index.pt"
RAG_META_PATH = "rag_index_meta.json"

def clean_output(text: str) -> str:
    if "### Response:" in text:
        text = text.split("### Response:")[-1].strip()
    for m in ["### Instruction:", "### Input:", "### System:", "### Context:"]:
        if m in text:
            text = text.split(m)[0].strip()
    return text.strip()

def load_model(base_model: str, adapter_dir: str):
    tok = AutoTokenizer.from_pretrained(base_model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb,
        device_map={"":0},
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()
    return tok, model

def retrieve_contexts(query: str, k: int, max_chars: int):
    if not (os.path.exists(RAG_EMB_PATH) and os.path.exists(RAG_META_PATH)):
        return []
    try:
        embs = torch.load(RAG_EMB_PATH, map_location="cpu")
        with open(RAG_META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        texts = meta.get("texts", [])
        if len(texts) != embs.shape[0]:
            return []
        # Load sentence-transformers if available
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        q = embedder.encode([query], convert_to_tensor=True)
        q = torch.nn.functional.normalize(q, p=2, dim=1)
        sims = torch.matmul(embs, q.squeeze(0))
        topk = min(k, sims.shape[0])
        vals, idx = torch.topk(sims, k=topk)
        out = []
        for i in idx.tolist():
            t = texts[i]
            if len(t) > max_chars:
                t = t[:max_chars] + "..."
            out.append(t)
        return out
    except Exception:
        return []

def build_prompt(question: str, contexts, persona: bool):
    parts = []
    if persona:
        parts.append(f"### System:\n{SYSTEM_PERSONA}\n\n")
    if contexts:
        joined = "\n\n---\n\n".join([f"Context {i+1}:\n{c}" for i,c in enumerate(contexts)])
        parts.append(f"### Context:\n{joined}\n\n")
    parts.append(f"### Instruction:\n{question}\n\n### Input:\n\n### Response:\n")
    return "".join(parts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", "-q", default="Explain Chapter 2 Verse 47 in simple words.")
    ap.add_argument("--base_model", default="mistralai/Mistral-7B-Instruct-v0.2")
    ap.add_argument("--adapter_dir", default="./lora_mistral_bhagavad")
    ap.add_argument("--max_new_tokens", type=int, default=300)
    ap.add_argument("--sample", action="store_true", help="Enable sampling (temperature/top_p)")
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--top_p", type=float, default=0.9)
    ap.add_argument("--repetition_penalty", type=float, default=1.1)
    ap.add_argument("--persona", action="store_true", help="Add Gita grounding persona")
    ap.add_argument("--rag", action="store_true", help="Include retrieved context snippets if index present")
    ap.add_argument("--rag_k", type=int, default=3)
    ap.add_argument("--rag_max_chars", type=int, default=800)
    args = ap.parse_args()

    tok, model = load_model(args.base_model, args.adapter_dir)
    contexts = retrieve_contexts(args.question, k=args.rag_k, max_chars=args.rag_max_chars) if args.rag else []
    prompt = build_prompt(args.question, contexts, persona=args.persona)
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    gen_kwargs = dict(
        max_new_tokens=args.max_new_tokens,
        eos_token_id=tok.eos_token_id,
        pad_token_id=tok.pad_token_id,
    )
    if args.sample:
        gen_kwargs.update(dict(do_sample=True, temperature=args.temperature, top_p=args.top_p, repetition_penalty=args.repetition_penalty))
    else:
        gen_kwargs.update(dict(do_sample=False))
    with torch.no_grad():
        out = model.generate(**inputs, **gen_kwargs)
    text = tok.decode(out[0], skip_special_tokens=True)
    print(clean_output(text))

if __name__ == "__main__":
    main()
