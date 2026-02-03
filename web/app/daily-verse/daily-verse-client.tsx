"use client"
import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { DailyVerseResponse } from '@/types/api'
import { Sidebar } from '@/components/shell/sidebar'
import { Sparkles, Heart, Share2, BookOpen, Calendar, Sunrise, RefreshCw, AlertCircle, Copy, Check } from 'lucide-react'
import Image from 'next/image'

export default function DailyVerseClient({ initialData }: { initialData: DailyVerseResponse | null }) {
  const [data, setData] = useState<DailyVerseResponse | null>(initialData)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(initialData ? null : 'Failed to load daily verse')
  const [copied, setCopied] = useState(false)

  const canShare = typeof navigator !== "undefined" && typeof (navigator as any).share === "function"

  const onSave = async () => {
    if (!data || (data as any).is_saved) return
    try {
      setSaving(true)
      const res = await apiClient.post('/save-verse-from-daily', {})
      if (res?.ok !== false) {
        setData({ ...data, is_saved: true } as any)
      }
    } catch (e) {
      console.error('Save failed:', e)
    } finally {
      setSaving(false)
    }
  }

  const onRefresh = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.get<DailyVerseResponse>('/daily-verse-with-save')
      setData(res)
    } catch (e) {
      console.error('Refresh failed:', e)
      setError('Failed to load verse. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleShare = async () => {
    if (!data) return
    const shareText = `"${data.text}" — ${data.source}`
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Daily Verse from Wisdom AI',
          text: shareText,
        })
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          console.error('Share failed:', err)
        }
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(shareText)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Copy failed:', err)
      }
    }
  }

  const currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36] text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex flex-1 flex-col min-w-0 relative">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 h-96 w-96 rounded-full bg-orange-500/10 blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-purple-500/10 blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-pink-500/5 blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>
        
        {/* Content Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 md:py-10 relative z-10">
          <div className="max-w-4xl mx-auto">
            {/* Header Section */}
            <div className="mb-10 text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-orange-400/30 bg-orange-400/10 px-4 py-2 mb-6 backdrop-blur-sm">
                <Sunrise className="h-4 w-4 text-orange-400 animate-pulse" />
                <span className="text-xs font-semibold uppercase tracking-widest text-orange-200">Today’s Inspiration</span>
              </div>
              
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-3 bg-gradient-to-r from-white via-orange-100 to-pink-100 bg-clip-text text-transparent leading-tight">
                Daily Verse
              </h1>
              
              <div className="flex items-center justify-center gap-2 text-white/60">
                <Calendar className="h-4 w-4" />
                <p className="text-sm">{currentDate}</p>
              </div>
              
              {data && (
                <button
                  onClick={onRefresh}
                  disabled={loading}
                  className="mt-4 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-2 text-xs font-medium text-white/80 backdrop-blur hover:bg-white/10 hover:border-white/30 transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Get a new daily verse"
                >
                  <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
              )}
            </div>

            {loading ? (
              <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-xl shadow-2xl p-8 md:p-10 animate-pulse">
                <div className="space-y-6">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-white/10"></div>
                    <div className="h-px flex-1 bg-white/10"></div>
                  </div>
                  <div className="space-y-3">
                    <div className="h-8 bg-white/10 rounded w-3/4"></div>
                    <div className="h-8 bg-white/10 rounded w-full"></div>
                    <div className="h-8 bg-white/10 rounded w-5/6"></div>
                  </div>
                  <div className="flex items-center justify-between pt-6 border-t border-white/10">
                    <div className="h-10 bg-white/10 rounded w-32"></div>
                    <div className="flex gap-2">
                      <div className="h-10 w-24 bg-white/10 rounded-full"></div>
                      <div className="h-10 w-24 bg-white/10 rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : error ? (
              <div className="rounded-3xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-8 backdrop-blur-xl shadow-2xl">
                <div className="text-center">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-500/20 mb-4">
                    <AlertCircle className="h-8 w-8 text-red-400" />
                  </div>
                  <p className="text-lg text-white/80 mb-6">{error}</p>
                  <button
                    onClick={onRefresh}
                    className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:shadow-orange-500/50 hover:scale-105 transition-all"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Try Again
                  </button>
                </div>
              </div>
            ) : !data ? (
              <div className="rounded-3xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-8 backdrop-blur-xl shadow-2xl">
                <div className="text-center">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-500/20 mb-4">
                    <BookOpen className="h-8 w-8 text-red-400" />
                  </div>
                  <p className="text-lg text-white/80">Failed to load daily verse. Please try again later.</p>
                </div>
              </div>
            ) : (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
                {/* Main Verse Card */}
                <div className="relative group">
                  {/* Glow effect */}
                  <div className="absolute -inset-1 bg-gradient-to-r from-orange-500/50 via-pink-500/50 to-purple-500/50 rounded-3xl blur-2xl opacity-20 group-hover:opacity-30 transition duration-1000"></div>
                  
                  <div className="relative rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-xl shadow-2xl overflow-hidden">
                    {/* Image Section */}
                    {data.image_url && (
                      <div className="relative h-64 md:h-80 overflow-hidden">
                        <Image 
                          src={data.image_url} 
                          alt="Daily verse illustration" 
                          fill 
                          className="object-cover"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                          priority
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0d1025] via-[#0d1025]/60 to-transparent"></div>
                        
                        {/* Decorative corner elements */}
                        <div className="absolute top-6 left-6 h-16 w-16 rounded-full bg-orange-500/20 blur-xl"></div>
                        <div className="absolute bottom-6 right-6 h-20 w-20 rounded-full bg-purple-500/20 blur-xl"></div>
                      </div>
                    )}
                    
                    {/* Content Section */}
                    <div className="p-8 md:p-10 space-y-8">
                      {/* Decorative Quote Icon */}
                      <div className="flex items-center gap-4">
                        <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500/20 to-pink-500/20 border border-orange-400/30">
                          <Sparkles className="h-6 w-6 text-orange-400" />
                        </div>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/20 to-transparent"></div>
                      </div>
                      
                      {/* Verse Text */}
                      <div className="relative">
                        <div className="absolute -left-4 -top-2 text-6xl text-orange-500/20 font-serif">&ldquo;</div>
                        <blockquote className="text-xl md:text-2xl lg:text-3xl font-light leading-relaxed text-white/90 italic relative z-10 pl-4">
                          {data.text}
                        </blockquote>
                        <div className="absolute -right-4 -bottom-2 text-6xl text-orange-500/20 font-serif">&rdquo;</div>
                      </div>
                      
                      {/* Source Attribution */}
                      <div className="flex items-center justify-between pt-6 border-t border-white/10">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-1 bg-gradient-to-b from-orange-500 to-pink-500 rounded-full"></div>
                          <div>
                            <div className="text-xs text-white/50 uppercase tracking-wider mb-1">Source</div>
                            <div className="text-base font-semibold text-white/90">{data.source}</div>
                          </div>
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={onSave}
                            disabled={(data as any).is_saved || saving}
                            className={`group/btn inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-all disabled:cursor-not-allowed ${
                              (data as any).is_saved
                                ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                                : 'bg-orange-500 hover:bg-orange-400 text-white shadow-lg hover:shadow-orange-500/50 hover:scale-105 border border-orange-400/30 disabled:opacity-50 disabled:hover:scale-100'
                            }`}
                            aria-label={(data as any).is_saved ? 'Verse saved' : 'Save verse'}
                          >
                            <Heart className={`h-4 w-4 ${(data as any).is_saved ? 'fill-green-300' : 'group-hover/btn:fill-white'} transition`} />
                            {saving ? 'Saving…' : (data as any).is_saved ? 'Saved' : 'Save'}
                          </button>
                          
                          <button
                            onClick={handleShare}
                            className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-5 py-2.5 text-sm font-medium text-white/90 backdrop-blur hover:bg-white/10 hover:border-white/30 transition-all hover:scale-105"
                            aria-label="Share this verse"
                          >
                            {copied ? <Check className="h-4 w-4" /> : canShare ? <Share2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                            {copied ? 'Copied!' : 'Share'}
                          </button>
                        </div>
                      </div>
                      
                      {/* Audio Player */}
                      {data.audio_url && (
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/20">
                              <BookOpen className="h-4 w-4 text-purple-400" />
                            </div>
                            <span className="text-sm font-medium text-white/80">Listen to this verse</span>
                          </div>
                          <audio controls src={data.audio_url} className="w-full" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Reflection Prompt */}
                <div className="mt-8 rounded-2xl border border-white/10 bg-gradient-to-br from-purple-500/10 to-pink-500/10 p-6 backdrop-blur-sm">
                  <div className="flex items-start gap-4">
                    <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 flex-shrink-0">
                      <Sparkles className="h-5 w-5 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white/90 mb-2">Reflection Prompt</h3>
                      <p className="text-sm text-white/70 leading-relaxed">
                        Take a moment to meditate on these words. How does this verse speak to your current journey? 
                        What wisdom can you carry with you today?
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
