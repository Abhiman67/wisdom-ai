"""
God AI - FastAPI Backend
A comprehensive spiritual AI companion backend with mood detection, 
verse recommendations, and multimedia content generation.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import os
import hashlib
import jwt
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# ML imports
try:
    from transformers import pipeline
    import torch
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML libraries not available: {e}")
    ML_AVAILABLE = False
    pipeline = None
    torch = None

# Image generation
from PIL import Image, ImageDraw, ImageFont
import textwrap

# TTS imports
import pyttsx3
import io
import base64

# RAG integration
from rag_integration import initialize_rag, get_rag_instance

# LLM integration
from llm_service import initialize_llm, get_llm_service

# ----------------------
# CONFIG / ENV
# ----------------------

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_key_please")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./god_ai.db")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "./media")

# Create media directories
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(f"{MEDIA_ROOT}/audio", exist_ok=True)
os.makedirs(f"{MEDIA_ROOT}/images", exist_ok=True)

# ----------------------
# DB MODELS
# ----------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=False)
    last_mood: Optional[str] = None
    recent_verses: Optional[str] = Field(default="{}")  # JSON object with mood -> verse_ids
    saved_verses: Optional[str] = Field(default="[]")  # JSON list of verse_ids
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSummary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    mood: Optional[str] = None
    summary: str
    verse_id: Optional[str] = None

class UsageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    mood: Optional[str] = None
    endpoint: Optional[str] = None

class Verse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    verse_id: str = Field(index=True, unique=True)  # e.g., "Gita_2.47"
    text: str
    source: str  # e.g., "Bhagavad Gita"
    mood_tags: Optional[str] = "[]"  # JSON list, e.g., ["sad","hopeful"]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ----------------------
# DB INITIALIZATION
# ----------------------

engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# ----------------------
# UTILITIES
# ----------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------------
# ML PIPELINES
# ----------------------

# Initialize ML pipelines
if ML_AVAILABLE:
    try:
        mood_pipeline = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None
        )
        summary_pipeline = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn"
        )
    except Exception as e:
        print(f"Warning: Could not load ML models: {e}")
        mood_pipeline = None
        summary_pipeline = None
else:
    mood_pipeline = None
    summary_pipeline = None

# ----------------------
# TTS SERVICE
# ----------------------

def generate_tts(verse_text: str, verse_id: str) -> str:
    """Generate TTS audio file for the verse text"""
    try:
        # Use pyttsx3 for local TTS
        engine = pyttsx3.init()
        
        # Configure voice properties
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # Use first available voice
        
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Generate audio file
        audio_filename = f"{verse_id.replace(' ', '_').replace('.', '_')}.mp3"
        audio_path = os.path.join(MEDIA_ROOT, "audio", audio_filename)
        
        engine.save_to_file(verse_text, audio_path)
        engine.runAndWait()
        
        return f"/media/audio/{audio_filename}"
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return None

# ----------------------
# IMAGE GENERATION
# ----------------------

def generate_verse_image(verse_text: str, verse_id: str) -> str:
    """Create an attractive image with the verse text"""
    try:
        # Image dimensions
        width, height = 1200, 630
        
        # Create gradient background
        img = Image.new("RGB", (width, height), color=(250, 245, 240))
        draw = ImageDraw.Draw(img)
        
        # Create gradient effect
        for y in range(height):
            color_value = int(250 - (y / height) * 30)
            draw.line([(0, y), (width, y)], fill=(color_value, color_value-5, color_value-10))
        
        # Try to load a nice font
        try:
            # Try system fonts
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_medium = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            try:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_large = font_medium = font_small = None
        
        # Wrap text to fit within margins
        margin = 80
        max_width = width - (margin * 2)
        
        # Split verse into lines
        words = verse_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font_large:
                bbox = draw.textbbox((0, 0), test_line, font=font_large)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(test_line) * 10  # Rough estimate
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        # Draw verse text
        line_height = 45
        start_y = height // 2 - (len(lines) * line_height) // 2
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            
            if font_large:
                bbox = draw.textbbox((0, 0), line, font=font_large)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 10
            
            x_pos = (width - text_width) // 2
            
            draw.text((x_pos, y_pos), line, font=font_large, fill=(40, 40, 40))
        
        # Add decorative border
        draw.rectangle([(margin-10, margin-10), (width-margin+10, height-margin+10)], 
                      outline=(200, 180, 160), width=3)
        
        # Add footer
        footer_text = "God AI 🌸"
        if font_small:
            bbox = draw.textbbox((0, 0), footer_text, font=font_small)
            footer_width = bbox[2] - bbox[0]
        else:
            footer_width = len(footer_text) * 8
        
        draw.text((width - footer_width - margin, height - 40), footer_text, 
                 font=font_small, fill=(120, 120, 120))
        
        # Save image
        image_filename = f"{verse_id.replace(' ', '_').replace('.', '_')}.png"
        image_path = os.path.join(MEDIA_ROOT, "images", image_filename)
        img.save(image_path, "PNG")
        
        return f"/media/images/{image_filename}"
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None

# ----------------------
# RAG INTEGRATION
# ----------------------

def get_relevant_verse(user_message: str, mood: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get relevant verse based on user message, mood, and avoid recent verses using RAG
    """
    # Get RAG instance
    rag = get_rag_instance()
    
    # Get user's recent verses to avoid repetition
    recent_verses = set()
    if user_id:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if user and user.recent_verses:
                recent_data = json.loads(user.recent_verses)
                for mood_key, verses in recent_data.items():
                    recent_verses.update(verses)
    
    if rag:
        # Use RAG for intelligent verse selection
        relevant_verses = rag.find_relevant_verses(
            query=user_message,
            mood=mood,
            user_id=user_id,
            recent_verses=recent_verses,
            top_k=1
        )
        
        if relevant_verses:
            verse = relevant_verses[0]
            # Truncate very long verses to prevent overwhelming responses
            text = verse["text"]
            if len(text) > 500:
                # Try to find a good breaking point (end of sentence)
                truncated = text[:500]
                last_period = truncated.rfind('.')
                if last_period > 200:  # If we can find a period in the last 300 chars
                    text = truncated[:last_period + 1] + "..."
                else:
                    text = truncated + "..."
            
            return {
                "verse_id": verse["verse_id"],
                "text": text,
                "source": verse["source"]
            }
    
    # Fallback: simple database query
    with Session(engine) as session:
        stmt = select(Verse)
        verses = session.exec(stmt).all()
        
        # Filter by mood and avoid recent verses
        for verse in verses:
            if verse.verse_id in recent_verses:
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
            
            return {
                "verse_id": verse.verse_id,
                "text": text,
                "source": verse.source
            }
        
        # Ultimate fallback
        if verses:
            verse = verses[0]
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
            
            return {
                "verse_id": verse.verse_id,
                "text": text,
                "source": verse.source
            }
        
        # Default verse if no verses in database
        return {
            "verse_id": "default_1",
            "text": "May you find peace and wisdom in your journey.",
            "source": "God AI"
        }

def generate_response(user_message: str, verse: Dict[str, Any], mood: str, user_summary: Optional[str] = None) -> str:
    """
    Generate AI response combining verse and context using LLM or enhanced template
    """
    llm = get_llm_service()
    if llm:
        return llm.generate_response(user_message, verse, mood, user_summary)
    # Fallback to template if LLM is not available
    mood_responses = {
        "sadness": "I understand you're going through a difficult time. Let this verse bring you comfort and hope:",
        "happy": "I'm glad you're feeling joyful! Here's a verse to celebrate this moment:",
        "anger": "I sense you're feeling frustrated. This wisdom might help bring clarity and peace:",
        "fear": "I hear the worry in your words. Let this verse offer you strength and courage:",
        "surprise": "I can feel the surprise in your message. Here's some guidance for this moment:",
        "disgust": "I understand your concern. This verse might offer a different perspective:"
    }
    mood_intro = mood_responses.get(mood, "Here's a verse that might speak to your heart:")
    verse_explanations = {
        "sadness": "This verse reminds us that even in our darkest moments, there is comfort and strength available to us. It speaks to the healing power of faith and the promise that we are not alone in our struggles.",
        "happy": "This verse celebrates the joy and blessings in our lives. It reminds us to be grateful for the good moments and to share our happiness with others.",
        "anger": "This verse offers wisdom about managing difficult emotions. It reminds us that patience and understanding can help us navigate challenging situations with grace.",
        "fear": "This verse speaks to courage and trust. It reminds us that we have inner strength and that we can face our fears with faith and determination.",
        "surprise": "This verse offers guidance for unexpected moments. It reminds us that life's surprises can be opportunities for growth and learning.",
        "disgust": "This verse provides perspective on difficult situations. It reminds us that there are always different ways to view challenges and find meaning in them."
    }
    explanation = verse_explanations.get(mood, "This verse offers wisdom and guidance for your current situation. It reminds us that there is always hope and meaning to be found.")
    response = f"{mood_intro}\n\n\"{verse['text']}\"\n— {verse['source']}\n\n{explanation}\n\nHow does this verse speak to your heart today?"
    return response

# ----------------------
# FASTAPI APP
# ----------------------

app = FastAPI(
    title="God AI Backend",
    description="A spiritual AI companion with mood detection and verse recommendations",
    version="1.0.0"
)

# Initialize RAG system on startup
@app.on_event("startup")
def startup_event():
    """Initialize RAG system and other startup tasks"""
    print("Initializing God AI Backend...")
    try:
        initialize_rag(engine)
        print("✓ RAG system initialized")
    except Exception as e:
        print(f"Warning: RAG initialization failed: {e}")
    
    try:
        initialize_llm()
        print("✓ LLM service initialized")
    except Exception as e:
        print(f"Warning: LLM initialization failed: {e}")
    
    print("✓ Backend ready!")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# PYDANTIC MODELS
# ----------------------

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    detected_mood: str
    verse_id: str
    verse_text: str
    verse_source: str

class SaveVerseRequest(BaseModel):
    verse_id: str

class DailyVerseResponse(BaseModel):
    verse_id: str
    text: str
    source: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    last_mood: Optional[str]
    recent_verses: Dict[str, List[str]]
    saved_verses: List[str]
    chat_history: List[Dict[str, Any]]

# ----------------------
# AUTHENTICATION
# ----------------------

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user_uuid = payload.get("sub")
    
    with Session(engine) as session:
        stmt = select(User).where(User.uuid == user_uuid)
        user = session.exec(stmt).one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

# ----------------------
# AUTH ROUTES
# ----------------------

@app.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest):
    with Session(engine) as session:
        # Check if email already exists
        existing_user = session.exec(select(User).where(User.email == request.email)).one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(request.password)
        user = User(
            name=request.name,
            email=request.email,
            hashed_password=hashed_password
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create token
        token = create_access_token({"sub": user.uuid})
        
        return TokenResponse(
            access_token=token,
            user_id=user.uuid,
            name=user.name
        )

@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == request.email)).one_or_none()
        
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        token = create_access_token({"sub": user.uuid})
        
        return TokenResponse(
            access_token=token,
            user_id=user.uuid,
            name=user.name
        )

# ----------------------
# CHAT ROUTE
# ----------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    message = request.message
    
    # 1. Mood detection
    mood = "neutral"
    if mood_pipeline:
        try:
            mood_results = mood_pipeline(message)
            # Handle nested list structure from transformers pipeline
            if isinstance(mood_results, list) and len(mood_results) > 0:
                # Extract the actual results from the nested structure
                actual_results = mood_results[0] if isinstance(mood_results[0], list) else mood_results
                if len(actual_results) > 0:
                    top_result = max(actual_results, key=lambda x: x['score'])
                    mood = top_result['label'].lower()
        except Exception as e:
            print(f"Mood detection failed: {e}")
    
    # 2. Store mood and usage log
    with Session(engine) as session:
        db_user = session.get(User, user.id)
        db_user.last_mood = mood
        db_user.updated_at = datetime.utcnow()
        
        session.add(UsageLog(user_id=user.id, mood=mood, endpoint="chat"))
        session.commit()
    
    # 3. Summarization
    summary = message[:200]  # Fallback
    if summary_pipeline:
        try:
            summary_result = summary_pipeline(message, max_length=60, min_length=10)
            if isinstance(summary_result, list) and len(summary_result) > 0:
                summary = summary_result[0]['summary_text']
        except Exception as e:
            print(f"Summarization failed: {e}")
    
    # 4. Get relevant verse
    verse = get_relevant_verse(message, mood=mood, user_id=user.id)
    
    # 5. Generate response
    reply = generate_response(message, verse, mood, summary)
    
    # 6. Store chat summary and update recent verses
    with Session(engine) as session:
        # Add chat summary
        session.add(ChatSummary(
            user_id=user.id,
            mood=mood,
            summary=summary,
            verse_id=verse['verse_id']
        ))
        
        # Update recent verses
        db_user = session.get(User, user.id)
        recent_verses = json.loads(db_user.recent_verses or "{}")
        
        if mood not in recent_verses:
            recent_verses[mood] = []
        
        # Keep only last 3 verses per mood
        recent_verses[mood].append(verse['verse_id'])
        if len(recent_verses[mood]) > 3:
            recent_verses[mood] = recent_verses[mood][-3:]
        
        db_user.recent_verses = json.dumps(recent_verses)
        session.commit()
    
    return ChatResponse(
        reply=reply,
        detected_mood=mood,
        verse_id=verse['verse_id'],
        verse_text=verse['text'],
        verse_source=verse['source']
    )

# ----------------------
# DAILY VERSE ROUTE
# ----------------------

@app.get("/daily-verse", response_model=DailyVerseResponse)
def daily_verse(user: User = Depends(get_current_user)):
    """Get today's personalized daily verse with audio and image"""
    # Get verse based on user's last mood
    mood = user.last_mood or "neutral"
    verse = get_relevant_verse("daily verse", mood=mood, user_id=user.id)
    
    # Generate audio and image if they don't exist
    audio_filename = f"{verse['verse_id'].replace(' ', '_').replace('.', '_')}.mp3"
    image_filename = f"{verse['verse_id'].replace(' ', '_').replace('.', '_')}.png"
    
    audio_path = os.path.join(MEDIA_ROOT, "audio", audio_filename)
    image_path = os.path.join(MEDIA_ROOT, "images", image_filename)
    
    # Only generate if files don't exist (for performance)
    audio_url = None
    image_url = None
    
    if not os.path.exists(audio_path):
        audio_url = generate_tts(verse['text'], verse['verse_id'])
    else:
        audio_url = f"/media/audio/{audio_filename}"
    
    if not os.path.exists(image_path):
        image_url = generate_verse_image(verse['text'], verse['verse_id'])
    else:
        image_url = f"/media/images/{image_filename}"
    
    # Log daily verse access
    with Session(engine) as session:
        session.add(UsageLog(user_id=user.id, mood=mood, endpoint="daily-verse"))
        session.commit()
    
    return DailyVerseResponse(
        verse_id=verse['verse_id'],
        text=verse['text'],
        source=verse['source'],
        audio_url=audio_url,
        image_url=image_url
    )

# ----------------------
# SAVE VERSE ROUTES
# ----------------------

@app.post("/save-verse")
def save_verse(request: SaveVerseRequest, user: User = Depends(get_current_user)):
    """Save a verse to user's favorites"""
    with Session(engine) as session:
        db_user = session.get(User, user.id)
        saved_verses = json.loads(db_user.saved_verses or "[]")
        
        if request.verse_id not in saved_verses:
            saved_verses.append(request.verse_id)
            db_user.saved_verses = json.dumps(saved_verses)
            session.commit()
            
            return {"success": True, "message": "Verse saved successfully"}
        else:
            return {"success": False, "message": "Verse already saved"}

@app.post("/save-verse-from-daily")
def save_verse_from_daily(user: User = Depends(get_current_user)):
    """Automatically save the current daily verse to user's favorites"""
    # Get the current daily verse
    mood = user.last_mood or "neutral"
    verse = get_relevant_verse("daily verse", mood=mood, user_id=user.id)
    
    with Session(engine) as session:
        db_user = session.get(User, user.id)
        saved_verses = json.loads(db_user.saved_verses or "[]")
        
        if verse['verse_id'] not in saved_verses:
            saved_verses.append(verse['verse_id'])
            db_user.saved_verses = json.dumps(saved_verses)
            session.commit()
            
            return {
                "success": True, 
                "message": "Daily verse saved successfully",
                "verse_id": verse['verse_id'],
                "verse_text": verse['text'],
                "source": verse['source']
            }
        else:
            return {
                "success": False, 
                "message": "Daily verse already saved",
                "verse_id": verse['verse_id']
            }

@app.get("/daily-verse-with-save")
def daily_verse_with_save(user: User = Depends(get_current_user)):
    """Get daily verse with save status (no automatic saving)"""
    # Get the daily verse
    mood = user.last_mood or "neutral"
    verse = get_relevant_verse("daily verse", mood=mood, user_id=user.id)
    
    # Generate audio and image if they don't exist
    audio_filename = f"{verse['verse_id'].replace(' ', '_').replace('.', '_')}.mp3"
    image_filename = f"{verse['verse_id'].replace(' ', '_').replace('.', '_')}.png"
    
    audio_path = os.path.join(MEDIA_ROOT, "audio", audio_filename)
    image_path = os.path.join(MEDIA_ROOT, "images", image_filename)
    
    audio_url = None
    image_url = None
    
    if not os.path.exists(audio_path):
        audio_url = generate_tts(verse['text'], verse['verse_id'])
    else:
        audio_url = f"/media/audio/{audio_filename}"
    
    if not os.path.exists(image_path):
        image_url = generate_verse_image(verse['text'], verse['verse_id'])
    else:
        image_url = f"/media/images/{image_filename}"
    
    # Check if verse is already saved (but don't auto-save)
    with Session(engine) as session:
        db_user = session.get(User, user.id)
        saved_verses = json.loads(db_user.saved_verses or "[]")
        is_already_saved = verse['verse_id'] in saved_verses
        
        # Log daily verse access
        session.add(UsageLog(user_id=user.id, mood=mood, endpoint="daily-verse"))
        session.commit()
        
        return {
            "verse_id": verse['verse_id'],
            "text": verse['text'],
            "source": verse['source'],
            "audio_url": audio_url,
            "image_url": image_url,
            "is_saved": is_already_saved,
            "message": "Daily verse loaded successfully"
        }

@app.get("/my-saved-verses")
def my_saved_verses(user: User = Depends(get_current_user)):
    """Get all saved verses for the user"""
    with Session(engine) as session:
        db_user = session.get(User, user.id)
        saved_verse_ids = json.loads(db_user.saved_verses or "[]")
        
        verses = []
        for verse_id in saved_verse_ids:
            verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).one_or_none()
            if verse:
                verses.append({
                    "verse_id": verse.verse_id,
                    "text": verse.text,
                    "source": verse.source,
                    "image_url": f"/media/images/{verse_id.replace(' ', '_').replace('.', '_')}.png",
                    "audio_url": f"/media/audio/{verse_id.replace(' ', '_').replace('.', '_')}.mp3"
                })
        
        return {"saved_verses": verses}

# ----------------------
# HISTORY ROUTES
# ----------------------

@app.get("/history/{user_id}")
def get_history(user_id: int, current_user: User = Depends(get_current_user)):
    # Users can only see their own history unless they're admin
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    with Session(engine) as session:
        chat_summaries = session.exec(
            select(ChatSummary)
            .where(ChatSummary.user_id == user_id)
            .order_by(ChatSummary.date.desc())
            .limit(50)
        ).all()
        
        history = []
        for summary in chat_summaries:
            history.append({
                "date": summary.date.isoformat(),
                "mood": summary.mood,
                "summary": summary.summary,
                "verse_id": summary.verse_id
            })
        
        return {"history": history}

@app.get("/last-session")
def last_session(user: User = Depends(get_current_user)):
    with Session(engine) as session:
        last_summary = session.exec(
            select(ChatSummary)
            .where(ChatSummary.user_id == user.id)
            .order_by(ChatSummary.date.desc())
        ).first()
        
        if not last_summary:
            return {"message": "No previous session found."}
        
        return {
            "message": f"Last time on {last_summary.date.date().isoformat()} you were feeling {last_summary.mood}. How are you feeling now?",
            "last_session": {
                "date": last_summary.date.isoformat(),
                "mood": last_summary.mood,
                "summary": last_summary.summary,
                "verse_id": last_summary.verse_id
            }
        }

# ----------------------
# USER PROFILE ROUTE
# ----------------------

@app.get("/profile", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)):
    with Session(engine) as session:
        # Get recent chat summaries
        recent_summaries = session.exec(
            select(ChatSummary)
            .where(ChatSummary.user_id == user.id)
            .order_by(ChatSummary.date.desc())
            .limit(10)
        ).all()
        
        chat_history = []
        for summary in recent_summaries:
            chat_history.append({
                "date": summary.date.isoformat(),
                "mood": summary.mood,
                "summary": summary.summary,
                "verse_id": summary.verse_id
            })
        
        return UserProfile(
            user_id=user.uuid,
            name=user.name,
            email=user.email,
            last_mood=user.last_mood,
            recent_verses=json.loads(user.recent_verses or "{}"),
            saved_verses=json.loads(user.saved_verses or "[]"),
            chat_history=chat_history
        )

# ----------------------
# ADMIN ROUTES
# ----------------------

@app.get("/admin/analytics")
def admin_analytics(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        # Active users (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = session.exec(
            select(UsageLog.user_id)
            .where(UsageLog.timestamp >= thirty_days_ago)
        ).all()
        active_user_count = len(set(active_users))
        
        # Mood distribution (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        mood_logs = session.exec(
            select(UsageLog)
            .where(UsageLog.timestamp >= week_ago)
        ).all()
        
        mood_counts = {}
        for log in mood_logs:
            if log.mood:
                mood_counts[log.mood] = mood_counts.get(log.mood, 0) + 1
        
        # Peak usage hours (last 7 days)
        hour_counts = {}
        for log in mood_logs:
            hour = log.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Most popular verses
        verse_counts = {}
        verse_logs = session.exec(
            select(ChatSummary.verse_id)
            .where(ChatSummary.date >= week_ago)
        ).all()
        
        for verse_id in verse_logs:
            if verse_id:
                verse_counts[verse_id] = verse_counts.get(verse_id, 0) + 1
        
        popular_verses = sorted(verse_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "active_users_last_30_days": active_user_count,
            "mood_distribution_last_7_days": mood_counts,
            "peak_usage_hours": peak_hours,
            "popular_verses": popular_verses,
            "total_users": session.exec(select(User)).all().__len__(),
            "total_verses": session.exec(select(Verse)).all().__len__()
        }

# ----------------------
# PDF PROCESSING ROUTE
# ----------------------

@app.post("/admin/process-pdfs")
def process_pdfs(current_user: User = Depends(get_current_user)):
    """Process PDF files and extract verses (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from pdf_processor import process_all_pdfs, save_verses_to_database
        
        # Process all PDFs
        verses_dict = process_all_pdfs()
        
        # Save to database
        save_verses_to_database(verses_dict)
        
        # Reinitialize RAG system with new verses
        try:
            initialize_rag(engine)
            print("✓ RAG system updated with new verses")
        except Exception as e:
            print(f"Warning: Could not update RAG system: {e}")
        
        # Calculate totals
        total_verses = sum(len(verses) for verses in verses_dict.values())
        
        return {
            "success": True,
            "message": f"Successfully processed {len(verses_dict)} PDF files",
            "total_verses_added": total_verses,
            "files_processed": list(verses_dict.keys()),
            "verses_per_file": {k: len(v) for k, v in verses_dict.items()}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

@app.get("/admin/llm-status")
def llm_status(current_user: User = Depends(get_current_user)):
    """Get LLM service status (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        llm = get_llm_service()
        if not llm:
            return {"error": "LLM service not initialized"}
        
        return llm.get_model_info()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting LLM status: {str(e)}")

@app.post("/admin/embedding-status")
def embedding_status(current_user: User = Depends(get_current_user)):
    """Get embedding storage status (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        rag = get_rag_instance()
        if not rag:
            return {"error": "RAG system not initialized"}
        
        storage_info = rag.get_storage_info()
        
        # Add current memory info
        storage_info.update({
            "current_embeddings_in_memory": len(rag.verse_embeddings),
            "current_metadata_in_memory": len(rag.verse_metadata)
        })
        
        return storage_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting embedding status: {str(e)}")

@app.post("/admin/regenerate-embeddings")
def regenerate_embeddings(current_user: User = Depends(get_current_user)):
    """Force regeneration of all embeddings (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        rag = get_rag_instance()
        if not rag:
            raise HTTPException(status_code=500, detail="RAG system not initialized")
        
        rag.regenerate_embeddings()
        
        return {
            "success": True,
            "message": "Embeddings regenerated successfully",
            "total_embeddings": len(rag.verse_embeddings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating embeddings: {str(e)}")

# ----------------------
# SEED DATA ROUTE
# ----------------------

@app.post("/admin/seed-verses")
def seed_verses(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
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
    
    return {"success": True, "verses_added": added_count}

# ----------------------
# STATIC FILES
# ----------------------

from fastapi.staticfiles import StaticFiles
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

# ----------------------
# HEALTH CHECK
# ----------------------

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ----------------------
# RUNNING THE APP
# ----------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
