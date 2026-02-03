import { cookies } from 'next/headers'

export async function GET(req: Request) {
  try {
    const token = cookies().get('token')?.value
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const headers: HeadersInit = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    // preserve query string (e.g., ?days=30)
    const url = new URL(req.url)
    const qs = url.search

    const res = await fetch(`${apiBase}/admin/analytics/engagement${qs}`, { headers })
    const data = await res.json().catch(() => ({}))
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: 'Upstream error', detail: String(e?.message || e) }), { status: 502, headers: { 'Content-Type': 'application/json' } })
  }
}
