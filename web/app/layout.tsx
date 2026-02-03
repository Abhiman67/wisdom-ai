import './globals.css'
import { ReactQueryProvider } from '@/components/providers/react-query-provider'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { ErrorBoundary } from '@/components/error-boundary'
import { Toaster } from 'sonner'
import type { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
  // Used by Next to resolve relative URLs in metadata (OG/Twitter images)
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: 'Wisdom AI',
  description: 'Spiritual companion with mood-aware verses and gentle guidance.',
  manifest: '/manifest.json',
  icons: [
    { rel: 'icon', url: '/icons/icon-192x192.png' },
    { rel: 'apple-touch-icon', url: '/icons/icon-192x192.png' }
  ],
  openGraph: {
    type: 'website',
    title: 'Wisdom AI — Gentle guidance and contextual verses',
    description: 'Ask Wisdom AI for thoughtful, verse-backed guidance. Daily verses, personal reflections, and a calming conversational assistant.',
    images: [{ url: '/images/og-landing.svg' }]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Wisdom AI — Gentle guidance and contextual verses',
    description: 'Ask Wisdom AI for thoughtful, verse-backed guidance. Daily verses, personal reflections, and a calming conversational assistant.',
    images: ['/images/og-landing.svg']
  }
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#7C3AED' },
    { media: '(prefers-color-scheme: dark)', color: '#8B5CF6' }
  ]
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ErrorBoundary>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            <ReactQueryProvider>
              {children}
              <Toaster richColors theme="system" />
            </ReactQueryProvider>
          </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
