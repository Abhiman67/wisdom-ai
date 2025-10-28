import { cookies } from 'next/headers'

export async function POST(req: Request) {
  const raw = await req.json()
  const { email, password, remember } = raw || {}
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  const res = await fetch(`${apiBase}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
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
      ...(remember ? { maxAge: 60 * 60 * 24 * 7 } : {}) // 7 days if remember, else session cookie
    })
  }
  return Response.json({ success: true })
}
