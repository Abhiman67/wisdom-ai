import gradio as gr
import chromadb
from sentence_transformers import SentenceTransformer
import os
import google.generativeai as genai
import openai

# --- Configuration ---
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"

# --- Global State ---
rag_client = None
rag_collection = None
embedder = None

def initialize_rag():
    global rag_client, rag_collection, embedder
    try:
        print("Loading Embedding Model...")
        embedder = SentenceTransformer(EMBED_MODEL)
        
        print("Connecting to Vector DB...")
        rag_client = chromadb.PersistentClient(path=CHROMA_PATH)
        rag_collection = rag_client.get_collection("bhagavad_gita")
        print("✅ RAG Initialized")
        return True
    except Exception as e:
        print(f"❌ RAG Init Failed: {e}")
        return False

# --- Core Logic ---
def query_rag(question, n_results=3):
    if not rag_collection or not embedder:
        return []
    
    # Embed
    q_embed = embedder.encode(question).tolist()
    
    # Search
    results = rag_collection.query(
        query_embeddings=[q_embed],
        n_results=n_results
    )
    
    context_docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    return list(zip(context_docs, metadatas))

def generate_answer(question, api_key, provider="Gemini"):
    if not api_key:
        return "⚠️ Please provide an API Key to generate an answer.", []
    
    # 1. Retrieve Context
    context_items = query_rag(question)
    if not context_items:
        return "⚠️ No relevant verses found in the index. (Did you build it?)", []
    
    # Format Context
    context_str = ""
    citations = []
    for doc, meta in context_items:
        ref = f"Chapter {meta['chapter']}, Verse {meta['verse']}"
        context_str += f"[{ref}]\n{doc}\n\n"
        citations.append(ref)
    
    system_prompt = """You are a wise spiritual guide inspired by the Bhagavad Gita. 
Answer the user's question using ONLY the provided context verses. 
If the answer is not in the context, say so gently. 
Quote specific verses (e.g. 2.47) to support your answer.
Keep the tone serene, helpful, and profound."""

    user_prompt = f"Context Verses:\n{context_str}\n\nUser Question: {question}"

    # 2. Call LLM
    try:
        if provider == "Gemini":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(system_prompt + "\n\n" + user_prompt)
            answer = response.text
            
        elif provider == "OpenAI":
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            answer = response.choices[0].message.content
            
        return answer, context_items
        
    except Exception as e:
        return f"❌ Error calling AI Provider: {str(e)}", context_items

# --- UI ---
def ui_wrapper(question, api_key_input, provider_dropdown):
    # Use input key or env var
    key = api_key_input or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    answer, context = generate_answer(question, key, provider_dropdown)
    
    # Format context for display
    context_display = []
    for doc, meta in context:
        context_display.append([f"Ch {meta['chapter']}:{meta['verse']}", doc])
        
    return answer, context_display

# --- Launch ---
print("🚀 Starting Wisdom AI (RAG Edition)...")
if initialize_rag():
    with gr.Blocks(title="Wisdom AI", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🕉️ Wisdom AI \n*Bhagavad Gita Guide (RAG Edition)*")
        
        with gr.Row():
            with gr.Column(scale=1):
                api_key = gr.Textbox(label="API Key (Gemini/OpenAI)", placeholder="sk-...", type="password")
                provider = gr.Dropdown(["Gemini", "OpenAI"], label="Provider", value="Gemini")
                question = gr.Textbox(label="Your Question", placeholder="What is Karma Yoga?", lines=3)
                submit = gr.Button("Ask Krishna", variant="primary")
            
            with gr.Column(scale=2):
                answer_box = gr.Markdown(label="Answer")
                with gr.Accordion("Reference Verses", open=False):
                    context_box = gr.Dataframe(headers=["Reference", "Content"], datatype=["str", "str"], wrap=True)
        
        submit.click(fn=ui_wrapper, inputs=[question, api_key, provider], outputs=[answer_box, context_box])
        
        # Example questions
        gr.Examples(
            ["What is the meaning of life?", "Why should I fight?", "Explain Karma Yoga"],
            inputs=[question]
        )

    app.launch(server_name="0.0.0.0", server_port=7860)
else:
    print("Failed to initialize RAG. Please check logs.")