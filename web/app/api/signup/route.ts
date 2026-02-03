import { cookies } from 'next/headers'

export async function POST(req: Request) {
  // Mock Signup: Accept any input
  const body = await req.json()

  // Create a dummy token using user data (base64 encoded for simplicity)
  // In a real app, use JWT. Here we just want it to work.
  const payload = JSON.stringify({ name: body.name || "User", email: body.email })
  const token = Buffer.from(payload).toString('base64')

  // Set auth cookie
  cookies().set('token', `mock_token_${token}`, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 24 * 7 // 7 days
  })

  return Response.json({ success: true, message: "Account created (Mock Mode)" })
}
