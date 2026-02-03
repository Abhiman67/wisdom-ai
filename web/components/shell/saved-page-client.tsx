"use client"
import { Sidebar } from '@/components/shell/sidebar'
import { VerseCard } from '@/components/verse-card'
import { SavedVerse } from '@/types/api'
import dynamic from 'next/dynamic'
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })

export function SavedPageClient({ verses, userName, userEmail }: { verses: SavedVerse[], userName?: string, userEmail?: string }) {
  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar userName={userName} userEmail={userEmail} />
      
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">Saved Verses</h1>
              <p className="text-white/60 mt-2">Your collection of meaningful verses</p>
            </div>

            {verses.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="h-20 w-20 rounded-full bg-white/5 flex items-center justify-center mb-4">
                  <BookmarkIcon className="h-10 w-10 text-white/30" />
                </div>
                <h2 className="text-xl font-semibold text-white/80 mb-2">No saved verses yet</h2>
                <p className="text-white/50 max-w-md">Start saving verses from your daily verses to build your personal collection</p>
              </div>
            ) : (
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {verses.map((verse, idx) => (
                  <div
                    key={verse.verse_id}
                    className="animate-in fade-in slide-in-from-bottom-4 duration-500"
                    style={{ animationDelay: `${idx * 50}ms` }}
                  >
                    <VerseCard
                      verseId={verse.verse_id}
                      text={verse.text}
                      source={verse.source}
                      imageUrl={verse.image_url}
                      audioUrl={verse.audio_url}
                      isSaved={true}
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
