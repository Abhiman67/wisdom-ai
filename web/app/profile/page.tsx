import { cookies } from 'next/headers'
import { UserProfile } from '@/types/api'
import { Sidebar } from '@/components/shell/sidebar'
import Link from 'next/link'
import dynamic from 'next/dynamic'
const UserIcon = dynamic(() => import('lucide-react').then(m => m.User), { ssr: false })
const MessageSquareIcon = dynamic(() => import('lucide-react').then(m => m.MessageSquare), { ssr: false })
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })
const FolderIcon = dynamic(() => import('lucide-react').then(m => m.Folder), { ssr: false })
const TrendingUpIcon = dynamic(() => import('lucide-react').then(m => m.TrendingUp), { ssr: false })
const AwardIcon = dynamic(() => import('lucide-react').then(m => m.Award), { ssr: false })
const CalendarIcon = dynamic(() => import('lucide-react').then(m => m.Calendar), { ssr: false })
const HeartIcon = dynamic(() => import('lucide-react').then(m => m.Heart), { ssr: false })
const SparklesIcon = dynamic(() => import('lucide-react').then(m => m.Sparkles), { ssr: false })
const BarChartIcon = dynamic(() => import('lucide-react').then(m => m.BarChart3), { ssr: false })
const SettingsIcon = dynamic(() => import('lucide-react').then(m => m.Settings), { ssr: false })
const BellIcon = dynamic(() => import('lucide-react').then(m => m.Bell), { ssr: false })
const ShieldIcon = dynamic(() => import('lucide-react').then(m => m.Shield), { ssr: false })

export default async function ProfilePage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: UserProfile | null = null
  let collections: any[] = []
  
  try {
    const res = await fetch(`${apiBase}/profile`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      data = (await res.json()) as UserProfile
    }
  } catch (e) {
    // continue to fallback UI
  }

  // Fetch collections count
  try {
    const res = await fetch(`${apiBase}/collections`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      collections = await res.json()
    }
  } catch (e) {
    // continue
  }

  // Calculate stats
  const stats = data ? {
    totalSavedVerses: data.saved_verses.length,
    totalCollections: collections.length,
    totalChats: data.chat_history.length,
    joinedDate: data.created_at ? new Date(data.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }) : 'Recently',
    streak: data.streak ?? 0,
    favoriteSource: data.favorite_source ?? (data.saved_verses.length > 0 ? 'Various Sources' : 'Not yet determined')
  } : null

  // Calculate achievements
  const achievements = data ? [
    { 
      title: 'Early Adopter', 
      description: 'Joined Wisdom AI', 
      icon: '🎯',
      unlocked: true,
      date: stats?.joinedDate
    },
    { 
      title: 'Collector', 
      description: 'Created your first collection', 
      icon: '📚',
      unlocked: collections.length > 0,
      date: collections.length > 0 ? 'Unlocked' : 'Locked'
    },
    { 
      title: 'Bookworm', 
      description: 'Saved 10+ verses', 
      icon: '🔖',
      unlocked: data.saved_verses.length >= 10,
      date: data.saved_verses.length >= 10 ? 'Unlocked' : `${data.saved_verses.length}/10`
    },
    { 
      title: 'Deep Thinker', 
      description: 'Had 20+ chat sessions', 
      icon: '💭',
      unlocked: data.chat_history.length >= 20,
      date: data.chat_history.length >= 20 ? 'Unlocked' : `${data.chat_history.length}/20`
    },
    { 
      title: 'Wisdom Seeker', 
      description: 'Maintain a 7-day streak', 
      icon: '⭐',
      unlocked: (stats?.streak ?? 0) >= 7,
      date: (stats?.streak ?? 0) >= 7 ? 'Unlocked' : `${stats?.streak ?? 0}/7 days`
    },
    { 
      title: 'Curator', 
      description: 'Created 5+ collections', 
      icon: '🏆',
      unlocked: collections.length >= 5,
      date: collections.length >= 5 ? 'Unlocked' : `${collections.length}/5`
    }
  ] : []

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
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-black mb-2 bg-gradient-to-r from-white via-orange-200 to-white bg-clip-text text-transparent">My Profile</h1>
              <p className="text-sm text-white/60">Your spiritual journey dashboard</p>
            </div>

            {!data ? (
              <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-6 backdrop-blur-xl shadow-xl">
                <p className="text-center text-white/80">Failed to load profile. Please try again later.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Stats Overview - 4 Cards */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="group rounded-2xl border border-white/10 bg-gradient-to-br from-orange-500/10 to-orange-600/5 p-6 backdrop-blur-xl shadow-xl hover:border-orange-500/30 transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="h-12 w-12 rounded-xl bg-orange-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <BookmarkIcon className="h-6 w-6 text-orange-400" />
                      </div>
                      <TrendingUpIcon className="h-5 w-5 text-orange-400/50" />
                    </div>
                    <p className="text-3xl font-black text-white mb-1">{stats?.totalSavedVerses}</p>
                    <p className="text-sm text-white/60">Saved Verses</p>
                  </div>

                  <div className="group rounded-2xl border border-white/10 bg-gradient-to-br from-purple-500/10 to-purple-600/5 p-6 backdrop-blur-xl shadow-xl hover:border-purple-500/30 transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="h-12 w-12 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <FolderIcon className="h-6 w-6 text-purple-400" />
                      </div>
                      <TrendingUpIcon className="h-5 w-5 text-purple-400/50" />
                    </div>
                    <p className="text-3xl font-black text-white mb-1">{stats?.totalCollections}</p>
                    <p className="text-sm text-white/60">Collections</p>
                  </div>

                  <div className="group rounded-2xl border border-white/10 bg-gradient-to-br from-blue-500/10 to-blue-600/5 p-6 backdrop-blur-xl shadow-xl hover:border-blue-500/30 transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="h-12 w-12 rounded-xl bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <MessageSquareIcon className="h-6 w-6 text-blue-400" />
                      </div>
                      <TrendingUpIcon className="h-5 w-5 text-blue-400/50" />
                    </div>
                    <p className="text-3xl font-black text-white mb-1">{stats?.totalChats}</p>
                    <p className="text-sm text-white/60">Chat Sessions</p>
                  </div>

                  <div className="group rounded-2xl border border-white/10 bg-gradient-to-br from-green-500/10 to-green-600/5 p-6 backdrop-blur-xl shadow-xl hover:border-green-500/30 transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="h-12 w-12 rounded-xl bg-green-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <SparklesIcon className="h-6 w-6 text-green-400" />
                      </div>
                      <TrendingUpIcon className="h-5 w-5 text-green-400/50" />
                    </div>
                    <p className="text-3xl font-black text-white mb-1">{stats?.streak}</p>
                    <p className="text-sm text-white/60">Day Streak</p>
                  </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid gap-6 lg:grid-cols-3">
                  {/* Left Column - Account & Activity */}
                  <div className="lg:col-span-2 space-y-6">
                    {/* Account Details */}
                    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/90 to-[#1f1f35]/70 p-6 backdrop-blur-xl shadow-xl">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-2xl font-black shadow-lg">
                            {data.name.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <h2 className="text-xl font-bold text-white">{data.name}</h2>
                            <p className="text-sm text-white/60">{data.email}</p>
                          </div>
                        </div>
                        <button className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm font-medium text-white/80 hover:bg-white/10 hover:text-white transition-all">
                          <SettingsIcon className="h-4 w-4 inline mr-2" />
                          Edit
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                          <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Last Mood</p>
                          <p className="text-lg font-semibold text-white flex items-center gap-2">
                            {data.last_mood ? (
                              <>
                                <span className="text-2xl">{data.last_mood === 'happy' ? '😊' : data.last_mood === 'sad' ? '😢' : data.last_mood === 'anxious' ? '😰' : data.last_mood === 'peaceful' ? '😌' : '🤔'}</span>
                                {data.last_mood}
                              </>
                            ) : '—'}
                          </p>
                        </div>
                        <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                          <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Favorite Source</p>
                          <p className="text-lg font-semibold text-white truncate">{stats?.favoriteSource}</p>
                        </div>
                        <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                          <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Member Since</p>
                          <p className="text-lg font-semibold text-white">{stats?.joinedDate}</p>
                        </div>
                        <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                          <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Current Streak</p>
                          <p className="text-lg font-semibold text-white flex items-center gap-2">
                            <span className="text-2xl">🔥</span>
                            {stats?.streak} days
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Recent Activity / Chat History */}
                    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/90 to-[#1f1f35]/70 p-6 backdrop-blur-xl shadow-xl">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="h-12 w-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                          <MessageSquareIcon className="h-6 w-6 text-blue-400" />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold text-white">Recent Activity</h2>
                          <p className="text-xs text-white/50">Your latest chat sessions</p>
                        </div>
                      </div>
                      <div className="space-y-3 max-h-[400px] overflow-y-auto custom-scrollbar">
                        {data.chat_history.length === 0 ? (
                          <div className="text-center py-12">
                            <div className="h-16 w-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4">
                              <MessageSquareIcon className="h-8 w-8 text-white/20" />
                            </div>
                            <p className="text-sm text-white/50">No chat history yet</p>
                            <p className="text-xs text-white/30 mt-1">Start a conversation to see your activity</p>
                          </div>
                        ) : (
                          data.chat_history.map((c, i: number) => (
                            <div key={i} className="group rounded-xl bg-white/5 border border-white/10 p-4 hover:bg-white/10 hover:border-white/20 transition-all duration-200">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-semibold text-orange-400 flex items-center gap-2">
                                  <HeartIcon className="h-3 w-3" />
                                  Mood: {c.mood ?? 'Unknown'}
                                </span>
                                <span className="text-xs text-white/40 flex items-center gap-1">
                                  <CalendarIcon className="h-3 w-3" />
                                  {new Date(c.date).toLocaleDateString()}
                                </span>
                              </div>
                              <p className="text-sm text-white/80 line-clamp-2">{c.summary}</p>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column - Achievements & Quick Actions */}
                  <div className="space-y-6">
                    {/* Achievements */}
                    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/90 to-[#1f1f35]/70 p-6 backdrop-blur-xl shadow-xl">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="h-12 w-12 rounded-xl bg-yellow-500/10 flex items-center justify-center">
                          <AwardIcon className="h-6 w-6 text-yellow-400" />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold text-white">Achievements</h2>
                          <p className="text-xs text-white/50">{achievements.filter(a => a.unlocked).length}/{achievements.length} unlocked</p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {achievements.map((achievement, i) => (
                          <div 
                            key={i} 
                            className={`rounded-xl p-4 border transition-all duration-200 ${
                              achievement.unlocked 
                                ? 'bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-yellow-500/30 hover:border-yellow-500/50' 
                                : 'bg-white/5 border-white/10 opacity-60 hover:opacity-80'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`text-2xl ${!achievement.unlocked && 'grayscale'}`}>
                                {achievement.icon}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-white mb-1">{achievement.title}</p>
                                <p className="text-xs text-white/60 mb-2">{achievement.description}</p>
                                <p className="text-xs text-white/40">{achievement.date}</p>
                              </div>
                              {achievement.unlocked && (
                                <div className="flex-shrink-0">
                                  <div className="h-6 w-6 rounded-full bg-green-500/20 flex items-center justify-center">
                                    <span className="text-green-400 text-xs">✓</span>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-[#252640]/90 to-[#1f1f35]/70 p-6 backdrop-blur-xl shadow-xl">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="h-12 w-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                          <SparklesIcon className="h-6 w-6 text-purple-400" />
                        </div>
                        <h2 className="text-xl font-bold text-white">Quick Actions</h2>
                      </div>
                      <div className="space-y-2">
                        <Link href="/saved" className="w-full group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all">
                          <BookmarkIcon className="h-4 w-4 text-orange-400" />
                          <span className="flex-1 text-left">View Saved Verses</span>
                          <span className="text-xs text-white/40">→</span>
                        </Link>
                        <Link href="/collections" className="w-full group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all">
                          <FolderIcon className="h-4 w-4 text-purple-400" />
                          <span className="flex-1 text-left">Manage Collections</span>
                          <span className="text-xs text-white/40">→</span>
                        </Link>
                        <Link href="/admin/analytics" className="w-full group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all">
                          <BarChartIcon className="h-4 w-4 text-blue-400" />
                          <span className="flex-1 text-left">View Analytics</span>
                          <span className="text-xs text-white/40">→</span>
                        </Link>
                        <Link href="/notifications" className="w-full group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all">
                          <BellIcon className="h-4 w-4 text-yellow-400" />
                          <span className="flex-1 text-left">Notifications</span>
                          <span className="text-xs text-white/40">→</span>
                        </Link>
                        <Link href="/reading-plans" className="w-full group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all">
                          <ShieldIcon className="h-4 w-4 text-green-400" />
                          <span className="flex-1 text-left">Reading Plans</span>
                          <span className="text-xs text-white/40">→</span>
                        </Link>
                      </div>
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
