import { generateDailyVerse } from '@/lib/gemini'
import { cookies } from 'next/headers'

// Cache the daily verse for 24 hours
let cachedVerse: { data: any; timestamp: number } | null = null
const CACHE_DURATION = 24 * 60 * 60 * 1000 // 24 hours

export async function GET() {
  try {
    const now = Date.now()
    
    // Check if we have a valid cached verse
    if (cachedVerse && (now - cachedVerse.timestamp) < CACHE_DURATION) {
      return Response.json(cachedVerse.data)
    }

    // Generate new verse using Gemini
    const verse = await generateDailyVerse()
    
    const responseData = {
      id: `verse-${Date.now()}`,
      text: verse.text,
      source: verse.source,
      reflection: verse.reflection,
      is_saved: false,
      generated_at: new Date().toISOString()
    }

    // Cache the verse
    cachedVerse = { data: responseData, timestamp: now }

    return Response.json(responseData)
  } catch (error) {
    console.error('Daily verse error:', error)
    
    // Return a fallback verse
    return Response.json({
      id: 'fallback-verse',
      text: "Be still, and know that I am God.",
      source: "Psalms 46:10",
      reflection: "In moments of chaos and uncertainty, we are reminded to pause, breathe, and connect with the divine presence.",
      is_saved: false,
      generated_at: new Date().toISOString()
    })
  }
}
