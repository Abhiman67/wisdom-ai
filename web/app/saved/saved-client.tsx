'use client'
import { useState } from 'react'
import { VerseCard } from '@/components/verse-card'
import { SavedVersesResponse, SavedVerse } from '@/types/api'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import dynamic from 'next/dynamic'
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })
const RefreshCw = dynamic(() => import('lucide-react').then(m => m.RefreshCw), { ssr: false })
const AlertCircle = dynamic(() => import('lucide-react').then(m => m.AlertCircle), { ssr: false })

export default function SavedVersesClient({ 
  initialData, 
  initialError 
}: { 
  initialData: SavedVersesResponse | null
  initialError: string | null
}) {
  const [data, setData] = useState<SavedVersesResponse | null>(initialData)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(initialError)

  const retry = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<SavedVersesResponse>('/my-saved-verses')
      setData(result)
    } catch (e) {
      console.error('Retry failed:', e)
      setError(e instanceof Error ? e.message : 'Failed to load saved verses')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />

      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 md:py-8 relative z-10">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl md:text-4xl font-black mb-2 bg-gradient-to-r from-white via-orange-200 to-white bg-clip-text text-transparent">Saved Verses</h1>
                <p className="text-sm text-white/60">Your collection of spiritual wisdom</p>
              </div>
              {data && (
                <button
                  onClick={retry}
                  disabled={loading}
                  className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-2 text-xs font-medium text-white/80 backdrop-blur hover:bg-white/10 hover:border-white/30 transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Refresh saved verses"
                >
                  <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
              )}
            </div>

            {loading && !data ? (
              <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-xl shadow-2xl p-12 animate-pulse">
                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-64 bg-white/10 rounded-xl"></div>
                  ))}
                </div>
              </div>
            ) : error ? (
              <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-8 backdrop-blur-xl shadow-xl">
                <div className="text-center">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-500/20 mb-4">
                    <AlertCircle className="h-8 w-8 text-red-400" />
                  </div>
                  <p className="text-lg text-white/80 mb-6">{error}</p>
                  <button
                    onClick={retry}
                    className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:shadow-orange-500/50 hover:scale-105 transition-all"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Try Again
                  </button>
                </div>
              </div>
            ) : !data ? (
              <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-12 text-center backdrop-blur-xl shadow-xl">
                <p className="text-white/60">No data available</p>
              </div>
            ) : data.saved_verses.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/70 to-[#1f1f35]/60 p-12 text-center backdrop-blur-xl shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="mb-4 mx-auto h-20 w-20 rounded-2xl bg-orange-500/10 flex items-center justify-center">
                  <BookmarkIcon className="h-10 w-10 text-orange-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">No saved verses yet</h3>
                <p className="text-sm text-white/60 max-w-md mx-auto">Save your favorite verses from the daily verse or chat to build your personal collection of wisdom.</p>
              </div>
            ) : (
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
