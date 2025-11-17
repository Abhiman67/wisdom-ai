import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PROTECTED_PREFIXES = ['/daily-verse', '/chat', '/saved', '/profile', '/admin', '/dashboard', '/collections', '/reading-plans', '/notifications']
const PUBLIC_PATHS = ['/welcome', '/login', '/signup', '/forgot-password', '/api']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  
  // Allow public paths
  if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }
  
  // Check if path needs protection
  const needsAuth = PROTECTED_PREFIXES.some(prefix => pathname.startsWith(prefix))
  
  if (needsAuth) {
    const token = req.cookies.get('token')?.value
    
    if (!token) {
      // Redirect to login with return URL
      const url = req.nextUrl.clone()
      url.pathname = '/login'
      url.searchParams.set('from', pathname)
      return NextResponse.redirect(url)
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next|icons|public|sw\.js|workbox-.*|manifest\.json|api/health).*)']
}
