# God AI Backend - API Documentation

## Overview

The God AI Backend provides a comprehensive REST API for a spiritual AI companion application. It features mood detection, intelligent verse recommendations, multimedia generation, and user management.

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /signup
Register a new user account.

**Request Body:**
```json
{
  "name": "Bhawya",
  "email": "bhawya@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "John Doe"
}
```

#### POST /login
Authenticate user and receive JWT token.

**Request Body (form-data):**
```
username: john@example.com
password: securepassword123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "John Doe"
}
```

### Chat & AI

#### POST /chat
Send a message to the AI companion and receive a personalized response with verse recommendation.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "I'm feeling sad and need some comfort"
}
```

**Response:**
```json
{
  "reply": "I understand you're going through a difficult time. Let this verse bring you comfort:\n\n\"The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters.\"\n\n— Bible - Psalms\n\nHow does this resonate with you today?",
  "detected_mood": "sad",
  "verse_id": "Psalm_23.1",
  "verse_text": "The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
  "verse_source": "Bible - Psalms"
}
```

#### GET /daily-verse
Get a personalized daily verse with audio and image (no automatic saving).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "verse_id": "Gita_2.47",
  "text": "You have a right to perform your prescribed duties, but not to the fruits of your actions...",
  "source": "Bhagavad Gita",
  "audio_url": "/media/audio/Gita_2_47.mp3",
  "image_url": "/media/images/Gita_2_47.png"
}
```

#### GET /daily-verse-with-save
Get daily verse with save status (recommended for frontend daily verse page).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "verse_id": "Gita_2.47",
  "text": "You have a right to perform your prescribed duties, but not to the fruits of your actions...",
  "source": "Bhagavad Gita",
  "audio_url": "/media/audio/Gita_2_47.mp3",
  "image_url": "/media/images/Gita_2_47.png",
  "is_saved": false,
  "message": "Daily verse loaded successfully"
}
```

#### GET /last-session
Recall the user's last conversation session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Last time on 2024-01-15 you were feeling sad. How are you feeling now?",
  "last_session": {
    "date": "2024-01-15T10:30:00Z",
    "mood": "sad",
    "summary": "User discussed feelings of loneliness and received comfort from Psalm 23",
    "verse_id": "Psalm_23.1"
  }
}
```

### Verse Management

#### POST /save-verse
Save a specific verse to the user's favorites.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "verse_id": "Gita_2.47"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verse saved successfully"
}
```

#### POST /save-verse-from-daily
Automatically save the current daily verse to user's favorites.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Daily verse saved successfully",
  "verse_id": "Gita_2.47",
  "verse_text": "You have a right to perform your prescribed duties...",
  "source": "Bhagavad Gita"
}
```

#### GET /my-saved-verses
Retrieve all saved verses for the user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "saved_verses": [
    {
      "verse_id": "Gita_2.47",
      "text": "You have a right to perform your prescribed duties...",
      "source": "Bhagavad Gita",
      "image_url": "/media/images/Gita_2_47.png",
      "audio_url": "/media/audio/Gita_2_47.mp3"
    }
  ]
}
```

### User Profile

#### GET /profile
Get comprehensive user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "John Doe",
  "email": "john@example.com",
  "last_mood": "sad",
  "recent_verses": {
    "sad": ["Psalm_23.1", "Quran_94.5"],
    "happy": ["Psalm_46.1"]
  },
  "saved_verses": ["Gita_2.47", "Psalm_23.1"],
  "chat_history": [
    {
      "date": "2024-01-15T10:30:00Z",
      "mood": "sad",
      "summary": "User discussed feelings of loneliness",
      "verse_id": "Psalm_23.1"
    }
  ]
}
```

#### GET /history/{user_id}
Get conversation history for a specific user (admin or self only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "history": [
    {
      "date": "2024-01-15T10:30:00Z",
      "mood": "sad",
      "summary": "User discussed feelings of loneliness",
      "verse_id": "Psalm_23.1"
    }
  ]
}
```

### Admin Endpoints

#### GET /admin/analytics
Get comprehensive usage analytics (admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "active_users_last_30_days": 150,
  "mood_distribution_last_7_days": {
    "sad": 45,
    "happy": 32,
    "neutral": 28,
    "angry": 12
  },
  "peak_usage_hours": [
    [20, 25],
    [21, 18],
    [19, 15]
  ],
  "popular_verses": [
    ["Psalm_23.1", 15],
    ["Gita_2.47", 12],
    ["Quran_94.5", 8]
  ],
  "total_users": 150,
  "total_verses": 15
}
```

#### POST /admin/process-pdfs
Process PDF files and extract verses from religious texts (admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 4 PDF files",
  "total_verses_added": 1247,
  "files_processed": [
    "bhagwad_gita.pdf",
    "Holy-Quran-English.pdf",
    "CSB_Pew_Bible_2nd_Printing.pdf",
    "Siri Guru Granth - English Translation (matching pages).pdf"
  ],
  "verses_per_file": {
    "bhagwad_gita.pdf": 700,
    "Holy-Quran-English.pdf": 6236,
    "CSB_Pew_Bible_2nd_Printing.pdf": 31102,
    "Siri Guru Granth - English Translation (matching pages).pdf": 1430
  }
}
```

#### POST /admin/seed-verses
Initialize the database with sample verses (admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "verses_added": 15
}
```

### Utility Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

## Data Models

### User Profile
```json
{
  "user_id": "uuid",
  "name": "string",
  "email": "string",
  "last_mood": "happy|sad|angry|fear|surprise|disgust|neutral",
  "recent_verses": {
    "mood": ["verse_id1", "verse_id2"]
  },
  "saved_verses": ["verse_id1", "verse_id2"],
  "chat_history": [
    {
      "date": "ISO8601_datetime",
      "mood": "string",
      "summary": "string",
      "verse_id": "string"
    }
  ]
}
```

### Verse
```json
{
  "verse_id": "string",
  "text": "string",
  "source": "string",
  "mood_tags": ["tag1", "tag2"]
}
```

## Mood Detection

The system detects emotions using a transformer-based model. Supported moods:
- `happy`: Joy, contentment, satisfaction
- `sad`: Sadness, grief, melancholy
- `angry`: Anger, frustration, irritation
- `fear`: Anxiety, worry, apprehension
- `surprise`: Astonishment, amazement
- `disgust`: Revulsion, distaste
- `neutral`: Balanced, calm state

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider implementing rate limiting based on:
- IP address
- User ID
- Endpoint-specific limits

## Media Files

Generated media files are stored in the `media/` directory:
- Audio files: `media/audio/{verse_id}.mp3`
- Images: `media/images/{verse_id}.png`

Files are served statically at `/media/` endpoint.

## Security Considerations

1. **JWT Secret**: Change the default JWT secret in production
2. **HTTPS**: Use HTTPS in production environments
3. **Input Validation**: All inputs are validated using Pydantic
4. **SQL Injection**: Protected by SQLModel/SQLAlchemy ORM
5. **CORS**: Configure CORS origins properly for production

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database_init.py

# Start server
uvicorn main:app --reload --port 8000
```

### Testing
```bash
# Run API tests
python test_api.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For API support and questions, please refer to the main README.md or open an issue on the project repository.
