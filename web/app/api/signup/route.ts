import { cookies } from 'next/headers'

export async function POST(req: Request) {
  const body = await req.json()
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const res = await fetch(`${apiBase}/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    return new Response(typeof data === 'string' ? data : JSON.stringify(data), { status: res.status })
  }
  const token = data.access_token || data.token
  if (token) {
    cookies().set('token', token, {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      maxAge: 60 * 60 * 24 * 7
    })
  }
  return Response.json({ success: true })
}
