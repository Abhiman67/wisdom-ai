import { cookies } from 'next/headers'

export async function POST(req: Request) {
  // Mock Login: Accept any input
  const body = await req.json()

  // Create dummy token
  const payload = JSON.stringify({ email: body.email })
  const token = Buffer.from(payload).toString('base64')

  // Set auth cookie
  cookies().set('token', `mock_token_${token}`, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 24 * 7
  })

  return Response.json({ success: true, message: "Logged in (Mock Mode)" })
}
