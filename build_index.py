import json
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
import os
from tqdm import tqdm

def build_index():
    print("🚀 Initializing RAG Indexer...")
    
    # 1. Initialize ChromaDB
    # persistent_client lets us save to disk
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete collection if exists to start fresh
    try:
        client.delete_collection("bhagavad_gita")
        print("🗑️  Deleted existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="bhagavad_gita",
        metadata={"hnsw:space": "cosine"}
    )
    
    # 2. Load Embedding Model
    print("Models loading... (this may take a moment)")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded")

    # 3. Read Data
    data_path = "Bhagwad_Gita.jsonl"
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found!")
        return

    documents = []
    ids = []
    metadatas = []
    
    print(f"📖 Reading {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            meta = item.get('metadata', {})
            
            # Construct content for embedding
            # We want to match against the meaning/translation primarily, and the Sanskrit
            content = f"Chapter {meta.get('chapter')}, Verse {meta.get('verse')}\n"
            content += f"Sanskrit: {item.get('input')}\n"
            content += f"Translation: {item.get('output')}"
            
            documents.append(content)
            ids.append(f"BG_{meta.get('chapter')}_{meta.get('verse')}")
            metadatas.append({
                "chapter": str(meta.get('chapter')),
                "verse": str(meta.get('verse')),
                "type": "verse"
            })

    # 4. Embed and Store
    print(f"🧠 Encoding {len(documents)} verses...")
    
    # Process in batches to show progress
    batch_size = 50
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs = documents[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        batch_metas = metadatas[i : i + batch_size]
        
        # Generate embeddings
        embeddings = model.encode(batch_docs).tolist()
        
        # Add to Chroma
        collection.add(
            documents=batch_docs,
            embeddings=embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
    print(f"✨ Success! Index built at ./chroma_db with {len(documents)} verses.")

if __name__ == "__main__":
    build_index()
