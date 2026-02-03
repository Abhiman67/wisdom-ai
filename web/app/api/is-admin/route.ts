import { cookies } from 'next/headers'

export async function GET() {
  try {
    const token = cookies().get('token')?.value
    if (!token) return Response.json({ isAdmin: false }, { status: 200 })
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const res = await fetch(`${apiBase}/admin/analytics`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store'
    })
    if (res.status === 200) return Response.json({ isAdmin: true })
    if (res.status === 401 || res.status === 403) return Response.json({ isAdmin: false })
    // Unknown upstream response; default to non-admin for safety
    return Response.json({ isAdmin: false })
  } catch {
    return Response.json({ isAdmin: false })
  }
}
