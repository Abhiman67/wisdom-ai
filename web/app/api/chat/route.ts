import { generateChatResponse, ChatMessage } from '@/lib/gemini'
import { cookies } from 'next/headers'

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { message, history = [] } = body

    if (!message || typeof message !== 'string') {
      return Response.json({ error: 'Message is required' }, { status: 400 })
    }

    // Check for API key
    if (!process.env.GEMINI_API_KEY) {
      return Response.json({ 
        error: 'Gemini API key not configured',
        response: "I'm currently unable to connect to my wisdom source. Please try again later."
      }, { status: 500 })
    }

    // Generate response using Gemini
    const result = await generateChatResponse(message, history as ChatMessage[])

    return Response.json({
      response: result.response,
      mood: result.mood,
      verses: result.verses,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return Response.json({ 
      error: 'Failed to generate response',
      response: "I apologize, but I'm having trouble connecting right now. Please try again in a moment."
    }, { status: 500 })
  }
}
