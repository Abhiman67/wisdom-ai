import { cookies } from 'next/headers'

export async function POST() {
  const token = cookies().get('token')?.value
  // Authentication disabled - allow access without token
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${apiBase}/save-verse-from-daily`, { 
    method: 'POST', 
    headers 
  })
  const data = await res.json().catch(() => ({}))
  return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
}
