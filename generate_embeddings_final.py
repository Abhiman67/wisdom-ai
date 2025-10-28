#!/usr/bin/env python3
"""
Generate embeddings for the optimized 38,040 verses
"""

import json
import pickle
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from sqlmodel import Session, create_engine, select, SQLModel, Field
from sentence_transformers import SentenceTransformer
import torch

# Define Verse model locally
class Verse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    verse_id: str = Field(index=True, unique=True)
    text: str
    source: str
    mood_tags: Optional[str] = "[]"
    created_at: datetime = Field(default_factory=datetime.utcnow)

def generate_embeddings():
    """Generate embeddings for all verses"""
    
    print("🔄 Starting embedding generation for 38,040 verses...")
    
    # Setup paths
    embeddings_dir = Path("./embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    embeddings_file = embeddings_dir / "verse_embeddings.pkl"
    metadata_file = embeddings_dir / "verse_metadata.json"
    version_file = embeddings_dir / "version.json"
    
    # Clear existing files
    if embeddings_file.exists():
        embeddings_file.unlink()
    if metadata_file.exists():
        metadata_file.unlink()
    if version_file.exists():
        version_file.unlink()
    
    print("✓ Cleared existing embedding files")
    
    # Load model
    print("🤖 Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    print(f"✓ Model loaded on {device}")
    
    # Connect to database
    engine = create_engine("sqlite:///./god_ai.db")
    
    with Session(engine) as session:
        # Get all verses
        verses = session.exec(select(Verse)).all()
        total_verses = len(verses)
        
        print(f"📖 Found {total_verses} verses in database")
        
        if total_verses == 0:
            print("❌ No verses found in database!")
            return False
        
        # Process verses in batches
        verse_embeddings = {}
        verse_metadata = {}
        
        batch_size = 100
        processed = 0
        
        print("🔄 Computing embeddings...")
        for i, verse in enumerate(verses):
            try:
                # Create searchable text combining verse text, source, and mood tags
                mood_tags = json.loads(verse.mood_tags or "[]")
                searchable_text = f"{verse.text} {verse.source} {' '.join(mood_tags)}"
                
                # Compute embedding
                embedding = model.encode(searchable_text)
                verse_embeddings[verse.verse_id] = embedding
                verse_metadata[verse.verse_id] = {
                    'text': verse.text,
                    'source': verse.source,
                    'mood_tags': mood_tags
                }
                
                processed += 1
                
                # Progress indicator
                if i % batch_size == 0:
                    progress = (i / total_verses) * 100
                    print(f"  Processed {i}/{total_verses} verses ({progress:.1f}%)...")
                    
            except Exception as e:
                print(f"Error processing verse {verse.verse_id}: {e}")
                continue
        
        print(f"✓ Processed {processed}/{total_verses} verses")
        
        # Save embeddings to disk
        print("💾 Saving embeddings to disk...")
        
        with open(embeddings_file, 'wb') as f:
            pickle.dump(verse_embeddings, f)
        
        with open(metadata_file, 'w') as f:
            json.dump(verse_metadata, f, indent=2)
        
        # Calculate file sizes
        embeddings_size = embeddings_file.stat().st_size / (1024 * 1024)  # MB
        metadata_size = metadata_file.stat().st_size / (1024 * 1024)  # MB
        total_size = embeddings_size + metadata_size
        
        # Create version file
        version_data = {
            "version": "1.0",
            "total_verses": len(verse_embeddings),
            "created_at": datetime.utcnow().isoformat(),
            "model": "all-MiniLM-L6-v2",
            "embeddings_size_mb": round(embeddings_size, 2),
            "metadata_size_mb": round(metadata_size, 2),
            "total_size_mb": round(total_size, 2),
            "current_embeddings_in_memory": len(verse_embeddings),
            "current_metadata_in_memory": len(verse_metadata)
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        print(f"✅ Successfully generated embeddings for {len(verse_embeddings)} verses")
        print(f"   Embeddings size: {embeddings_size:.2f} MB")
        print(f"   Metadata size: {metadata_size:.2f} MB")
        print(f"   Total size: {total_size:.2f} MB")
        
        return True

if __name__ == "__main__":
    success = generate_embeddings()
    if success:
        print("\n🎉 Embedding generation completed successfully!")
        print("Your RAG system now has full semantic search capabilities!")
    else:
        print("\n⚠️ Embedding generation completed with warnings")
