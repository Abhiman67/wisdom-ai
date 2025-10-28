#!/usr/bin/env python3
"""
CSV Processor for Religious Texts
Processes clean CSV files for Bhagavad Gita, Quran, and Bible
"""

import pandas as pd
import json
from sqlmodel import Session, select, create_engine
from main import Verse
from datetime import datetime
import os

# Create engine with explicit database path
DATABASE_URL = "sqlite:///./god_ai.db"
engine = create_engine(DATABASE_URL, echo=False)

def clear_existing_verses():
    """Clear all existing verses from the database"""
    print("🗑️ Clearing existing verse data...")
    with Session(engine) as session:
        # Delete all existing verses
        verses = session.exec(select(Verse)).all()
        for verse in verses:
            session.delete(verse)
        session.commit()
    print("✅ Cleared existing verse data")

def process_bhagavad_gita(csv_file="Bhagwad_Gita.csv"):
    """Process Bhagavad Gita CSV file"""
    print(f"📖 Processing Bhagavad Gita from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} not found")
        return 0
    
    try:
        df = pd.read_csv(csv_file)
        verses_added = 0
        
        with Session(engine) as session:
            for _, row in df.iterrows():
                # Create verse ID
                verse_id = f"Gita_{row['Chapter']}_{row['Verse']}"
                
                # Use English meaning as the main text
                text = row['EngMeaning']
                if pd.isna(text) or text.strip() == "":
                    continue
                
                # Create verse object
                verse = Verse(
                    verse_id=verse_id,
                    text=text.strip(),
                    source="Bhagavad Gita",
                    mood_tags="[]"  # Will be updated later
                )
                
                session.add(verse)
                verses_added += 1
            
            session.commit()
        print(f"✅ Added {verses_added} verses from Bhagavad Gita")
        return verses_added
        
    except Exception as e:
        print(f"❌ Error processing Bhagavad Gita: {e}")
        return 0

def process_quran(csv_file="The Quran Dataset.csv"):
    """Process Quran CSV file"""
    print(f"📖 Processing Quran from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} not found")
        return 0
    
    try:
        df = pd.read_csv(csv_file)
        verses_added = 0
        
        with Session(engine) as session:
            for _, row in df.iterrows():
                # Create verse ID
                verse_id = f"Quran_{row['surah_no']}_{row['ayah_no_surah']}"
                
                # Use English translation
                text = row['ayah_en']
                if pd.isna(text) or text.strip() == "":
                    continue
                
                # Create verse object
                verse = Verse(
                    verse_id=verse_id,
                    text=text.strip(),
                    source=f"Quran - {row['surah_name_en']}",
                    mood_tags="[]"  # Will be updated later
                )
                
                session.add(verse)
                verses_added += 1
            
            session.commit()
        print(f"✅ Added {verses_added} verses from Quran")
        return verses_added
        
    except Exception as e:
        print(f"❌ Error processing Quran: {e}")
        return 0

def process_bible_version(csv_file, version_name):
    """Process a single Bible version CSV file"""
    print(f"📖 Processing {version_name} from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} not found")
        return 0
    
    try:
        df = pd.read_csv(csv_file)
        verses_added = 0
        
        with Session(engine) as session:
            for _, row in df.iterrows():
                # Create verse ID
                verse_id = f"Bible_{version_name}_{row['b']}_{row['c']}_{row['v']}"
                
                # Use the text column
                text = row['t']
                if pd.isna(text) or text.strip() == "":
                    continue
                
                # Create verse object
                verse = Verse(
                    verse_id=verse_id,
                    text=text.strip(),
                    source=f"Bible - {version_name}",
                    mood_tags="[]"  # Will be updated later
                )
                
                session.add(verse)
                verses_added += 1
            
            session.commit()
        print(f"✅ Added {verses_added} verses from {version_name}")
        return verses_added
        
    except Exception as e:
        print(f"❌ Error processing {version_name}: {e}")
        return 0

def process_all_csv_files():
    """Process all CSV files"""
    print("🚀 Starting CSV processing for religious texts...")
    
    # Clear existing data
    clear_existing_verses()
    
    total_verses = 0
    
    # Process Bhagavad Gita
    total_verses += process_bhagavad_gita()
    
    # Process Quran
    total_verses += process_quran()
    
    # Process Bible versions (only KJV remaining)
    bible_versions = [
        ("t_kjv.csv", "KJV")
    ]
    
    for csv_file, version_name in bible_versions:
        total_verses += process_bible_version(csv_file, version_name)
    
    print(f"\n🎉 Processing complete!")
    print(f"📊 Total verses added: {total_verses}")
    
    return total_verses

if __name__ == "__main__":
    process_all_csv_files()
