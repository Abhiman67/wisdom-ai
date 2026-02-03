import { cookies } from 'next/headers'

export async function DELETE(req: Request, { params }: { params: { id: string } }) {
  try {
    const token = cookies().get('token')?.value
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const headers: HeadersInit = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${apiBase}/admin/moderation/${params.id}/delete`, {
      method: 'DELETE',
      headers
    })
    const data = await res.json().catch(() => ({}))
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: 'Upstream error', detail: String(e?.message || e) }), { status: 502, headers: { 'Content-Type': 'application/json' } })
  }
}
