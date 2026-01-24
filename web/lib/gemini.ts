import { GoogleGenerativeAI } from '@google/generative-ai'

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '')

// System prompt that makes Gemini act as a spiritual wisdom AI
const SYSTEM_PROMPT = `You are "Wisdom AI", a deeply knowledgeable and compassionate spiritual guide. You have expertise in major world scriptures including:

- The Bhagavad Gita (Hindu scripture)
- The Holy Bible (Christian scripture - King James Version)  
- The Holy Quran (Islamic scripture)

Your role is to:
1. Provide relevant verses and wisdom from these sacred texts based on the user's questions or emotional state
2. Offer compassionate, non-judgmental guidance
3. Help users find peace, understanding, and spiritual growth
4. Detect the user's mood/emotional state and respond appropriately
5. Quote actual verses accurately with proper citations (Book, Chapter:Verse)

Guidelines:
- Be warm, empathetic, and supportive
- Never push one religion over another - respect all paths
- If someone is in crisis, encourage professional help while offering comfort
- Keep responses focused and meaningful (not too long)
- Include 1-2 relevant scripture quotes per response when appropriate
- Format verses beautifully with proper attribution

When quoting verses, use this format:
"[Verse text here]"
— [Source, Chapter:Verse]

Remember: You are a bridge between ancient wisdom and modern seekers. Speak with reverence but also relatability.`

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function generateChatResponse(
  message: string,
  history: ChatMessage[] = []
): Promise<{ response: string; mood?: string; verses?: any[] }> {
  try {
    const model = genAI.getGenerativeModel({ 
      model: 'gemini-2.0-flash',
      generationConfig: {
        temperature: 0.7,
        topP: 0.9,
        maxOutputTokens: 1024,
      }
    })

    // Build conversation history for context
    const historyFormatted = history.map(msg => ({
      role: msg.role === 'user' ? 'user' : 'model',
      parts: [{ text: msg.content }]
    }))

    const chat = model.startChat({
      history: [
        { role: 'user', parts: [{ text: 'Please act according to these instructions: ' + SYSTEM_PROMPT }] },
        { role: 'model', parts: [{ text: 'I understand. I am Wisdom AI, a compassionate spiritual guide with deep knowledge of the Bhagavad Gita, Holy Bible, and Holy Quran. I will provide relevant verses and wisdom while respecting all spiritual paths. How may I help you on your journey today?' }] },
        ...historyFormatted
      ],
    })

    const result = await chat.sendMessage(message)
    const response = result.response.text()

    // Simple mood detection based on user message
    const mood = detectMood(message)

    return {
      response,
      mood,
      verses: extractVerses(response)
    }
  } catch (error) {
    console.error('Gemini API error:', error)
    throw new Error('Failed to generate response')
  }
}

function detectMood(text: string): string {
  const lowerText = text.toLowerCase()
  
  if (/sad|depressed|down|unhappy|crying|tears|lonely|alone|hopeless/.test(lowerText)) {
    return 'sad'
  }
  if (/anxious|worried|stressed|nervous|fear|scared|panic|overwhelmed/.test(lowerText)) {
    return 'anxious'
  }
  if (/angry|mad|furious|frustrated|annoyed|irritated|rage/.test(lowerText)) {
    return 'angry'
  }
  if (/happy|joy|grateful|blessed|thankful|excited|wonderful|amazing/.test(lowerText)) {
    return 'joyful'
  }
  if (/confused|lost|uncertain|don't know|unsure|guidance|direction/.test(lowerText)) {
    return 'seeking'
  }
  if (/peace|calm|serene|meditat|quiet|stillness/.test(lowerText)) {
    return 'peaceful'
  }
  
  return 'neutral'
}

function extractVerses(response: string): any[] {
  // Extract quoted verses from the response
  const versePattern = /"([^"]+)"\s*—\s*([^"\n]+)/g
  const verses: any[] = []
  let match

  while ((match = versePattern.exec(response)) !== null) {
    verses.push({
      text: match[1],
      source: match[2].trim()
    })
  }

  return verses
}

// For daily verse generation
export async function generateDailyVerse(): Promise<{ text: string; source: string; reflection: string }> {
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' })

    const prompt = `Generate an inspiring verse of the day from one of these sacred texts: Bhagavad Gita, Holy Bible (KJV), or Holy Quran.

Respond in this exact JSON format only (no markdown, no code blocks):
{
  "text": "The exact verse text here",
  "source": "Book Chapter:Verse (e.g., 'Bhagavad Gita 2:47' or 'Psalms 23:1' or 'Quran 2:286')",
  "reflection": "A brief 2-3 sentence reflection on how this verse applies to daily life"
}

Choose a different verse each time, focusing on themes like: hope, courage, peace, love, wisdom, patience, faith, gratitude, or perseverance.`

    const result = await model.generateContent(prompt)
    const responseText = result.response.text()
    
    // Parse JSON from response
    const jsonMatch = responseText.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0])
    }
    
    // Fallback
    return {
      text: "Be still, and know that I am God.",
      source: "Psalms 46:10",
      reflection: "In moments of chaos and uncertainty, we are reminded to pause, breathe, and connect with the divine presence that surrounds us."
    }
  } catch (error) {
    console.error('Error generating daily verse:', error)
    return {
      text: "Be still, and know that I am God.",
      source: "Psalms 46:10", 
      reflection: "In moments of chaos and uncertainty, we are reminded to pause, breathe, and connect with the divine presence that surrounds us."
    }
  }
}
