import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

const PROTECTED_PREFIXES = ['/daily-verse', '/chat', '/saved', '/profile', '/admin', '/dashboard', '/collections', '/reading-plans', '/notifications']
const PUBLIC_PATHS = ['/welcome', '/login', '/signup', '/forgot-password', '/api', '/auth']

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  
  // Allow public paths
  if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }
  
  // Check if path needs protection
  const needsAuth = PROTECTED_PREFIXES.some(prefix => pathname.startsWith(prefix))
  
  if (!needsAuth) {
    return NextResponse.next()
  }

  // Create Supabase client
  let response = NextResponse.next({
    request: { headers: req.headers },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return req.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          req.cookies.set({ name, value, ...options })
          response = NextResponse.next({
            request: { headers: req.headers },
          })
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          req.cookies.set({ name, value: '', ...options })
          response = NextResponse.next({
            request: { headers: req.headers },
          })
          response.cookies.set({ name, value: '', ...options })
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    // Redirect to login with return URL
    const url = req.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('from', pathname)
    return NextResponse.redirect(url)
  }

  return response
}

export const config = {
  matcher: ['/((?!_next|icons|public|sw\.js|workbox-.*|manifest\.json|api/health).*)']
}
