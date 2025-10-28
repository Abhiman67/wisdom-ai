"""
Database initialization script for God AI Backend
Creates initial admin user and seeds verse data
"""

import os
import sys
from datetime import datetime
from sqlmodel import Session, create_engine, select
from main import User, Verse, hash_password

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./god_ai.db")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@godai.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_NAME = os.getenv("ADMIN_NAME", "God AI Admin")

def create_admin_user():
    """Create initial admin user"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Check if admin already exists
        existing_admin = session.exec(
            select(User).where(User.email == ADMIN_EMAIL)
        ).one_or_none()
        
        if existing_admin:
            print(f"Admin user already exists: {ADMIN_EMAIL}")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_admin=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print(f"Admin user created: {ADMIN_EMAIL}")
        return admin_user

def seed_verses():
    """Seed the database with sample verses"""
    engine = create_engine(DATABASE_URL)
    
    sample_verses = [
        {
            "verse_id": "Gita_2.47",
            "text": "You have a right to perform your prescribed duties, but not to the fruits of your actions. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
            "source": "Bhagavad Gita",
            "mood_tags": "[\"neutral\", \"purpose\", \"duty\"]"
        },
        {
            "verse_id": "Psalm_23.1",
            "text": "The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
            "source": "Bible - Psalms",
            "mood_tags": "[\"comfort\", \"peace\", \"sad\"]"
        },
        {
            "verse_id": "Quran_94.5",
            "text": "So, surely with hardship comes ease. Surely with hardship comes ease.",
            "source": "Quran",
            "mood_tags": "[\"hope\", \"difficulty\", \"sad\"]"
        },
        {
            "verse_id": "Matthew_11.28",
            "text": "Come unto me, all ye that labour and are heavy laden, and I will give you rest.",
            "source": "Bible - Matthew",
            "mood_tags": "[\"comfort\", \"rest\", \"tired\"]"
        },
        {
            "verse_id": "Gita_4.8",
            "text": "To protect the righteous, to annihilate the miscreants, and to reestablish the principles of dharma, I advent Myself millennium after millennium.",
            "source": "Bhagavad Gita",
            "mood_tags": "[\"hope\", \"justice\", \"purpose\"]"
        },
        {
            "verse_id": "Psalm_46.1",
            "text": "God is our refuge and strength, a very present help in trouble.",
            "source": "Bible - Psalms",
            "mood_tags": "[\"strength\", \"comfort\", \"fear\"]"
        },
        {
            "verse_id": "Quran_13.28",
            "text": "Those who believe, and whose hearts find satisfaction in the remembrance of Allah: for without doubt in the remembrance of Allah do hearts find satisfaction.",
            "source": "Quran",
            "mood_tags": "[\"peace\", \"remembrance\", \"faith\"]"
        },
        {
            "verse_id": "Proverbs_3.5",
            "text": "Trust in the Lord with all thine heart; and lean not unto thine own understanding.",
            "source": "Bible - Proverbs",
            "mood_tags": "[\"trust\", \"wisdom\", \"guidance\"]"
        },
        {
            "verse_id": "Romans_8.28",
            "text": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
            "source": "Bible - Romans",
            "mood_tags": "[\"hope\", \"purpose\", \"faith\"]"
        },
        {
            "verse_id": "Gita_6.5",
            "text": "One must deliver himself with the help of his mind, and not degrade himself. The mind is the friend of the conditioned soul, and his enemy as well.",
            "source": "Bhagavad Gita",
            "mood_tags": "[\"mind\", \"self-control\", \"wisdom\"]"
        },
        {
            "verse_id": "Philippians_4.13",
            "text": "I can do all things through Christ which strengtheneth me.",
            "source": "Bible - Philippians",
            "mood_tags": "[\"strength\", \"courage\", \"faith\"]"
        },
        {
            "verse_id": "Quran_2.286",
            "text": "Allah does not burden a soul beyond that it can bear.",
            "source": "Quran",
            "mood_tags": "[\"comfort\", \"strength\", \"difficulty\"]"
        },
        {
            "verse_id": "John_14.27",
            "text": "Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.",
            "source": "Bible - John",
            "mood_tags": "[\"peace\", \"comfort\", \"fear\"]"
        },
        {
            "verse_id": "Gita_9.22",
            "text": "To those who are constantly devoted to serving Me with love, I give the understanding by which they can come to Me.",
            "source": "Bhagavad Gita",
            "mood_tags": "[\"love\", \"devotion\", \"guidance\"]"
        },
        {
            "verse_id": "Isaiah_41.10",
            "text": "Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee; yea, I will help thee; yea, I will uphold thee with the right hand of my righteousness.",
            "source": "Bible - Isaiah",
            "mood_tags": "[\"strength\", \"comfort\", \"fear\"]"
        }
    ]
    
    with Session(engine) as session:
        added_count = 0
        for verse_data in sample_verses:
            existing = session.exec(
                select(Verse).where(Verse.verse_id == verse_data["verse_id"])
            ).one_or_none()
            
            if not existing:
                verse = Verse(**verse_data)
                session.add(verse)
                added_count += 1
        
        session.commit()
        print(f"Added {added_count} verses to the database")

def process_pdfs_if_available():
    """Process PDF files if they exist"""
    pdf_files = [
        "bhagwad_gita.pdf",
        "Holy-Quran-English.pdf", 
        "CSB_Pew_Bible_2nd_Printing.pdf",
        "Siri Guru Granth - English Translation (matching pages).pdf"
    ]
    
    # Check if any PDFs exist
    existing_pdfs = [pdf for pdf in pdf_files if os.path.exists(pdf)]
    
    if existing_pdfs:
        print(f"\nFound {len(existing_pdfs)} PDF files. Processing religious texts...")
        try:
            from pdf_processor import process_all_pdfs, save_verses_to_database
            
            # Process PDFs
            verses_dict = process_all_pdfs()
            
            # Save to database
            save_verses_to_database(verses_dict)
            
            total_verses = sum(len(verses) for verses in verses_dict.values())
            print(f"✅ Processed {total_verses} verses from religious texts!")
            
        except Exception as e:
            print(f"Warning: Could not process PDFs: {e}")
            print("You can process them later using: python process_religious_texts.py")
    else:
        print("\nNo PDF files found. Using sample verses only.")
        print("Add PDF files and run 'python process_religious_texts.py' to extract more verses.")

def main():
    """Main initialization function"""
    print("Initializing God AI Database...")
    
    try:
        # Create admin user
        admin_user = create_admin_user()
        
        # Seed sample verses
        seed_verses()
        
        # Process PDFs if available
        process_pdfs_if_available()
        
        print("\nDatabase initialization completed successfully!")
        print(f"Admin login: {ADMIN_EMAIL}")
        print(f"Admin password: {ADMIN_PASSWORD}")
        print("\nYou can now start the application with:")
        print("uvicorn main:app --reload --port 8000")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
