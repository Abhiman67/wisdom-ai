export async function GET() {
  try {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const res = await fetch(`${apiBase}/health`)
    const text = await res.text().catch(() => '')
    return new Response(text || 'ok', { status: res.status, headers: { 'Content-Type': 'text/plain' } })
  } catch (e) {
    return new Response('unreachable', { status: 502, headers: { 'Content-Type': 'text/plain' } })
  }
}
