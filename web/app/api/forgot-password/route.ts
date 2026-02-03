export async function POST(req: Request) {
  // Placeholder endpoint to avoid 404 while backend flow is pending
  // In production, integrate with an email provider and backend endpoint that issues a token
  const { email } = await req.json().catch(() => ({}))
  if (!email) return new Response(JSON.stringify({ ok: false, error: 'Email required' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
  return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } })
}
