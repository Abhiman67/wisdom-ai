"""
Gradio Web UI for Bhagavad Gita AI Assistant
Supports both Simple Q&A and Chat modes with streaming responses
"""
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from peft import PeftModel
import argparse
import re
from threading import Thread
from datetime import datetime
import json
import os
from typing import List, Tuple
from collections import OrderedDict

# Optional: lightweight retrieval with sentence-transformers (CPU by default)
try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENT_EMBED = True
except Exception:
    SentenceTransformer = None  # type: ignore
    _HAS_SENT_EMBED = False

# Global model variables
model = None
tokenizer = None
conversation_history = []

# RAG globals
_rag_index_embeddings = None  # torch.FloatTensor [N, D]
_rag_index_texts: List[str] = []
_rag_index_meta: List[dict] = []
_rag_embedder = None
_rag_cache_path = "rag_index.pt"
_rag_meta_path = "rag_index_meta.json"
_rag_built = False

# Tiny LRU cache for query embeddings to avoid re-encoding repeated/similar questions
_qemb_cache_max = 32
_qemb_cache: OrderedDict[str, torch.Tensor] = OrderedDict()

# Persona
SYSTEM_PERSONA = (
    "You are a Bhagavad Gita assistant. Always ground answers in the Bhagavad Gita's teachings. "
    "Prefer citing chapter and verse when applicable, and relate advice back to concepts like dharma, "
    "karma yoga, bhakti, and detachment from results."
)

def clean_output(text):
    """Remove template artifacts and clean up model output."""
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

def load_model(base_model="mistralai/Mistral-7B-Instruct-v0.2", adapter_dir="./lora_mistral_bhagavad"):
    """Load model once at startup"""
    print("Loading model... This may take 30-40 seconds...")
    
    from transformers import BitsAndBytesConfig
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False
    )
    
    print("Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map={"": 0},  # Load everything on GPU 0
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()
    
    print("✓ Model loaded successfully!")
    return tokenizer, model


# ============================
# Retrieval (RAG) utilities
# ============================
def _get_default_corpus_path() -> str:
    """Pick train JSONL if available, else full JSONL."""
    candidates = ["Bhagwad_Gita_train.jsonl", "Bhagwad_Gita.jsonl"]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "Bhagwad_Gita.jsonl"


def load_embedder(device: str = "cpu"):
    """Load sentence-transformer model for embeddings (CPU by default)."""
    global _rag_embedder
    if _rag_embedder is not None:
        return _rag_embedder
    if not _HAS_SENT_EMBED:
        raise RuntimeError("sentence-transformers not installed. Install it to enable RAG.")
    # Small, fast model
    _rag_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
    return _rag_embedder


def _prepare_corpus(jsonl_path: str) -> Tuple[List[str], List[dict]]:
    """Read JSONL and build a list of texts and meta objects."""
    texts: List[str] = []
    meta: List[dict] = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                instr = (obj.get("instruction") or "").strip()
                inp = (obj.get("input") or "").strip()
                outp = (obj.get("output") or "").strip()
                md = obj.get("metadata") or {}
                # Compose retrieval text: prefer verse + explanation
                composed = []
                if inp:
                    composed.append(inp)
                if outp:
                    composed.append(outp)
                if not composed and instr:
                    composed.append(instr)
                if not composed:
                    continue
                text = "\n\n".join(composed)
                texts.append(text)
                meta.append(md)
    except FileNotFoundError:
        pass
    return texts, meta


def build_or_load_rag_index(
    corpus_path: str = None,
    cache_path: str = None,
    meta_path: str = None,
    device: str = "cpu",
):
    """Build or load an in-memory cosine index for retrieval.
    Saves/loads torch tensor (embeddings) and JSON meta.
    """
    global _rag_index_embeddings, _rag_index_texts, _rag_index_meta, _rag_built
    if cache_path is None:
        cache_path = _rag_cache_path
    if meta_path is None:
        meta_path = _rag_meta_path
    if corpus_path is None:
        corpus_path = _get_default_corpus_path()

    # Load if present
    if os.path.exists(cache_path) and os.path.exists(meta_path):
        try:
            _rag_index_embeddings = torch.load(cache_path, map_location="cpu")
            with open(meta_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            _rag_index_texts = saved.get("texts", [])
            _rag_index_meta = saved.get("meta", [])
            if isinstance(_rag_index_embeddings, torch.Tensor) and len(_rag_index_texts) == _rag_index_embeddings.shape[0]:
                _rag_built = True
                return
        except Exception:
            pass

    # Build new
    texts, meta = _prepare_corpus(corpus_path)
    if not texts:
        _rag_index_embeddings = None
        _rag_index_texts = []
        _rag_index_meta = []
        _rag_built = False
        return

    embedder = load_embedder(device=device)
    # Encode on CPU by default to avoid GPU contention
    embs = embedder.encode(texts, batch_size=32, show_progress_bar=True, convert_to_tensor=True, device=device)
    # Normalize for cosine similarity via dot product
    embs = torch.nn.functional.normalize(embs, p=2, dim=1)

    _rag_index_embeddings = embs.cpu()
    _rag_index_texts = texts
    _rag_index_meta = meta
    _rag_built = True

    # Save cache
    try:
        torch.save(_rag_index_embeddings, cache_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"texts": _rag_index_texts, "meta": _rag_index_meta}, f)
    except Exception:
        pass


def retrieve_contexts(query: str, k: int = 3, max_chars: int = 800, device: str = "cpu") -> List[str]:
    """Return top-k context strings for a query."""
    if not _rag_built or _rag_index_embeddings is None or len(_rag_index_texts) == 0:
        # Attempt to build lazily
        build_or_load_rag_index(device=device)
    if _rag_index_embeddings is None or len(_rag_index_texts) == 0:
        return []

    embedder = load_embedder(device=device)
    # Tiny LRU cache lookup
    q_key = query.strip().lower()
    cached = _qemb_cache.get(q_key)
    if cached is None:
        q = embedder.encode([query], convert_to_tensor=True, device=device)
        q = torch.nn.functional.normalize(q, p=2, dim=1)
        # Insert into LRU
        _qemb_cache[q_key] = q
        if len(_qemb_cache) > _qemb_cache_max:
            _qemb_cache.popitem(last=False)
    else:
        # Move to end (most recently used)
        _qemb_cache.move_to_end(q_key)
        q = cached
    # Cosine via dot product on normalized embeddings
    scores = torch.matmul(_rag_index_embeddings, q.squeeze(0).cpu())  # [N]
    topk = min(k, scores.shape[0])
    vals, idx = torch.topk(scores, k=topk)

    contexts: List[str] = []
    for i in idx.tolist():
        txt = _rag_index_texts[i]
        # Trim overly long contexts
        if len(txt) > max_chars:
            txt = txt[:max_chars] + "\n..."
        # Optionally include meta details
        md = _rag_index_meta[i] if i < len(_rag_index_meta) else {}
        prefix = ""
        if md:
            chap = md.get("chapter") or md.get("Chapter") or ""
            verse = md.get("verse") or md.get("Verse") or ""
            if chap or verse:
                prefix = f"[Chapter {chap}, Verse {verse}]\n"
        contexts.append(prefix + txt)
    return contexts

def build_prompt(question, input_text="", context_history=None, extra_context: str = "", gita_only: bool = False):
    """Build prompt with explicit structure guiding quoting, explanation and practical application.

    This prompt instructs the generator to:
      1) Quote relevant verse(s) (with chapter.verse if known).
      2) Give a concise, line-by-line explanation of quoted verse(s).
      3) Relate the explanation to the user's question and provide a practical takeaway.
      4) Avoid inventing citations and explicitly indicate when a citation cannot be verified.
    """
    prompt_parts = []
    if gita_only:
        prompt_parts.append(f"### System:\n{SYSTEM_PERSONA}\n\n")

    # Include recent conversation turns for continuity
    if context_history:
        for q, a in context_history[-3:]:
            prompt_parts.append(f"### Previous Question:\n{q}\n\n### Previous Answer:\n{a}\n\n")

    # Retrieved context should be clearly labelled and used as sources only
    if extra_context:
        prompt_parts.append(f"### Retrieved Context (use as sources if relevant):\n{extra_context}\n\n")

    # Strong structured instruction
    prompt_parts.append("### Instruction:\nPlease answer the user's question using the Bhagavad Gita as the primary source. Follow this structure:\n")
    prompt_parts.append("1) If you have relevant verses, quote them exactly and label with chapter.verse.\n")
    prompt_parts.append("2) Provide a concise, line-by-line explanation of each quoted verse (2-5 short sentences each).\n")
    prompt_parts.append("3) Explicitly connect the explanation to the user's question and provide a practical takeaway or action the user can try.\n")
    prompt_parts.append("4) If you cannot verify a verse or citation, say 'I cannot verify that citation' instead of inventing one.\n\n")

    # Current user question and any direct input/context
    prompt_parts.append(f"### User Question:\n{question}\n\n### Input Context:\n{input_text}\n\n### Response:\n")
    return "".join(prompt_parts)

def generate_answer_instant(question, temperature, max_tokens, repetition_penalty, use_context=False, use_rag=False, rag_k=3, rag_max_chars=800, gita_only: bool = True):
    """Generate answer without streaming (instant display)"""
    global conversation_history, model, tokenizer
    
    if model is None:
        return "⚠️ Model not loaded. Please wait for startup to complete."
    
    try:
        # Optional RAG retrieval
        extra_ctx = ""
        if use_rag:
            ctx_list = retrieve_contexts(question, k=int(rag_k), max_chars=int(rag_max_chars), device="cpu")
            if ctx_list:
                extra_ctx = "\n\n---\n\n".join([f"Context {i+1}:\n{c}" for i, c in enumerate(ctx_list)])

        context = conversation_history if use_context else None
        prompt = build_prompt(question, context_history=context, extra_context=extra_ctx, gita_only=gita_only)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
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
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        cleaned_response = clean_output(response)
        if use_context:
            conversation_history.append((question, cleaned_response))
        return cleaned_response
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

def generate_answer_streaming(question, temperature, max_tokens, repetition_penalty, use_context=False, use_rag=False, rag_k=3, rag_max_chars=800, gita_only: bool = True):
    """Generate answer with streaming (word-by-word display)"""
    global conversation_history, model, tokenizer
    
    if model is None:
        yield "⚠️ Model not loaded. Please wait for startup to complete."
        return
    
    try:
        extra_ctx = ""
        if use_rag:
            ctx_list = retrieve_contexts(question, k=int(rag_k), max_chars=int(rag_max_chars), device="cpu")
            if ctx_list:
                extra_ctx = "\n\n---\n\n".join([f"Context {i+1}:\n{c}" for i, c in enumerate(ctx_list)])
        context = conversation_history if use_context else None
        prompt = build_prompt(question, context_history=context, extra_context=extra_ctx, gita_only=gita_only)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True, skip_prompt=True)
        generation_kwargs = dict(
            **inputs,
            max_new_tokens=int(max_tokens),
            temperature=float(temperature),
            top_p=0.9,
            repetition_penalty=float(repetition_penalty),
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
            streamer=streamer,
        )
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        partial_response = ""
        cleaned = ""
        for new_text in streamer:
            partial_response += new_text
            cleaned = clean_output(prompt + partial_response)
            yield cleaned
        if use_context:
            conversation_history.append((question, cleaned))
    except Exception as e:
        yield f"❌ Error generating response: {str(e)}"

def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return None, "Conversation cleared!"

def export_conversation(format_type):
    """Export conversation to file"""
    global conversation_history
    
    if not conversation_history:
        return None, "No conversation to export"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "Text":
        filename = f"conversation_{timestamp}.txt"
        content = f"Bhagavad Gita AI - Conversation Export\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for i, (q, a) in enumerate(conversation_history, 1):
            content += f"Q{i}: {q}\n\nA{i}: {a}\n\n{'='*60}\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    elif format_type == "Markdown":
        filename = f"conversation_{timestamp}.md"
        content = f"# Bhagavad Gita AI - Conversation\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
        for i, (q, a) in enumerate(conversation_history, 1):
            content += f"### Question {i}\n{q}\n\n### Answer {i}\n{a}\n\n---\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    elif format_type == "JSON":
        filename = f"conversation_{timestamp}.json"
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "conversation": [
                {"question": q, "answer": a} for q, a in conversation_history
            ]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return filename, f"✓ Exported to {filename}"

def format_chat_history(history):
    """Format conversation history for chatbot display"""
    return [(q, a) for q, a in history]

# Example questions
EXAMPLES = [
    "What is the main teaching of Bhagavad Gita?",
    "Explain Chapter 2 Verse 47",
    "What is karma yoga?",
    "What does Krishna say about detachment from results?",
    "What is the difference between karma yoga and bhakti yoga?",
    "How should one deal with difficult situations according to the Gita?",
    "What is dharma?",
    "Summarize the essence of the Gita in simple terms"
]

def create_ui(share=False, streaming=True):
    """Create Gradio interface"""
    # Inject custom Google Fonts (Inter for body, Lora for headings) + minimal spiritual feel
    custom_css = """
    /* Google Fonts: Poppins (modern, clean) for body, Lora (serif, spiritual) for headings */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Lora:wght@500;600&display=swap');
    body, .gradio-container { font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    h1, h2, h3, h4, h5, h6, .gr-markdown h1, .gr-markdown h2 { font-family: 'Lora', serif; letter-spacing:0.5px; }
    /* Light mode background */
    .gradio-container { background: radial-gradient(circle at 30% 20%, #faf8f3 0%, #f2efe9 70%); color:#2d281f; }
    .gradio-container ::selection { background:#e2d8b8; }
    .gr-block.gr-panel { border-radius: 10px; backdrop-filter: blur(2px); }
    .gr-button { font-weight:600; }
    .gr-textbox textarea { font-family: 'Poppins', sans-serif; line-height:1.4; }
    .header-emblem { font-family:'Lora', serif; font-size: 1.05rem; opacity:0.80; }
    .spirit-note { font-size:0.82rem; font-style:italic; color:#6b5f37; }
    .gr-markdown a { color:#6b5f37; text-decoration: none; }
    .gr-markdown a:hover { text-decoration: underline; }
        /* Dark mode overrides - use html[data-theme='dark'] to cover main app and settings */
        html[data-theme='dark'] { 
            color-scheme: dark;
            --background-fill-primary: #12110f;
            --background-fill-secondary: #1a1814;
            --block-background-fill: rgba(50,45,38,0.55);
            --body-text-color: #e9e4d8;
        }
        html[data-theme='dark'], html[data-theme='dark'] body {
            background: radial-gradient(circle at 30% 20%, #1e1b16 0%, #12110f 75%) fixed;
            color:#e9e4d8;
            min-height: 100vh;
        }
        html[data-theme='dark'] .gradio-container { background: transparent; color:#e9e4d8; min-height: 100vh; }
        html[data-theme='dark'] .spirit-note { color:#d1c6a4; }
        html[data-theme='dark'] .gr-markdown, html[data-theme='dark'] .prose, html[data-theme='dark'] label, html[data-theme='dark'] .gr-form, html[data-theme='dark'] .gr-accordion, html[data-theme='dark'] .gr-panel, html[data-theme='dark'] .settings { color:#e9e4d8; }
        html[data-theme='dark'] .gr-markdown a { color:#d1c6a4; }
        html[data-theme='dark'] .gr-button { background:#2a251d; border-color:#3a342b; color:#e9e4d8; }
        html[data-theme='dark'] .gr-textbox textarea { background:#2a251d; color:#f3efe6; }
        html[data-theme='dark'] .gr-block.gr-panel { background:var(--block-background-fill); }
    /* Inputs focus */
    .gr-textbox textarea:focus { outline: 2px solid #c4b68a; }
    html[data-theme='dark'] .gr-textbox textarea:focus { outline: 2px solid #e0d2a8; }
    """

    with gr.Blocks(title="Bhagavad Gita AI Assistant", theme=gr.themes.Soft(), css=custom_css) as demo:
        gr.Markdown("# 🕉️ Bhagavad Gita AI Assistant")
        gr.Markdown("<div class='header-emblem'>Wisdom • Duty • Devotion</div>")
        gr.Markdown("Ask questions about Bhagavad Gita teachings, verses, and concepts.<br><span class='spirit-note'>Answers are guided by dharma, karma yoga, bhakti and detachment.</span>")
        
        with gr.Tabs() as tabs:
            # Tab 1: Simple Q&A Mode
            with gr.Tab("Simple Q&A"):
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Your Question",
                            placeholder="What is karma yoga?",
                            lines=3
                        )
                        
                        with gr.Accordion("⚙️ Advanced Settings", open=False):
                            temperature = gr.Slider(
                                minimum=0.1,
                                maximum=1.5,
                                value=0.7,
                                step=0.1,
                                label="Temperature (creativity)",
                                info="Higher = more creative, Lower = more focused"
                            )
                            max_tokens = gr.Slider(
                                minimum=100,
                                maximum=500,
                                value=300,
                                step=50,
                                label="Max Response Length",
                                info="Maximum tokens to generate"
                            )
                            repetition_penalty = gr.Slider(
                                minimum=1.0,
                                maximum=1.5,
                                value=1.1,
                                step=0.1,
                                label="Repetition Penalty",
                                info="Higher = less repetition"
                            )
                            use_streaming = gr.Checkbox(
                                value=streaming,
                                label="Enable Streaming (see response word-by-word)",
                                info="Disable for instant full response"
                            )
                            gita_only = gr.Checkbox(
                                value=True,
                                label="Gita-only persona (cite teachings/verses)",
                                info="Steer answers to Bhagavad Gita concepts and verses"
                            )
                            use_rag = gr.Checkbox(
                                value=False,
                                label="Enable Retrieval (RAG)",
                                info="Augment with top passages from training corpus"
                            )
                            rag_k = gr.Slider(
                                minimum=1,
                                maximum=5,
                                value=3,
                                step=1,
                                label="Top-K Contexts",
                                info="Number of passages to include"
                            )
                            rag_max_chars = gr.Slider(
                                minimum=300,
                                maximum=1500,
                                value=800,
                                step=50,
                                label="Max Context Characters",
                                info="Limit per passage to keep prompt small"
                            )
                        
                        submit_btn = gr.Button("Ask", variant="primary", size="lg")
                        
                        gr.Examples(
                            examples=EXAMPLES,
                            inputs=question_input,
                            label="Example Questions"
                        )
                    
                    with gr.Column(scale=3):
                        answer_output = gr.Textbox(
                            label="Answer",
                            lines=15,
                            show_copy_button=True
                        )
                        inference_time = gr.Textbox(
                            label="Status",
                            value="Ready",
                            interactive=False
                        )
                
                # Connect simple Q&A
                def handle_simple_qa(question, temp, max_tok, rep_pen, stream_enabled, persona_on, rag_on, k, max_chars):
                    if stream_enabled:
                        # Yield chunks so Gradio streams text instead of displaying a generator object
                        for chunk in generate_answer_streaming(
                            question, temp, max_tok, rep_pen,
                            use_context=False, use_rag=rag_on, rag_k=k, rag_max_chars=max_chars, gita_only=persona_on
                        ):
                            yield chunk
                    else:
                        return generate_answer_instant(
                            question, temp, max_tok, rep_pen,
                            use_context=False, use_rag=rag_on, rag_k=k, rag_max_chars=max_chars, gita_only=persona_on
                        )
                
                submit_btn.click(
                    fn=handle_simple_qa,
                    inputs=[question_input, temperature, max_tokens, repetition_penalty, use_streaming, gita_only, use_rag, rag_k, rag_max_chars],
                    outputs=answer_output
                )
            
            # Tab 2: Chat Mode
            with gr.Tab("Chat / Conversation"):
                gr.Markdown("💬 **Chat Mode** - Ask follow-up questions with conversation memory")
                
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=450,
                    show_copy_button=True
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Message",
                        placeholder="Type your question...",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear Conversation")
                    export_format = gr.Dropdown(
                        choices=["Text", "Markdown", "JSON"],
                        value="Markdown",
                        label="Export Format",
                        scale=1
                    )
                    export_btn = gr.Button("📥 Export", scale=1)
                
                with gr.Accordion("⚙️ Chat Settings", open=False):
                    chat_temperature = gr.Slider(0.1, 1.5, value=0.7, step=0.1, label="Temperature")
                    chat_max_tokens = gr.Slider(100, 500, value=300, step=50, label="Max Length")
                    chat_repetition = gr.Slider(1.0, 1.5, value=1.1, step=0.1, label="Repetition Penalty")
                    chat_streaming = gr.Checkbox(value=streaming, label="Enable Streaming")
                    chat_gita_only = gr.Checkbox(value=True, label="Gita-only persona")
                    chat_use_rag = gr.Checkbox(value=False, label="Enable Retrieval (RAG)")
                    chat_rag_k = gr.Slider(1, 5, value=3, step=1, label="Top-K Contexts")
                    chat_rag_max_chars = gr.Slider(300, 1500, value=800, step=50, label="Max Context Characters")
                
                export_status = gr.Textbox(label="Export Status", interactive=False)
                export_file = gr.File(label="Download", visible=True)
                
                # Chat mode handlers
                def handle_chat(message, history, temp, max_tok, rep_pen, stream_enabled, persona_on, rag_on, k, max_chars):
                    if stream_enabled:
                        # Streaming chat
                        partial = ""
                        for chunk in generate_answer_streaming(message, temp, max_tok, rep_pen, use_context=True, use_rag=rag_on, rag_k=k, rag_max_chars=max_chars, gita_only=persona_on):
                            partial = chunk
                            yield history + [[message, partial]]
                    else:
                        # Instant chat
                        response = generate_answer_instant(message, temp, max_tok, rep_pen, use_context=True, use_rag=rag_on, rag_k=k, rag_max_chars=max_chars, gita_only=persona_on)
                        yield history + [[message, response]]
                
                send_btn.click(
                    fn=handle_chat,
                    inputs=[chat_input, chatbot, chat_temperature, chat_max_tokens, chat_repetition, chat_streaming, chat_gita_only, chat_use_rag, chat_rag_k, chat_rag_max_chars],
                    outputs=chatbot
                ).then(
                    fn=lambda: "",
                    outputs=chat_input
                )
                
                chat_input.submit(
                    fn=handle_chat,
                    inputs=[chat_input, chatbot, chat_temperature, chat_max_tokens, chat_repetition, chat_streaming, chat_gita_only, chat_use_rag, chat_rag_k, chat_rag_max_chars],
                    outputs=chatbot
                ).then(
                    fn=lambda: "",
                    outputs=chat_input
                )
                
                clear_btn.click(
                    fn=lambda: ([], "Conversation cleared!"),
                    outputs=[chatbot, export_status]
                )
                
                export_btn.click(
                    fn=export_conversation,
                    inputs=[export_format],
                    outputs=[export_file, export_status]
                )
        
        gr.Markdown("""
        ---
        ### 💡 Tips
        - **Simple Q&A**: Best for one-off questions and quick lookups
        - **Chat Mode**: Use for follow-up questions and deeper exploration
        - **Streaming**: Watch the response appear word-by-word (disable for instant full response)
        - **Temperature**: Lower (0.3-0.5) for focused answers, Higher (0.8-1.2) for creative interpretations
    - **Retrieval (RAG)**: Enable to ground answers in relevant verses and explanations
        """)
    
    return demo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", default="mistralai/Mistral-7B-Instruct-v0.2", help="Base model name")
    parser.add_argument("--adapter_dir", default="./lora_mistral_bhagavad", help="LoRA adapter directory")
    parser.add_argument("--share", action="store_true", help="Create public shareable link")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on")
    parser.add_argument("--no-streaming", action="store_true", help="Disable streaming by default")
    args = parser.parse_args()

    # Allow overrides via environment variables (useful for deployments)
    env_base = os.getenv("BASE_MODEL")
    env_adapter = os.getenv("ADAPTER_ID") or os.getenv("ADAPTER_DIR")
    if env_base:
        args.base_model = env_base
    if env_adapter:
        args.adapter_dir = env_adapter
    
    # Build or load retrieval index early (non-blocking if cached) and warm up embedder
    try:
        device_pref = "cuda" if (torch.cuda.is_available()) else "cpu"
        # Preload embedder so first query doesn't download on-demand
        try:
            load_embedder(device=device_pref)
            # Warmup encode to trigger any lazy initializations
            try:
                _ = _rag_embedder.encode(["warmup"], convert_to_tensor=True, device=device_pref)
            except Exception:
                pass
        except Exception as e:
            print(f"(Optional) RAG embedder not available: {e}")
        build_or_load_rag_index(device=device_pref)
        print(f"✓ RAG ready on {device_pref}")
    except Exception as e:
        print(f"(Optional) RAG init failed: {e}")

    # Load model at startup
    global model, tokenizer
    tokenizer, model = load_model(args.base_model, args.adapter_dir)
    # Print adapter status for verification
    try:
        active = getattr(model, "active_adapters", None) or getattr(model, "active_adapter", None)
        peft_keys = list(getattr(model, "peft_config", {}).keys())
        print("Adapter status -> active_adapters:", active, "| peft_config keys:", peft_keys)
    except Exception:
        pass
    
    # Create and launch UI
    demo = create_ui(share=args.share, streaming=not args.no_streaming)
    
    print(f"\n{'='*60}")
    print(f"🕉️  Bhagavad Gita AI Assistant")
    print(f"{'='*60}")
    print(f"✓ Server starting on http://localhost:{args.port}")
    if args.share:
        print(f"✓ Public link will be generated...")
    print(f"✓ Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=args.port,
        share=args.share,
        show_error=True
    )

if __name__ == "__main__":
    main()
