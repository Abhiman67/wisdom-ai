import { NextRequest } from 'next/server'

/**
 * Chat History API Route
 * 
 * GET /api/chat-history - Returns recent chat queries
 * GET /api/chat-history?chatId=X - Returns a specific chat by ID
 * 
 * Uses query params instead of dynamic routes [id] to avoid:
 * - params Promise issues in Next.js 14+
 * - VS Code browser adding extra query params
 * - Silent failures
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const chatId = searchParams.get('chatId')
    const limit = searchParams.get('limit') || '10'
    
    console.log('[chat-history] Request received, chatId:', chatId, 'limit:', limit)
    
    let endpoint: string
    
    if (chatId) {
      // Fetch specific chat by ID
      endpoint = `${API_BASE}/admin/db/queries/${chatId}`
      console.log('[chat-history] Fetching single chat from:', endpoint)
    } else {
      // Fetch recent chats list
      endpoint = `${API_BASE}/admin/db/queries?limit=${limit}`
      console.log('[chat-history] Fetching recent chats from:', endpoint)
    }
    
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't cache - we want fresh data
      cache: 'no-store',
    })
    
    if (!response.ok) {
      console.error('[chat-history] Backend error:', response.status, response.statusText)
      return new Response(
        JSON.stringify({ 
          error: 'Failed to fetch chat history',
          status: response.status,
          statusText: response.statusText
        }),
        { 
          status: response.status,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }
    
    const data = await response.json()
    console.log('[chat-history] Successfully fetched data, items:', Array.isArray(data) ? data.length : 1)
    
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    console.error('[chat-history] Error:', error)
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}
