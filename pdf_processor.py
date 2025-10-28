"""
PDF Processing System for God AI Backend
Extracts and processes verses from religious texts (Bhagavad Gita, Quran, Bible, Guru Granth Sahib)
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pdfplumber
from sqlmodel import Session, create_engine, select
from main import Verse, engine

# Initialize transformers for mood tagging
try:
    from transformers import pipeline
    mood_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None
    )
    print("✓ Mood classification model loaded")
except Exception as e:
    print(f"Warning: Could not load mood classifier: {e}")
    mood_classifier = None

class ReligiousTextProcessor:
    """Base class for processing different religious texts"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.verses = []
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def parse_verses(self, text: str) -> List[Dict[str, Any]]:
        """Parse verses from text - to be implemented by subclasses"""
        raise NotImplementedError
    
    def tag_moods(self, verse_text: str) -> List[str]:
        """Tag verses with mood categories using AI"""
        if not mood_classifier:
            return ["neutral"]
        
        try:
            # Get mood predictions
            results = mood_classifier(verse_text)
            moods = []
            
            # Map model emotions to our mood categories
            emotion_mapping = {
                'joy': 'happy',
                'sadness': 'sad',
                'anger': 'angry',
                'fear': 'fear',
                'surprise': 'surprise',
                'disgust': 'disgust'
            }
            
            # Handle nested list structure from transformers pipeline
            actual_results = results[0] if isinstance(results[0], list) else results
            
            # Get top emotions with score > 0.3
            for result in actual_results:
                if result['score'] > 0.3:
                    emotion = result['label'].lower()
                    mood = emotion_mapping.get(emotion, 'neutral')
                    if mood not in moods:
                        moods.append(mood)
            
            # Add contextual mood tags based on keywords
            verse_lower = verse_text.lower()
            contextual_moods = []
            
            if any(word in verse_lower for word in ['comfort', 'peace', 'rest', 'calm', 'heal']):
                contextual_moods.append('comfort')
            if any(word in verse_lower for word in ['strength', 'power', 'courage', 'brave']):
                contextual_moods.append('strength')
            if any(word in verse_lower for word in ['hope', 'future', 'promise', 'better']):
                contextual_moods.append('hope')
            if any(word in verse_lower for word in ['love', 'beloved', 'dear', 'heart']):
                contextual_moods.append('love')
            if any(word in verse_lower for word in ['wisdom', 'understand', 'knowledge', 'teach']):
                contextual_moods.append('wisdom')
            if any(word in verse_lower for word in ['forgive', 'mercy', 'pardon', 'grace']):
                contextual_moods.append('forgiveness')
            if any(word in verse_lower for word in ['purpose', 'duty', 'work', 'serve']):
                contextual_moods.append('purpose')
            
            moods.extend(contextual_moods)
            return list(set(moods)) if moods else ["neutral"]
            
        except Exception as e:
            print(f"Error in mood tagging: {e}")
            return ["neutral"]
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process PDF and return structured verses"""
        print(f"Processing {self.source_name} from {pdf_path}...")
        
        # Extract text
        text = self.extract_text(pdf_path)
        if not text:
            return []
        
        # Parse verses
        verses = self.parse_verses(text)
        
        # Add mood tags to each verse
        for verse in verses:
            verse['mood_tags'] = self.tag_moods(verse['text'])
        
        print(f"✓ Extracted {len(verses)} verses from {self.source_name}")
        return verses

class BhagavadGitaProcessor(ReligiousTextProcessor):
    """Processor for Bhagavad Gita"""
    
    def __init__(self):
        super().__init__("Bhagavad Gita")
    
    def parse_verses(self, text: str) -> List[Dict[str, Any]]:
        verses = []
        
        # Pattern for Bhagavad Gita verses (Chapter.Verse format)
        verse_pattern = r'(\d+\.\d+)\s+(.+?)(?=\d+\.\d+|\Z)'
        matches = re.findall(verse_pattern, text, re.DOTALL)
        
        for chapter_verse, verse_text in matches:
            # Clean the verse text
            verse_text = re.sub(r'\s+', ' ', verse_text.strip())
            verse_text = re.sub(r'[^\w\s.,;:!?-]', '', verse_text)
            
            if len(verse_text) > 20:  # Filter out very short fragments
                verses.append({
                    'verse_id': f"Gita_{chapter_verse}",
                    'text': verse_text,
                    'source': self.source_name
                })
        
        return verses

class QuranProcessor(ReligiousTextProcessor):
    """Processor for Quran"""
    
    def __init__(self):
        super().__init__("Quran")
    
    def parse_verses(self, text: str) -> List[Dict[str, Any]]:
        verses = []
        
        # Pattern for Quran verses (Surah:Verse format)
        verse_pattern = r'(\d+:\d+)\s+(.+?)(?=\d+:\d+|\Z)'
        matches = re.findall(verse_pattern, text, re.DOTALL)
        
        for surah_verse, verse_text in matches:
            # Clean the verse text
            verse_text = re.sub(r'\s+', ' ', verse_text.strip())
            verse_text = re.sub(r'[^\w\s.,;:!?-]', '', verse_text)
            
            if len(verse_text) > 20:  # Filter out very short fragments
                verses.append({
                    'verse_id': f"Quran_{surah_verse.replace(':', '_')}",
                    'text': verse_text,
                    'source': self.source_name
                })
        
        return verses

class BibleProcessor(ReligiousTextProcessor):
    """Processor for Bible"""
    
    def __init__(self):
        super().__init__("Bible")
    
    def parse_verses(self, text: str) -> List[Dict[str, Any]]:
        verses = []
        
        # Pattern for Bible verses (Book Chapter:Verse format)
        verse_pattern = r'(\d+)\s+(.+?)(?=\n\s*\d+\s+|\Z)'
        matches = re.findall(verse_pattern, text, re.DOTALL)
        
        # Also try to extract book names and chapters
        book_pattern = r'([A-Z][a-z]+)\s+(\d+):(\d+)\s+(.+?)(?=[A-Z][a-z]+\s+\d+:\d+|\Z)'
        book_matches = re.findall(book_pattern, text, re.DOTALL)
        
        for book, chapter, verse_num, verse_text in book_matches:
            # Clean the verse text
            verse_text = re.sub(r'\s+', ' ', verse_text.strip())
            verse_text = re.sub(r'[^\w\s.,;:!?-]', '', verse_text)
            
            if len(verse_text) > 20:
                verses.append({
                    'verse_id': f"{book}_{chapter}_{verse_num}",
                    'text': verse_text,
                    'source': f"{self.source_name} - {book}"
                })
        
        return verses

class GuruGranthSahibProcessor(ReligiousTextProcessor):
    """Processor for Guru Granth Sahib"""
    
    def __init__(self):
        super().__init__("Guru Granth Sahib")
    
    def parse_verses(self, text: str) -> List[Dict[str, Any]]:
        verses = []
        
        # Pattern for Guru Granth Sahib verses (Ang:Shabad format)
        verse_pattern = r'(\d+)\s+(.+?)(?=\n\s*\d+\s+|\Z)'
        matches = re.findall(verse_pattern, text, re.DOTALL)
        
        for ang_num, verse_text in matches:
            # Clean the verse text
            verse_text = re.sub(r'\s+', ' ', verse_text.strip())
            verse_text = re.sub(r'[^\w\s.,;:!?-]', '', verse_text)
            
            if len(verse_text) > 20:
                verses.append({
                    'verse_id': f"Granth_{ang_num}",
                    'text': verse_text,
                    'source': self.source_name
                })
        
        return verses

def process_all_pdfs() -> Dict[str, List[Dict[str, Any]]]:
    """Process all PDF files and return structured verses"""
    
    pdf_files = {
        "bhagwad_gita.pdf": BhagavadGitaProcessor(),
        "Holy-Quran-English.pdf": QuranProcessor(),
        "CSB_Pew_Bible_2nd_Printing.pdf": BibleProcessor(),
        "Siri Guru Granth - English Translation (matching pages).pdf": GuruGranthSahibProcessor()
    }
    
    all_verses = {}
    
    for pdf_file, processor in pdf_files.items():
        if os.path.exists(pdf_file):
            verses = processor.process_pdf(pdf_file)
            all_verses[pdf_file] = verses
        else:
            print(f"Warning: {pdf_file} not found")
    
    return all_verses

def save_verses_to_database(verses_dict: Dict[str, List[Dict[str, Any]]]):
    """Save processed verses to database"""
    
    with Session(engine) as session:
        total_added = 0
        
        for pdf_file, verses in verses_dict.items():
            print(f"Saving verses from {pdf_file}...")
            
            for verse_data in verses:
                # Check if verse already exists
                existing = session.exec(
                    select(Verse).where(Verse.verse_id == verse_data['verse_id'])
                ).one_or_none()
                
                if not existing:
                    # Create new verse
                    verse = Verse(
                        verse_id=verse_data['verse_id'],
                        text=verse_data['text'],
                        source=verse_data['source'],
                        mood_tags=json.dumps(verse_data.get('mood_tags', ['neutral']))
                    )
                    session.add(verse)
                    total_added += 1
        
        session.commit()
        print(f"✓ Added {total_added} new verses to database")

def main():
    """Main processing function"""
    print("🕉️ Processing Religious Texts for God AI")
    print("=" * 50)
    
    # Process all PDFs
    verses_dict = process_all_pdfs()
    
    # Save to database
    save_verses_to_database(verses_dict)
    
    # Print summary
    total_verses = sum(len(verses) for verses in verses_dict.values())
    print(f"\n✅ Processing Complete!")
    print(f"📚 Total verses processed: {total_verses}")
    
    for pdf_file, verses in verses_dict.items():
        print(f"   {pdf_file}: {len(verses)} verses")

if __name__ == "__main__":
    main()
