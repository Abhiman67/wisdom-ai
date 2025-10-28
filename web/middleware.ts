import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PROTECTED_PREFIXES = ['/daily-verse', '/chat', '/saved', '/profile', '/admin']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  const token = req.cookies.get('token')?.value

  const isProtected = PROTECTED_PREFIXES.some(p => pathname.startsWith(p))
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/signup')

  if (isProtected && !token) {
    const url = new URL('/login', req.url)
    url.searchParams.set('next', pathname)
    return NextResponse.redirect(url)
  }
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/daily-verse', req.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next|icons|public|sw\.js|workbox-.*|manifest\.json|api/health).*)']
}
