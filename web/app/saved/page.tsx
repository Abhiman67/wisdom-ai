import { cookies } from 'next/headers'
import { VerseCard } from '@/components/verse-card'
import { SavedVersesResponse, SavedVerse } from '@/types/api'
import { Sidebar } from '@/components/shell/sidebar'
import dynamic from 'next/dynamic'
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })

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
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex flex-1 flex-col min-w-0 relative">
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        {/* Content Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 md:py-8 relative z-10">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-black mb-2 bg-gradient-to-r from-white via-orange-200 to-white bg-clip-text text-transparent">Saved Verses</h1>
              <p className="text-sm text-white/60">Your collection of spiritual wisdom</p>
            </div>

            {!data && (
              <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-6 backdrop-blur-xl shadow-xl">
                <p className="text-center text-white/80">Failed to load saved verses. Please try again later.</p>
              </div>
            )}
            
            {data && data.saved_verses.length === 0 && (
              <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/70 to-[#1f1f35]/60 p-12 text-center backdrop-blur-xl shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="mb-4 mx-auto h-20 w-20 rounded-2xl bg-orange-500/10 flex items-center justify-center">
                  <BookmarkIcon className="h-10 w-10 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">No saved verses yet</h3>
                <p className="text-sm text-white/60 max-w-md mx-auto">Save your favorite verses from the daily verse or chat to build your personal collection of wisdom.</p>
              </div>
            )}
            
            {data && data.saved_verses.length > 0 && (
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {data.saved_verses.map((v: SavedVerse, idx: number) => (
                  <div key={v.verse_id} className="animate-in fade-in slide-in-from-bottom-2" style={{animationDelay: `${idx * 50}ms`}}>
                    <VerseCard
                      verseId={v.verse_id}
                      text={v.text}
                      source={v.source}
                      imageUrl={v.image_url}
                      audioUrl={v.audio_url}
                      isSaved
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
