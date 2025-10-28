import { cookies } from 'next/headers'

export async function GET() {
  try {
    const token = cookies().get('token')?.value
    if (!token) return new Response('Unauthorized', { status: 401 })
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const res = await fetch(`${apiBase}/admin/analytics`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await res.json().catch(() => ({}))
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: 'Upstream error', detail: String(e?.message || e) }), { status: 502, headers: { 'Content-Type': 'application/json' } })
  }
}
