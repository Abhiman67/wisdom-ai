"use client"
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { ThemeToggle } from '@/components/theme-toggle'
import { HealthIndicator } from '@/components/health-indicator'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'

const nav = [
  { href: '/dashboard', label: 'Home' },
  { href: '/daily-verse', label: 'Daily verse' },
  { href: '/chat', label: 'Chat' },
  { href: '/saved', label: 'Saved' },
  { href: '/profile', label: 'Profile' },
  // Avoid prefetching the heavy Admin page (Recharts) on every route
  { href: '/admin', label: 'Admin', prefetch: false as const }
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [isAdmin, setIsAdmin] = useState<boolean>(false)

  useEffect(() => {
    let mounted = true
    fetch('/api/is-admin', { cache: 'no-store' })
      .then(r => r.json())
      .then(d => { if (mounted) setIsAdmin(Boolean(d?.isAdmin)) })
      .catch(() => {})
    return () => { mounted = false }
  }, [])

  const logout = async () => {
    try { await apiClient.post('/logout', {}) } catch {}
    router.push('/welcome')
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background/70 backdrop-blur supports-[backdrop-filter]:bg-background/50">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/10 to-transparent" />
        <div className="container flex h-16 items-center justify-between gap-4">
          <Link href="/dashboard" className="bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text font-semibold tracking-tight text-transparent">
            Wisdom AI
          </Link>
          <nav className="hidden gap-1 md:flex">
            {nav
              .filter(i => i.href !== '/admin' || isAdmin)
              .map(i => (
              <Link
                key={i.href}
                href={i.href}
                prefetch={(i as any).prefetch ?? true}
                className={`rounded-md px-3 py-1.5 text-sm transition-colors ${pathname?.startsWith(i.href) ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              >
                {i.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            {process.env.NODE_ENV === 'development' && <HealthIndicator />}
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t">
        <div className="container py-6 text-center text-sm text-muted-foreground">© {new Date().getFullYear()} Wisdom AI</div>
      </footer>
    </div>
  )
}
