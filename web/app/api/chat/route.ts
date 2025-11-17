import { cookies } from 'next/headers'

export async function POST(req: Request) {
  const token = cookies().get('token')?.value
  // Authentication disabled - allow access without token
  const body = await req.json()
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${apiBase}/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  })
  const data = await res.json().catch(() => ({}))
  return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
}
