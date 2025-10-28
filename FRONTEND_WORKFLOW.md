# God AI Frontend Workflow Guide

## Manual Save Daily Verse Experience

This guide shows how to implement the frontend for a daily verse experience where users manually save verses they like.

## Daily Verse Page Implementation

### 1. Page Load - Daily Verse Display

```javascript
// Frontend: Daily Verse Page Component
const DailyVersePage = () => {
  const [dailyVerse, setDailyVerse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Automatically load daily verse when page opens
    loadDailyVerse();
  }, []);

  const loadDailyVerse = async () => {
    try {
      setLoading(true);
      
      // Use the endpoint that shows save status
      const response = await fetch('/api/daily-verse-with-save', {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      setDailyVerse({
        verseId: data.verse_id,
        text: data.text,
        source: data.source,
        audioUrl: data.audio_url,
        imageUrl: data.image_url,
        isSaved: data.is_saved,
        message: data.message
      });
      
    } catch (error) {
      console.error('Error loading daily verse:', error);
      showNotification('Failed to load daily verse', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="daily-verse-page">
      {loading ? (
        <div className="loading-spinner">Loading your daily verse...</div>
      ) : (
        <div className="verse-container">
          <img src={dailyVerse.imageUrl} alt="Daily Verse" className="verse-image" />
          <div className="verse-text">{dailyVerse.text}</div>
          <div className="verse-source">— {dailyVerse.source}</div>
          
          <audio controls src={dailyVerse.audioUrl} className="verse-audio">
            Your browser does not support the audio element.
          </audio>
          
          <div className="verse-actions">
            <button 
              className={`save-button ${dailyVerse.isSaved ? 'saved' : ''}`}
              onClick={handleSaveVerse}
              disabled={dailyVerse.isSaved || saving}
            >
              {saving ? 'Saving...' : 
               dailyVerse.isSaved ? '✓ Saved to Favorites' : 'Save to Favorites'}
            </button>
            
            <button className="share-button" onClick={handleShareVerse}>
              Share Verse
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 2. Save Button (Manual Save Only)

```javascript
const handleSaveVerse = async () => {
  try {
    setSaving(true);
    
    // Save the current daily verse
    const response = await fetch('/api/save-verse-from-daily', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      showNotification(data.message, 'success');
      // Update UI to show verse is saved
      setDailyVerse(prev => ({ ...prev, isSaved: true }));
    } else {
      showNotification(data.message, 'info');
    }
    
  } catch (error) {
    console.error('Error saving verse:', error);
    showNotification('Failed to save verse', 'error');
  } finally {
    setSaving(false);
  }
};
```

### 3. Saved Verses Page

```javascript
const SavedVersesPage = () => {
  const [savedVerses, setSavedVerses] = useState([]);

  useEffect(() => {
    loadSavedVerses();
  }, []);

  const loadSavedVerses = async () => {
    try {
      const response = await fetch('/api/my-saved-verses', {
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      });
      
      const data = await response.json();
      setSavedVerses(data.saved_verses);
      
    } catch (error) {
      console.error('Error loading saved verses:', error);
    }
  };

  return (
    <div className="saved-verses-page">
      <h2>My Saved Verses</h2>
      <div className="verses-grid">
        {savedVerses.map(verse => (
          <div key={verse.verse_id} className="verse-card">
            <img src={verse.image_url} alt={verse.verse_id} />
            <div className="verse-content">
              <p className="verse-text">{verse.text}</p>
              <p className="verse-source">— {verse.source}</p>
            </div>
            <audio controls src={verse.audio_url} className="verse-audio" />
          </div>
        ))}
      </div>
    </div>
  );
};
```

## API Endpoint Usage

### For Daily Verse Page (Recommended)
```javascript
// Use this endpoint for the daily verse page
GET /api/daily-verse-with-save

// Benefits:
// - Loads personalized verse
// - Shows save status (is_saved: true/false)
// - Generates audio/image if needed
// - User controls which verses to save
```

### For Chat Interface
```javascript
// Use this endpoint for chat interactions
POST /api/chat
{
  "message": "User's message here"
}

// The chat endpoint handles mood detection and verse recommendations
// Users can save verses from chat using the save button
```

### For Manual Verse Saving
```javascript
// Use this endpoint when user clicks save button
POST /api/save-verse-from-daily

// Or for specific verses:
POST /api/save-verse
{
  "verse_id": "Gita_2.47"
}
```

## User Experience Flow

### 1. Daily Verse Page (Main Experience)
```
User opens app → Daily Verse Page loads automatically → 
Verse displays with audio/image → User reads/listens to verse → 
User decides if they want to save it → User clicks "Save" button → 
Verse is saved to favorites (only if user chooses)
```

### 2. Chat Experience
```
User types message → AI responds with relevant verse → 
User can save the verse if they like it → 
User continues conversation
```

### 3. Saved Verses Page
```
User navigates to Saved Verses → Only manually saved verses display → 
User can browse, listen to audio, view images
```

## Frontend Benefits

✅ **User Control**: Users decide which verses to save  
✅ **Manual Saving**: Only save verses that resonate with users  
✅ **Rich Media**: Audio and images generated automatically  
✅ **Personalization**: Verses based on user's mood and history  
✅ **No Repetition**: System avoids showing recent verses  
✅ **Easy Access**: All saved verses in one place  

## Backend Endpoints Summary

| Endpoint | Purpose | Auto-Save | Use Case |
|----------|---------|-----------|----------|
| `GET /daily-verse-with-save` | Daily verse page | ❌ No | Main daily verse experience |
| `GET /daily-verse` | Basic daily verse | ❌ No | If you want manual control |
| `POST /chat` | Chat interaction | ❌ No | Conversational AI |
| `POST /save-verse-from-daily` | Manual save | ✅ Yes | When user clicks save button |
| `GET /my-saved-verses` | View saved | ❌ N/A | Saved verses page |

## Implementation Notes

1. **Use `/daily-verse-with-save`** for your main daily verse page
2. **User clicks save button** to save verses they like
3. **Automatic personalization** based on user mood
4. **Rich media generation** happens automatically
5. **User-controlled experience** - only save meaningful verses

This workflow ensures users have full control over their saved verses collection!
