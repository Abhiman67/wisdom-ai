"""
RAG (Retrieval-Augmented Generation) Integration Module
Provides verse recommendation using semantic similarity
"""

import json
import numpy as np
import pickle
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, SQLModel, Field
from typing import Optional
from datetime import datetime

# We'll import Verse dynamically to avoid circular imports

try:
    from sentence_transformers import SentenceTransformer
    import torch
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RAG libraries not available: {e}")
    RAG_AVAILABLE = False
    SentenceTransformer = None
    torch = None

# Initialize sentence transformer model for embeddings
if RAG_AVAILABLE:
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        print(f"✓ RAG model loaded on {device}")
    except Exception as e:
        print(f"Warning: Could not load RAG model: {e}")
        model = None
        device = 'cpu'
else:
    model = None
    device = 'cpu'

class VerseRAG:
    """Verse Retrieval-Augmented Generation system with persistent embedding storage"""
    
    def __init__(self, engine):
        self.engine = engine
        self.verse_embeddings = {}
        self.verse_metadata = {}
        
        # Setup embedding storage
        self.embeddings_dir = Path("./embeddings")
        self.embeddings_dir.mkdir(exist_ok=True)
        self.embeddings_file = self.embeddings_dir / "verse_embeddings.pkl"
        self.metadata_file = self.embeddings_dir / "verse_metadata.json"
        self.version_file = self.embeddings_dir / "version.json"
        
        # Current version (increment when embedding format changes)
        self.current_version = "1.0"
        
        self._load_verses()
    
    def _load_verses(self):
        """Load embeddings from disk or compute if not available"""
        if not model:
            print("Warning: RAG model not available")
            return
        
        # Try to load from disk first
        if self._load_embeddings_from_disk():
            return
        
        # If not available, compute and save
        self._compute_and_save_embeddings()
    
    def _load_embeddings_from_disk(self) -> bool:
        """Load embeddings from disk if available"""
        if not self._embeddings_exist():
            return False
        
        try:
            # Check version compatibility
            if not self._check_version_compatibility():
                print("⚠️ Embedding version mismatch. Will regenerate embeddings.")
                return False
            
            print("📂 Loading embeddings from disk...")
            
            # Load embeddings
            with open(self.embeddings_file, 'rb') as f:
                self.verse_embeddings = pickle.load(f)
            
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                self.verse_metadata = json.load(f)
            
            print(f"✅ Loaded {len(self.verse_embeddings)} embeddings from disk")
            return True
            
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return False
    
    def _embeddings_exist(self) -> bool:
        """Check if embeddings exist on disk"""
        return (self.embeddings_file.exists() and 
                self.metadata_file.exists() and 
                self.version_file.exists())
    
    def _check_version_compatibility(self) -> bool:
        """Check if stored embeddings are compatible with current version"""
        try:
            with open(self.version_file, 'r') as f:
                version_info = json.load(f)
                return version_info.get('version') == self.current_version
        except:
            return False
    
    def _compute_and_save_embeddings(self):
        """Compute embeddings and save to disk"""
        print("🔄 Computing embeddings for the first time...")
        
        # Import Verse dynamically to avoid circular imports
        from main import Verse
        
        with Session(self.engine) as session:
            verses = session.exec(select(Verse)).all()
            
            print(f"Processing {len(verses)} verses...")
            
            for i, verse in enumerate(verses):
                try:
                    # Create searchable text combining verse text, source, and mood tags
                    mood_tags = json.loads(verse.mood_tags or "[]")
                    searchable_text = f"{verse.text} {verse.source} {' '.join(mood_tags)}"
                    
                    # Compute embedding
                    embedding = model.encode(searchable_text)
                    self.verse_embeddings[verse.verse_id] = embedding
                    self.verse_metadata[verse.verse_id] = {
                        'text': verse.text,
                        'source': verse.source,
                        'mood_tags': mood_tags
                    }
                    
                    # Progress indicator for large datasets
                    if i % 100 == 0:
                        print(f"  Processed {i}/{len(verses)} verses...")
                        
                except Exception as e:
                    print(f"Error processing verse {verse.verse_id}: {e}")
                    continue
        
        # Save to disk
        self._save_embeddings_to_disk()
        print(f"✅ Computed and saved {len(self.verse_embeddings)} embeddings")
    
    def _save_embeddings_to_disk(self):
        """Save embeddings to disk"""
        try:
            print("💾 Saving embeddings to disk...")
            
            # Save embeddings as pickle (efficient for numpy arrays)
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.verse_embeddings, f)
            
            # Save metadata as JSON (human readable)
            with open(self.metadata_file, 'w') as f:
                json.dump(self.verse_metadata, f, indent=2)
            
            # Save version info
            version_info = {
                "version": self.current_version,
                "total_verses": len(self.verse_embeddings),
                "created_at": str(np.datetime64('now')),
                "model": "all-MiniLM-L6-v2"
            }
            with open(self.version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
            
            print(f"✅ Saved embeddings to {self.embeddings_dir}")
            
        except Exception as e:
            print(f"❌ Error saving embeddings: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about stored embeddings"""
        if not self._embeddings_exist():
            return {"exists": False}
        
        try:
            with open(self.version_file, 'r') as f:
                version_info = json.load(f)
            
            embeddings_size = self.embeddings_file.stat().st_size / (1024 * 1024)  # MB
            metadata_size = self.metadata_file.stat().st_size / (1024 * 1024)  # MB
            
            return {
                "exists": True,
                "version": version_info.get('version'),
                "total_verses": version_info.get('total_verses'),
                "created_at": version_info.get('created_at'),
                "model": version_info.get('model'),
                "embeddings_size_mb": round(embeddings_size, 2),
                "metadata_size_mb": round(metadata_size, 2),
                "total_size_mb": round(embeddings_size + metadata_size, 2)
            }
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    def clear_embeddings(self):
        """Clear all stored embeddings"""
        try:
            for file_path in [self.embeddings_file, self.metadata_file, self.version_file]:
                if file_path.exists():
                    file_path.unlink()
            print("🗑️ Cleared all stored embeddings")
        except Exception as e:
            print(f"❌ Error clearing embeddings: {e}")
    
    def _compute_similarity(self, query_embedding: np.ndarray, verse_embedding: np.ndarray) -> float:
        """Compute cosine similarity between query and verse embeddings"""
        return np.dot(query_embedding, verse_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(verse_embedding)
        )
    
    def find_relevant_verses(
        self, 
        query: str, 
        mood: Optional[str] = None,
        user_id: Optional[int] = None,
        recent_verses: Optional[set] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most relevant verses for a given query
        
        Args:
            query: User's message or search query
            mood: Detected mood to filter verses
            user_id: User ID for personalization
            recent_verses: Set of recently shown verses to avoid repetition
            top_k: Number of top verses to return
            
        Returns:
            List of relevant verse dictionaries
        """
        if not model or not self.verse_embeddings:
            return self._fallback_recommendation(mood, recent_verses)
        
        # Compute query embedding
        query_embedding = model.encode(query)
        
        # Calculate similarities
        similarities = []
        for verse_id, verse_embedding in self.verse_embeddings.items():
            # Skip recent verses
            if recent_verses and verse_id in recent_verses:
                continue
            
            # Mood filtering (more permissive - only filter if verse has specific mood tags that conflict)
            if mood:
                verse_mood_tags = self.verse_metadata[verse_id]['mood_tags']
                # Only filter out verses if they have explicit mood tags that conflict with the detected mood
                # If verse has no mood tags (empty list), include it for any mood
                if verse_mood_tags:  # Only apply filtering if verse has mood tags
                    # Define mood conflicts - verses with these tags shouldn't be shown for opposite moods
                    mood_conflicts = {
                        'sadness': ['happy', 'joy', 'celebration'],
                        'happy': ['sadness', 'sorrow', 'grief'],
                        'angry': ['peace', 'calm', 'serenity'],
                        'fear': ['courage', 'strength', 'confidence']
                    }
                    
                    conflicting_tags = mood_conflicts.get(mood, [])
                    if any(tag in verse_mood_tags for tag in conflicting_tags):
                        continue
            
            similarity = self._compute_similarity(query_embedding, verse_embedding)
            similarities.append((verse_id, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for verse_id, similarity in similarities[:top_k]:
            metadata = self.verse_metadata[verse_id]
            results.append({
                'verse_id': verse_id,
                'text': metadata['text'],
                'source': metadata['source'],
                'similarity_score': float(similarity),
                'mood_tags': metadata['mood_tags']
            })
        
        return results
    
    def _fallback_recommendation(self, mood: Optional[str], recent_verses: Optional[set]) -> List[Dict[str, Any]]:
        """Fallback recommendation when RAG model is not available"""
        # Import Verse dynamically to avoid circular imports
        from main import Verse
        
        with Session(self.engine) as session:
            stmt = select(Verse)
            verses = session.exec(stmt).all()
            
            # Filter by mood and recent verses
            filtered_verses = []
            for verse in verses:
                if recent_verses and verse.verse_id in recent_verses:
                    continue
                
                if mood:
                    mood_tags = json.loads(verse.mood_tags or "[]")
                    if mood not in mood_tags:
                        continue
                
                # Truncate very long verses to prevent overwhelming responses
                text = verse.text
                if len(text) > 500:
                    # Try to find a good breaking point (end of sentence)
                    truncated = text[:500]
                    last_period = truncated.rfind('.')
                    if last_period > 200:  # If we can find a period in the last 300 chars
                        text = truncated[:last_period + 1] + "..."
                    else:
                        text = truncated + "..."
                
                filtered_verses.append({
                    'verse_id': verse.verse_id,
                    'text': text,
                    'source': verse.source,
                    'similarity_score': 0.5,  # Default score
                    'mood_tags': json.loads(verse.mood_tags or "[]")
                })
            
            return filtered_verses[:5] if filtered_verses else []
    
    def update_verse_embeddings(self, verse_id: str):
        """Update embeddings for a specific verse (useful when adding new verses)"""
        if not model:
            return
        
        # Import Verse dynamically to avoid circular imports
        from main import Verse
            
        with Session(self.engine) as session:
            verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).one_or_none()
            if verse:
                mood_tags = json.loads(verse.mood_tags or "[]")
                searchable_text = f"{verse.text} {verse.source} {' '.join(mood_tags)}"
                
                embedding = model.encode(searchable_text)
                self.verse_embeddings[verse_id] = embedding
                self.verse_metadata[verse_id] = {
                    'text': verse.text,
                    'source': verse.source,
                    'mood_tags': mood_tags
                }
                
                # Save updated embeddings to disk
                self._save_embeddings_to_disk()
    
    def regenerate_embeddings(self):
        """Force regeneration of all embeddings"""
        print("🔄 Regenerating all embeddings...")
        self.clear_embeddings()
        self._compute_and_save_embeddings()

# Global RAG instance (will be initialized in main.py)
rag_instance = None

def initialize_rag(engine):
    """Initialize the global RAG instance"""
    global rag_instance
    rag_instance = VerseRAG(engine)
    return rag_instance

def get_rag_instance():
    """Get the global RAG instance"""
    return rag_instance
