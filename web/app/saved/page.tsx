import { cookies } from 'next/headers'
import { AppShell } from '@/components/shell/app-shell'
import { VerseCard } from '@/components/verse-card'
import { SavedVersesResponse, SavedVerse } from '@/types/api'

export default async function SavedPage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: SavedVersesResponse | null = null
  try {
    const res = await fetch(`${apiBase}/my-saved-verses`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      data = await res.json()
    }
  } catch (e) {
    // ignore to render fallback UI
  }

  return (
    <AppShell>
      <div className="container py-8">
        <h1 className="mb-6 text-2xl font-semibold">Saved verses</h1>
        {!data && <div className="rounded-md border p-6">Failed to load saved verses.</div>}
        {data && data.saved_verses.length === 0 && (
          <div className="rounded-md border p-8 text-center">
            <div className="mb-2 text-2xl">📖</div>
            <p className="text-sm text-muted-foreground">No saved verses yet. Save your favorites from the daily verse or chat.</p>
          </div>
        )}
        {data && data.saved_verses.length > 0 && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {data.saved_verses.map((v: SavedVerse) => (
              <VerseCard key={v.verse_id}
                verseId={v.verse_id}
                text={v.text}
                source={v.source}
                imageUrl={v.image_url}
                audioUrl={v.audio_url}
                isSaved
              />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
