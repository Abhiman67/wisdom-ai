import { cookies } from 'next/headers'

export async function GET() {
  const token = cookies().get('token')?.value
  // Authentication disabled - allow access without token
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const headers: HeadersInit = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${apiBase}/daily-verse-with-save`, {
    headers
  })
  const data = await res.json().catch(() => ({}))
  return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
}
