"""
Script to process religious texts from PDFs and populate the database
Run this after setting up the database to extract verses from all PDF files
"""

import os
import sys
from pathlib import Path

def check_pdfs_exist():
    """Check if all expected PDF files exist"""
    expected_pdfs = [
        "bhagwad_gita.pdf",
        "Holy-Quran-English.pdf", 
        "CSB_Pew_Bible_2nd_Printing.pdf",
        "Siri Guru Granth - English Translation (matching pages).pdf"
    ]
    
    missing_pdfs = []
    for pdf in expected_pdfs:
        if not Path(pdf).exists():
            missing_pdfs.append(pdf)
    
    if missing_pdfs:
        print(f"❌ Missing PDF files: {missing_pdfs}")
        return False
    
    print("✓ All PDF files found")
    return True

def main():
    """Main processing function"""
    print("🕉️ Processing Religious Texts for God AI")
    print("=" * 50)
    
    # Check if PDFs exist
    if not check_pdfs_exist():
        print("Please ensure all PDF files are in the project directory")
        return
    
    try:
        # Import and run the PDF processor
        from pdf_processor import process_all_pdfs, save_verses_to_database
        
        print("Processing PDF files...")
        verses_dict = process_all_pdfs()
        
        print("Saving verses to database...")
        save_verses_to_database(verses_dict)
        
        # Print summary
        total_verses = sum(len(verses) for verses in verses_dict.values())
        print(f"\n✅ Processing Complete!")
        print(f"📚 Total verses processed: {total_verses}")
        
        for pdf_file, verses in verses_dict.items():
            print(f"   📖 {pdf_file}: {len(verses)} verses")
        
        print(f"\n🎉 Your God AI Backend now has {total_verses} authentic verses!")
        print("The RAG system will be updated when you restart the server.")
        
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
