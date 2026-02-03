import { cookies } from 'next/headers'
import { VerseCard } from '@/components/verse-card'
import { SavedVersesResponse, SavedVerse } from '@/types/api'
import { Sidebar } from '@/components/shell/sidebar'
import dynamic from 'next/dynamic'
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })

import SavedVersesClient from './saved-client'

export default async function SavedPage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: SavedVersesResponse | null = null
  let error: string | null = null
  try {
    const res = await fetch(`${apiBase}/my-saved-verses`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      data = await res.json()
    } else {
      error = 'Failed to load saved verses'
    }
  } catch (e) {
    error = e instanceof Error ? e.message : 'Network error'
  }

  return <SavedVersesClient initialData={data} initialError={error} />
}
