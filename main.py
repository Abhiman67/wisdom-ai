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
from passlib.context import CryptContext
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

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable must be set")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes for access token
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days for refresh token
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wisdom_user:wisdom_pass@localhost:5432/wisdom_ai")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "./media")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

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

class Collection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    description: Optional[str] = None
    verse_ids: str = Field(default="[]")  # JSON list of verse_ids
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VerseNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    verse_id: str = Field(index=True)
    note: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VerseRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    verse_id: str = Field(index=True)
    rating: int  # 1-5 stars
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VerseComment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    verse_id: str = Field(index=True)
    comment: str
    is_flagged: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReadingPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    duration_days: int
    verse_schedule: str  # JSON: [{"day": 1, "verse_ids": [...]}]
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserReadingPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    reading_plan_id: int = Field(foreign_key="readingplan.id")
    start_date: datetime
    current_day: int = Field(default=1)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailyVerseSchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True, unique=True)
    verse_id: str
    created_by_admin: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    message: str
    type: str  # "info", "success", "warning", "verse_reminder"
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MoodHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    mood: str
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

class SystemLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str  # "INFO", "WARNING", "ERROR"
    message: str
    user_id: Optional[int] = None
    endpoint: Optional[str] = None
    details: Optional[str] = None  # JSON string for additional context
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

class AnalyticsEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    event_type: str  # "verse_view", "verse_save", "chat_message", "daily_verse_view"
    verse_id: Optional[str] = None
    event_metadata: Optional[str] = None  # JSON string
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

class ShareableLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True)
    verse_id: str
    created_by: int = Field(foreign_key="user.id")
    views: int = Field(default=0)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ABTest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    variant_a: str  # JSON config
    variant_b: str  # JSON config
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ABTestAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    test_id: int = Field(foreign_key="abtest.id")
    variant: str  # "A" or "B"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ----------------------
# DB INITIALIZATION
# ----------------------

engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# ----------------------
# UTILITIES
# ----------------------

# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

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
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    created_at: Optional[str] = None
    streak: int = 0
    favorite_source: Optional[str] = None

class CollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    verse_ids: List[str] = []
    is_public: bool = False

class NoteRequest(BaseModel):
    note: str

class RatingRequest(BaseModel):
    rating: int

class CommentRequest(BaseModel):
    comment: str

class ShareResponse(BaseModel):
    share_url: str
    token: str

class ReadingPlanRequest(BaseModel):
    name: str
    description: str
    duration_days: int
    verse_schedule: List[Dict[str, Any]]

class ABTestRequest(BaseModel):
    name: str
    description: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]

# ----------------------
# HELPER FUNCTIONS
# ----------------------

def log_system_event(level: str, message: str, user_id: Optional[int] = None, 
                     endpoint: Optional[str] = None, details: Optional[Dict] = None):
    """Log system events to database"""
    with Session(engine) as session:
        log = SystemLog(
            level=level,
            message=message,
            user_id=user_id,
            endpoint=endpoint,
            details=json.dumps(details) if details else None
        )
        session.add(log)
        session.commit()

def track_analytics(user_id: int, event_type: str, verse_id: Optional[str] = None, 
                   metadata: Optional[Dict] = None):
    """Track analytics events"""
    with Session(engine) as session:
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            verse_id=verse_id,
            event_metadata=json.dumps(metadata) if metadata else None
        )
        session.add(event)
        session.commit()

# ----------------------
# ORIGINAL HELPER FUNCTIONS
# ----------------------

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

# Optional authentication - returns guest user if no token
def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    if not credentials:
        # Return a guest user for unauthenticated access
        with Session(engine) as session:
            guest = session.exec(select(User).where(User.email == "guest@wisdom-ai.com")).one_or_none()
            if not guest:
                # Create guest user if doesn't exist
                guest = User(
                    name="Guest User",
                    email="guest@wisdom-ai.com",
                    hashed_password=hash_password("guest123"),
                    is_admin=False
                )
                session.add(guest)
                session.commit()
                session.refresh(guest)
            return guest
    
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
@limiter.limit("5/minute")
def signup(request: Request, signup_data: SignupRequest):
    # Validate password strength
    if len(signup_data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in signup_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not any(c.islower() for c in signup_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in signup_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    
    with Session(engine) as session:
        # Check if email already exists
        existing_user = session.exec(select(User).where(User.email == signup_data.email)).one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(signup_data.password)
        user = User(
            name=signup_data.name,
            email=signup_data.email,
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
@limiter.limit("10/minute")
def login(request: Request, login_data: LoginRequest):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == login_data.email)).one_or_none()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
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
def chat(request: ChatRequest, user: User = Depends(get_current_user_optional)):
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
def save_verse_from_daily(user: User = Depends(get_current_user_optional)):
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
def daily_verse_with_save(user: User = Depends(get_current_user_optional)):
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
def my_saved_verses(user: User = Depends(get_current_user_optional)):
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
    """Get chat history for a user"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    with Session(engine) as session:
        summaries = session.exec(
            select(ChatSummary)
            .where(ChatSummary.user_id == user_id)
            .order_by(ChatSummary.date.desc())
            .limit(50)
        ).all()
        
        return [{
            "id": s.id,
            "date": s.date.isoformat(),
            "mood": s.mood,
            "summary": s.summary,
            "verse_id": s.verse_id
        } for s in summaries]

# ----------------------
# COLLECTIONS ROUTES
# ----------------------

@app.post("/collections")
def create_collection(request: CollectionRequest, user: User = Depends(get_current_user)):
    """Create a new verse collection"""
    with Session(engine) as session:
        collection = Collection(
            user_id=user.id,
            name=request.name,
            description=request.description,
            verse_ids=json.dumps(request.verse_ids),
            is_public=request.is_public
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        track_analytics(user.id, "collection_created", metadata={"collection_id": collection.id})
        
        return {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "verse_count": len(request.verse_ids),
            "is_public": collection.is_public
        }

@app.get("/collections")
def get_collections(user: User = Depends(get_current_user)):
    """Get user's collections"""
    with Session(engine) as session:
        collections = session.exec(
            select(Collection).where(Collection.user_id == user.id)
        ).all()
        
        return [{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "verse_count": len(json.loads(c.verse_ids)),
            "is_public": c.is_public,
            "created_at": c.created_at.isoformat()
        } for c in collections]

@app.get("/collections/{collection_id}")
def get_collection(collection_id: int, user: User = Depends(get_current_user)):
    """Get collection details with verses"""
    with Session(engine) as session:
        collection = session.get(Collection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        if collection.user_id != user.id and not collection.is_public:
            raise HTTPException(status_code=403, detail="Access denied")
        
        verse_ids = json.loads(collection.verse_ids)
        verses = []
        for vid in verse_ids:
            verse = session.exec(select(Verse).where(Verse.verse_id == vid)).first()
            if verse:
                verses.append({
                    "verse_id": verse.verse_id,
                    "text": verse.text,
                    "source": verse.source
                })
        
        return {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "verses": verses,
            "is_public": collection.is_public,
            "created_at": collection.created_at.isoformat()
        }

@app.post("/collections/{collection_id}/verses/{verse_id}")
def add_verse_to_collection(collection_id: int, verse_id: str, user: User = Depends(get_current_user)):
    """Add a verse to collection"""
    with Session(engine) as session:
        collection = session.get(Collection, collection_id)
        if not collection or collection.user_id != user.id:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        verse_ids = json.loads(collection.verse_ids)
        if verse_id not in verse_ids:
            verse_ids.append(verse_id)
            collection.verse_ids = json.dumps(verse_ids)
            collection.updated_at = datetime.utcnow()
            session.commit()
        
        return {"success": True, "verse_count": len(verse_ids)}

@app.delete("/collections/{collection_id}/verses/{verse_id}")
def remove_verse_from_collection(collection_id: int, verse_id: str, user: User = Depends(get_current_user)):
    """Remove a verse from collection"""
    with Session(engine) as session:
        collection = session.get(Collection, collection_id)
        if not collection or collection.user_id != user.id:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        verse_ids = json.loads(collection.verse_ids)
        if verse_id in verse_ids:
            verse_ids.remove(verse_id)
            collection.verse_ids = json.dumps(verse_ids)
            collection.updated_at = datetime.utcnow()
            session.commit()
        
        return {"success": True, "verse_count": len(verse_ids)}

# ----------------------
# VERSE NOTES ROUTES
# ----------------------

@app.post("/verses/{verse_id}/notes")
def add_note(verse_id: str, request: NoteRequest, user: User = Depends(get_current_user)):
    """Add a note to a verse"""
    with Session(engine) as session:
        note = VerseNote(
            user_id=user.id,
            verse_id=verse_id,
            note=request.note
        )
        session.add(note)
        session.commit()
        session.refresh(note)
        
        track_analytics(user.id, "note_added", verse_id=verse_id)
        
        return {
            "id": note.id,
            "verse_id": note.verse_id,
            "note": note.note,
            "created_at": note.created_at.isoformat()
        }

@app.get("/verses/{verse_id}/notes")
def get_notes(verse_id: str, user: User = Depends(get_current_user)):
    """Get user's notes for a verse"""
    with Session(engine) as session:
        notes = session.exec(
            select(VerseNote)
            .where(VerseNote.verse_id == verse_id)
            .where(VerseNote.user_id == user.id)
        ).all()
        
        return [{
            "id": n.id,
            "note": n.note,
            "created_at": n.created_at.isoformat(),
            "updated_at": n.updated_at.isoformat()
        } for n in notes]

@app.put("/verses/{verse_id}/notes/{note_id}")
def update_note(verse_id: str, note_id: int, request: NoteRequest, user: User = Depends(get_current_user)):
    """Update a note"""
    with Session(engine) as session:
        note = session.get(VerseNote, note_id)
        if not note or note.user_id != user.id:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note.note = request.note
        note.updated_at = datetime.utcnow()
        session.commit()
        
        return {"success": True, "updated_at": note.updated_at.isoformat()}

# ----------------------
# VERSE SHARING ROUTES
# ----------------------

@app.post("/verses/{verse_id}/share", response_model=ShareResponse)
def share_verse(verse_id: str, user: User = Depends(get_current_user)):
    """Generate shareable link for a verse"""
    import secrets
    
    with Session(engine) as session:
        # Check if verse exists
        verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).first()
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        # Generate unique token
        token = secrets.token_urlsafe(16)
        
        share_link = ShareableLink(
            token=token,
            verse_id=verse_id,
            created_by=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session.add(share_link)
        session.commit()
        
        track_analytics(user.id, "verse_shared", verse_id=verse_id)
        
        # In production, use actual domain
        share_url = f"https://wisdom-ai.com/share/{token}"
        
        return ShareResponse(share_url=share_url, token=token)

@app.get("/share/{token}")
def view_shared_verse(token: str):
    """Public endpoint to view shared verse"""
    with Session(engine) as session:
        share_link = session.exec(
            select(ShareableLink).where(ShareableLink.token == token)
        ).first()
        
        if not share_link:
            raise HTTPException(status_code=404, detail="Share link not found")
        
        if share_link.expires_at and share_link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Share link expired")
        
        # Increment view count
        share_link.views += 1
        session.commit()
        
        # Get verse
        verse = session.exec(
            select(Verse).where(Verse.verse_id == share_link.verse_id)
        ).first()
        
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        return {
            "verse_id": verse.verse_id,
            "text": verse.text,
            "source": verse.source,
            "views": share_link.views
        }

# ----------------------
# COMMUNITY FEATURES (RATINGS & COMMENTS)
# ----------------------

@app.post("/verses/{verse_id}/rate")
def rate_verse(verse_id: str, request: RatingRequest, user: User = Depends(get_current_user)):
    """Rate a verse (1-5 stars)"""
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    with Session(engine) as session:
        # Check if user already rated
        existing = session.exec(
            select(VerseRating)
            .where(VerseRating.verse_id == verse_id)
            .where(VerseRating.user_id == user.id)
        ).first()
        
        if existing:
            existing.rating = request.rating
            session.commit()
            return {"success": True, "message": "Rating updated"}
        else:
            rating = VerseRating(
                user_id=user.id,
                verse_id=verse_id,
                rating=request.rating
            )
            session.add(rating)
            session.commit()
            
            track_analytics(user.id, "verse_rated", verse_id=verse_id, metadata={"rating": request.rating})
            
            return {"success": True, "message": "Rating added"}

@app.get("/verses/{verse_id}/rating")
def get_verse_rating(verse_id: str):
    """Get average rating for a verse"""
    with Session(engine) as session:
        ratings = session.exec(
            select(VerseRating).where(VerseRating.verse_id == verse_id)
        ).all()
        
        if not ratings:
            return {"average": 0, "count": 0}
        
        avg = sum(r.rating for r in ratings) / len(ratings)
        return {"average": round(avg, 2), "count": len(ratings)}

@app.post("/verses/{verse_id}/comments")
def add_comment(verse_id: str, request: CommentRequest, user: User = Depends(get_current_user)):
    """Add a comment to a verse"""
    with Session(engine) as session:
        comment = VerseComment(
            user_id=user.id,
            verse_id=verse_id,
            comment=request.comment
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        
        track_analytics(user.id, "comment_added", verse_id=verse_id)
        
        return {
            "id": comment.id,
            "comment": comment.comment,
            "created_at": comment.created_at.isoformat()
        }

@app.get("/verses/{verse_id}/comments")
def get_comments(verse_id: str, skip: int = 0, limit: int = 20):
    """Get comments for a verse"""
    with Session(engine) as session:
        comments = session.exec(
            select(VerseComment, User)
            .where(VerseComment.verse_id == verse_id)
            .where(VerseComment.is_flagged == False)
            .where(VerseComment.user_id == User.id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        return [{
            "id": c[0].id,
            "comment": c[0].comment,
            "user_name": c[1].name,
            "created_at": c[0].created_at.isoformat()
        } for c in comments]

# ----------------------
# MOOD TRACKING
# ----------------------

@app.get("/mood-history")
def get_mood_history(user: User = Depends(get_current_user), days: int = 30):
    """Get user's mood history over time"""
    with Session(engine) as session:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        moods = session.exec(
            select(MoodHistory)
            .where(MoodHistory.user_id == user.id)
            .where(MoodHistory.timestamp >= cutoff)
            .order_by(MoodHistory.timestamp.asc())
        ).all()
        
        return [{
            "mood": m.mood,
            "timestamp": m.timestamp.isoformat()
        } for m in moods]

# ----------------------
# READING PLANS
# ----------------------

@app.get("/reading-plans")
def get_reading_plans():
    """Get all available reading plans"""
    with Session(engine) as session:
        plans = session.exec(
            select(ReadingPlan).where(ReadingPlan.is_active == True)
        ).all()
        
        return [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "duration_days": p.duration_days
        } for p in plans]

@app.post("/reading-plans/{plan_id}/enroll")
def enroll_in_plan(plan_id: int, user: User = Depends(get_current_user)):
    """Enroll user in a reading plan"""
    with Session(engine) as session:
        # Check if plan exists
        plan = session.get(ReadingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Reading plan not found")
        
        # Check if already enrolled
        existing = session.exec(
            select(UserReadingPlan)
            .where(UserReadingPlan.user_id == user.id)
            .where(UserReadingPlan.reading_plan_id == plan_id)
            .where(UserReadingPlan.completed == False)
        ).first()
        
        if existing:
            return {"success": False, "message": "Already enrolled in this plan"}
        
        enrollment = UserReadingPlan(
            user_id=user.id,
            reading_plan_id=plan_id,
            start_date=datetime.utcnow()
        )
        session.add(enrollment)
        session.commit()
        
        track_analytics(user.id, "reading_plan_enrolled", metadata={"plan_id": plan_id})
        
        return {"success": True, "message": "Enrolled successfully"}

@app.get("/my-reading-plans")
def get_my_reading_plans(user: User = Depends(get_current_user)):
    """Get user's enrolled reading plans"""
    with Session(engine) as session:
        enrollments = session.exec(
            select(UserReadingPlan, ReadingPlan)
            .where(UserReadingPlan.user_id == user.id)
            .where(UserReadingPlan.reading_plan_id == ReadingPlan.id)
        ).all()
        
        return [{
            "enrollment_id": e[0].id,
            "plan_name": e[1].name,
            "plan_description": e[1].description,
            "duration_days": e[1].duration_days,
            "current_day": e[0].current_day,
            "completed": e[0].completed,
            "start_date": e[0].start_date.isoformat()
        } for e in enrollments]

# ----------------------
# NOTIFICATIONS
# ----------------------

@app.get("/notifications")
def get_notifications(user: User = Depends(get_current_user), unread_only: bool = False):
    """Get user's notifications"""
    with Session(engine) as session:
        query = select(Notification).where(Notification.user_id == user.id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        notifications = session.exec(
            query.order_by(Notification.created_at.desc()).limit(50)
        ).all()
        
        return [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifications]

@app.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user: User = Depends(get_current_user)):
    """Mark notification as read"""
    with Session(engine) as session:
        notification = session.get(Notification, notification_id)
        if not notification or notification.user_id != user.id:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        session.commit()
        
        return {"success": True}

# ----------------------
# HISTORY ROUTES (ORIGINAL)
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
def get_profile(user: User = Depends(get_current_user_optional)):
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
        
        # Calculate streak from usage logs
        streak = 0
        try:
            logs = session.exec(
                select(UsageLog)
                .where(UsageLog.user_id == user.id)
                .order_by(UsageLog.timestamp.desc())
            ).all()
            
            if logs:
                dates = sorted(set(log.timestamp.date() for log in logs), reverse=True)
                current_date = datetime.utcnow().date()
                streak = 0
                for date in dates:
                    if date == current_date or (current_date - date).days == streak:
                        streak += 1
                        current_date = date
                    else:
                        break
        except:
            streak = 0
        
        # Calculate favorite source from saved verses
        favorite_source = None
        try:
            saved_verse_ids = json.loads(user.saved_verses or "[]")
            if saved_verse_ids:
                source_counts = {}
                for verse_id in saved_verse_ids:
                    verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).one_or_none()
                    if verse:
                        source_counts[verse.source] = source_counts.get(verse.source, 0) + 1
                if source_counts:
                    favorite_source = max(source_counts, key=source_counts.get)
        except:
            favorite_source = None
        
        return UserProfile(
            user_id=user.uuid,
            name=user.name,
            email=user.email,
            last_mood=user.last_mood,
            recent_verses=json.loads(user.recent_verses or "{}"),
            saved_verses=json.loads(user.saved_verses or "[]"),
            chat_history=chat_history,
            created_at=user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            streak=streak,
            favorite_source=favorite_source
        )

# ----------------------
# ADMIN ROUTES
# ----------------------

@app.get("/admin/analytics")
def admin_analytics(current_user: User = Depends(get_current_user_optional)):
    # Temporarily allow all users to access admin for testing (remove in production)
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
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
        
        # Top verses (by saves)
        all_users = session.exec(select(User)).all()
        verse_save_counts = {}
        for u in all_users:
            saved = json.loads(u.saved_verses or "[]")
            for vid in saved:
                verse_save_counts[vid] = verse_save_counts.get(vid, 0) + 1
        
        popular_verses = sorted(verse_save_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Total counts
        total_users = session.exec(select(User)).all()
        total_verses = session.exec(select(Verse)).all()
        
        return {
            "active_users_last_30_days": active_user_count,
            "mood_distribution_last_7_days": mood_counts,
            "peak_usage_hours": sorted(hour_counts.items()),
            "popular_verses": popular_verses,
            "total_users": len(total_users),
            "total_verses": len(total_verses)
        }

# ----------------------
# ADMIN USER MANAGEMENT
# ----------------------

@app.get("/admin/users")
def admin_get_users(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None
):
    """Get all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        query = select(User)
        
        if search:
            query = query.where(
                (User.name.contains(search)) | (User.email.contains(search))
            )
        
        users = session.exec(query.offset(skip).limit(limit)).all()
        
        return [{
            "id": u.id,
            "uuid": u.uuid,
            "name": u.name,
            "email": u.email,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat(),
            "last_mood": u.last_mood
        } for u in users]

@app.put("/admin/users/{user_id}")
def admin_update_user(
    user_id: int,
    is_admin: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """Update user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if is_admin is not None:
            user.is_admin = is_admin
        
        session.commit()
        
        log_system_event("INFO", f"User {user.email} updated by admin", current_user.id, "/admin/users")
        
        return {"success": True, "message": "User updated"}

@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Delete user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_admin:
            raise HTTPException(status_code=400, detail="Cannot delete admin user")
        
        session.delete(user)
        session.commit()
        
        log_system_event("WARNING", f"User {user.email} deleted by admin", current_user.id, "/admin/users")
        
        return {"success": True, "message": "User deleted"}

# ----------------------
# ADMIN VERSE MANAGEMENT
# ----------------------

@app.get("/admin/verses")
def admin_get_verses(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    source: Optional[str] = None
):
    """Get all verses (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        query = select(Verse)
        
        if search:
            query = query.where(Verse.text.contains(search) | Verse.verse_id.contains(search))
        
        if source:
            query = query.where(Verse.source == source)
        
        verses = session.exec(query.offset(skip).limit(limit)).all()
        
        return [{
            "id": v.id,
            "verse_id": v.verse_id,
            "text": v.text[:200] + "..." if len(v.text) > 200 else v.text,
            "source": v.source,
            "created_at": v.created_at.isoformat()
        } for v in verses]

@app.post("/admin/verses")
def admin_create_verse(
    verse_id: str,
    text: str,
    source: str,
    mood_tags: List[str] = [],
    current_user: User = Depends(get_current_user)
):
    """Create new verse (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        # Check if verse_id already exists
        existing = session.exec(select(Verse).where(Verse.verse_id == verse_id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Verse ID already exists")
        
        verse = Verse(
            verse_id=verse_id,
            text=text,
            source=source,
            mood_tags=json.dumps(mood_tags)
        )
        session.add(verse)
        session.commit()
        
        log_system_event("INFO", f"Verse {verse_id} created by admin", current_user.id, "/admin/verses")
        
        return {"success": True, "verse_id": verse_id}

@app.put("/admin/verses/{verse_id}")
def admin_update_verse(
    verse_id: str,
    text: Optional[str] = None,
    source: Optional[str] = None,
    mood_tags: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """Update verse (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).first()
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        if text:
            verse.text = text
        if source:
            verse.source = source
        if mood_tags is not None:
            verse.mood_tags = json.dumps(mood_tags)
        
        session.commit()
        
        log_system_event("INFO", f"Verse {verse_id} updated by admin", current_user.id, "/admin/verses")
        
        return {"success": True, "message": "Verse updated"}

@app.delete("/admin/verses/{verse_id}")
def admin_delete_verse(verse_id: str, current_user: User = Depends(get_current_user)):
    """Delete verse (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).first()
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        session.delete(verse)
        session.commit()
        
        log_system_event("WARNING", f"Verse {verse_id} deleted by admin", current_user.id, "/admin/verses")
        
        return {"success": True, "message": "Verse deleted"}

# ----------------------
# ADMIN CONTENT MODERATION
# ----------------------

@app.get("/admin/moderation/flagged")
def admin_get_flagged_content(current_user: User = Depends(get_current_user_optional)):
    """Get flagged comments (admin only)"""
    # Temporarily disabled for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        flagged = session.exec(
            select(VerseComment, User)
            .where(VerseComment.is_flagged == True)
            .where(VerseComment.user_id == User.id)
        ).all()
        
        return [{
            "id": c[0].id,
            "verse_id": c[0].verse_id,
            "comment": c[0].comment,
            "user_name": c[1].name,
            "user_email": c[1].email,
            "created_at": c[0].created_at.isoformat()
        } for c in flagged]

@app.post("/admin/moderation/{comment_id}/approve")
def admin_approve_comment(comment_id: int, current_user: User = Depends(get_current_user_optional)):
    """Approve flagged comment (admin only)"""
    # Temporarily disabled for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        comment = session.get(VerseComment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comment.is_flagged = False
        session.commit()
        
        log_system_event("INFO", f"Comment {comment_id} approved by admin", current_user.id, "/admin/moderation")
        
        return {"success": True, "message": "Comment approved"}

@app.delete("/admin/moderation/{comment_id}/delete")
def admin_delete_comment(comment_id: int, current_user: User = Depends(get_current_user_optional)):
    """Delete flagged comment (admin only)"""
    # Temporarily disabled for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        comment = session.get(VerseComment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        session.delete(comment)
        session.commit()
        
        log_system_event("WARNING", f"Comment {comment_id} deleted by admin", current_user.id, "/admin/moderation")
        
        return {"success": True, "message": "Comment deleted"}

@app.post("/verses/{verse_id}/comments/{comment_id}/flag")
def flag_comment(verse_id: str, comment_id: int, user: User = Depends(get_current_user)):
    """Flag a comment for moderation"""
    with Session(engine) as session:
        comment = session.get(VerseComment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comment.is_flagged = True
        session.commit()
        
        # Create notification for admins
        admins = session.exec(select(User).where(User.is_admin == True)).all()
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title="Comment Flagged",
                message=f"A comment on {verse_id} has been flagged for review",
                type="warning"
            )
            session.add(notification)
        session.commit()
        
        return {"success": True, "message": "Comment flagged for review"}

# ----------------------
# ADMIN SYSTEM LOGS
# ----------------------

@app.get("/admin/logs")
def admin_get_logs(
    current_user: User = Depends(get_current_user),
    level: Optional[str] = None,
    limit: int = 100
):
    """Get system logs (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        query = select(SystemLog)
        
        if level:
            query = query.where(SystemLog.level == level)
        
        logs = session.exec(query.order_by(SystemLog.timestamp.desc()).limit(limit)).all()
        
        return [{
            "id": l.id,
            "level": l.level,
            "message": l.message,
            "user_id": l.user_id,
            "endpoint": l.endpoint,
            "timestamp": l.timestamp.isoformat()
        } for l in logs]

# ----------------------
# ADMIN ANALYTICS
# ----------------------

@app.get("/admin/analytics/engagement")
def admin_engagement_metrics(current_user: User = Depends(get_current_user_optional), days: int = 30):
    """Get user engagement metrics (admin only)"""
    # Temporarily disabled for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Event counts by type
        events = session.exec(
            select(AnalyticsEvent)
            .where(AnalyticsEvent.timestamp >= cutoff)
        ).all()
        
        event_counts = {}
        for e in events:
            event_counts[e.event_type] = event_counts.get(e.event_type, 0) + 1
        
        # Daily active users
        daily_users = {}
        for e in events:
            day = e.timestamp.date().isoformat()
            if day not in daily_users:
                daily_users[day] = set()
            daily_users[day].add(e.user_id)
        
        dau = {day: len(users) for day, users in daily_users.items()}
        
        return {
            "event_counts": event_counts,
            "daily_active_users": dau,
            "total_events": len(events)
        }

@app.get("/admin/analytics/verse-popularity")
def admin_verse_popularity(current_user: User = Depends(get_current_user_optional), limit: int = 20):
    """Get verse popularity metrics (admin only)"""
    # Temporarily disabled for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        # Count by verse views
        events = session.exec(
            select(AnalyticsEvent)
            .where(AnalyticsEvent.event_type == "verse_view")
        ).all()
        
        verse_views = {}
        for e in events:
            if e.verse_id:
                verse_views[e.verse_id] = verse_views.get(e.verse_id, 0) + 1
        
        # Get verse details
        popular = sorted(verse_views.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        result = []
        for verse_id, views in popular:
            verse = session.exec(select(Verse).where(Verse.verse_id == verse_id)).first()
            if verse:
                result.append({
                    "verse_id": verse_id,
                    "views": views,
                    "text": verse.text[:100] + "...",
                    "source": verse.source
                })
        
        return result

# ----------------------
# ADMIN A/B TESTING
# ----------------------

@app.post("/admin/ab-test")
def admin_create_ab_test(request: ABTestRequest, current_user: User = Depends(get_current_user)):
    """Create A/B test (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        test = ABTest(
            name=request.name,
            description=request.description,
            variant_a=json.dumps(request.variant_a),
            variant_b=json.dumps(request.variant_b)
        )
        session.add(test)
        session.commit()
        session.refresh(test)
        
        log_system_event("INFO", f"A/B test '{request.name}' created", current_user.id, "/admin/ab-test")
        
        return {"success": True, "test_id": test.id}

@app.get("/admin/ab-tests")
def admin_get_ab_tests(current_user: User = Depends(get_current_user)):
    """Get all A/B tests (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        tests = session.exec(select(ABTest)).all()
        
        return [{
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat()
        } for t in tests]

@app.get("/my-ab-tests")
def get_my_ab_test_variants(user: User = Depends(get_current_user)):
    """Get user's A/B test assignments"""
    with Session(engine) as session:
        assignments = session.exec(
            select(ABTestAssignment, ABTest)
            .where(ABTestAssignment.user_id == user.id)
            .where(ABTestAssignment.test_id == ABTest.id)
            .where(ABTest.is_active == True)
        ).all()
        
        return [{
            "test_name": a[1].name,
            "variant": a[0].variant,
            "config": json.loads(a[1].variant_a if a[0].variant == "A" else a[1].variant_b)
        } for a in assignments]

# ----------------------
# ADMIN READING PLAN MANAGEMENT
# ----------------------

@app.post("/admin/reading-plans")
def admin_create_reading_plan(request: ReadingPlanRequest, current_user: User = Depends(get_current_user)):
    """Create reading plan (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        plan = ReadingPlan(
            name=request.name,
            description=request.description,
            duration_days=request.duration_days,
            verse_schedule=json.dumps(request.verse_schedule)
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)
        
        log_system_event("INFO", f"Reading plan '{request.name}' created", current_user.id, "/admin/reading-plans")
        
        return {"success": True, "plan_id": plan.id}

@app.put("/admin/reading-plans/{plan_id}")
def admin_update_reading_plan(
    plan_id: int,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """Update reading plan (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        plan = session.get(ReadingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Reading plan not found")
        
        if is_active is not None:
            plan.is_active = is_active
        
        session.commit()
        
        return {"success": True, "message": "Reading plan updated"}

# ----------------------
# ADMIN DAILY VERSE SCHEDULE
# ----------------------

@app.post("/admin/daily-verse-schedule")
def admin_schedule_daily_verse(
    date: str,  # ISO format: "2025-11-15"
    verse_id: str,
    current_user: User = Depends(get_current_user)
):
    """Schedule a specific verse for a date (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        # Parse date
        schedule_date = datetime.fromisoformat(date)
        
        # Check if already scheduled
        existing = session.exec(
            select(DailyVerseSchedule).where(DailyVerseSchedule.date == schedule_date)
        ).first()
        
        if existing:
            existing.verse_id = verse_id
            session.commit()
            return {"success": True, "message": "Schedule updated"}
        else:
            schedule = DailyVerseSchedule(
                date=schedule_date,
                verse_id=verse_id,
                created_by_admin=current_user.id
            )
            session.add(schedule)
            session.commit()
            return {"success": True, "message": "Verse scheduled"}

@app.get("/admin/daily-verse-schedule")
def admin_get_schedule(current_user: User = Depends(get_current_user), days: int = 30):
    """Get daily verse schedule (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        cutoff = datetime.utcnow() - timedelta(days=1)
        future = datetime.utcnow() + timedelta(days=days)
        
        schedules = session.exec(
            select(DailyVerseSchedule)
            .where(DailyVerseSchedule.date >= cutoff)
            .where(DailyVerseSchedule.date <= future)
            .order_by(DailyVerseSchedule.date.asc())
        ).all()
        
        return [{
            "date": s.date.isoformat(),
            "verse_id": s.verse_id
        } for s in schedules]

# ----------------------
# ORIGINAL ADMIN ROUTES (REMOVED DUPLICATE)
# ----------------------

@app.get("/admin/system-health")
def admin_system_health(current_user: User = Depends(get_current_user_optional)):
    """Get detailed system health status (admin only)"""
    # Temporarily allow all users to access admin for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    health_status = {
        "application": True,
        "database": False,
        "api": True,
        "llm": False
    }
    
    # Check database
    try:
        with Session(engine) as session:
            session.exec(select(User).limit(1)).first()
            health_status["database"] = True
    except:
        pass
    
    # Check LLM
    try:
        llm = get_llm_service()
        if llm:
            health_status["llm"] = True
    except:
        pass
    
    return health_status

@app.get("/admin/recent-activity")
def admin_recent_activity(current_user: User = Depends(get_current_user_optional)):
    """Get recent system activity (admin only)"""
    # Temporarily allow all users to access admin for testing
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    with Session(engine) as session:
        # Get recent chat summaries
        recent_chats = session.exec(
            select(ChatSummary)
            .order_by(ChatSummary.date.desc())
            .limit(5)
        ).all()
        
        # Get recent user logins (from usage logs)
        recent_logins = session.exec(
            select(UsageLog)
            .where(UsageLog.endpoint == "chat")
            .order_by(UsageLog.timestamp.desc())
            .limit(5)
        ).all()
        
        activities = []
        
        for chat in recent_chats:
            time_diff = datetime.utcnow() - chat.date
            minutes = int(time_diff.total_seconds() / 60)
            timestamp = f"{minutes} minutes ago" if minutes < 60 else f"{int(minutes/60)} hours ago"
            activities.append({
                "type": "chat",
                "message": f"New chat session created",
                "timestamp": timestamp
            })
        
        for login in recent_logins[:3]:
            time_diff = datetime.utcnow() - login.timestamp
            minutes = int(time_diff.total_seconds() / 60)
            timestamp = f"{minutes} minutes ago" if minutes < 60 else f"{int(minutes/60)} hours ago"
            activities.append({
                "type": "user_login",
                "message": f"User accessed the system",
                "timestamp": timestamp
            })
        
        # Sort by most recent
        return activities[:10]

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
