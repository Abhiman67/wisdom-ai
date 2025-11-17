"use client"

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Sidebar } from '@/components/shell/sidebar'
import { 
  BookOpen, MessageSquare, Bookmark, TrendingUp,
  Calendar, Heart, Sparkles, ArrowRight
} from 'lucide-react'

interface DashboardStats {
  totalSaved: number
  totalChats: number
  streak: number
  todayVerse: any
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/profile').then(r => r.json()),
      fetch('/api/daily-verse-with-save').then(r => r.json())
    ])
      .then(([profile, verse]) => {
        setStats({
          totalSaved: profile?.saved_verses?.length || 0,
          totalChats: profile?.chat_history?.length || 0,
          streak: profile?.streak || 0,
          todayVerse: verse
        })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36] text-white overflow-hidden">
        <Sidebar />
        <main className="flex flex-1 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-orange-500 border-t-transparent" />
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36] text-white overflow-hidden">
      <Sidebar />

      <main className="flex flex-1 flex-col min-w-0 relative">
        {/* Animated background orbs */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-orange-500/10 blur-3xl" />
          <div className="absolute right-1/4 top-1/2 h-96 w-96 animate-pulse rounded-full bg-purple-500/10 blur-3xl" style={{ animationDelay: '2s' }} />
          <div className="absolute bottom-1/4 left-1/2 h-96 w-96 animate-pulse rounded-full bg-pink-500/10 blur-3xl" style={{ animationDelay: '4s' }} />
        </div>

        <div className="relative flex-1 overflow-y-auto px-4 py-8 md:px-8 lg:px-12">
          <div className="mx-auto max-w-7xl">
            {/* Welcome Section */}
            <div className="mb-10 text-center">
              <h1 className="mb-3 bg-gradient-to-r from-orange-400 via-pink-400 to-purple-400 bg-clip-text text-4xl font-bold text-transparent sm:text-5xl">
                Welcome Back
              </h1>
              <p className="text-lg text-white/70">
                Your spiritual journey continues today
              </p>
            </div>

            {/* Stats Cards */}
            <div className="mb-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                icon={<Bookmark className="h-6 w-6" />}
                label="Saved Verses"
                value={stats?.totalSaved || 0}
                gradient="from-orange-500 to-pink-500"
              />
              <StatCard
                icon={<MessageSquare className="h-6 w-6" />}
                label="Conversations"
                value={stats?.totalChats || 0}
                gradient="from-purple-500 to-blue-500"
              />
              <StatCard
                icon={<Calendar className="h-6 w-6" />}
                label="Day Streak"
                value={stats?.streak || 0}
                gradient="from-green-500 to-emerald-500"
              />
              <StatCard
                icon={<Heart className="h-6 w-6" />}
                label="Favorites"
                value={stats?.totalSaved || 0}
                gradient="from-pink-500 to-rose-500"
              />
            </div>

            {/* Today's Verse Preview */}
            {stats?.todayVerse && (
              <div className="mb-10">
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-white">Today's Verse</h2>
                  <Link
                    href="/daily-verse"
                    className="flex items-center gap-2 text-sm text-orange-400 transition-colors hover:text-orange-300"
                  >
                    View Full <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
                <div className="group overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-8 backdrop-blur-xl transition-all hover:border-orange-500/30 hover:shadow-2xl hover:shadow-orange-500/10">
                  <div className="mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-orange-400" />
                    <span className="text-xs font-medium uppercase tracking-widest text-orange-400">
                      Daily Inspiration
                    </span>
                  </div>
                  <p className="mb-4 text-xl italic leading-relaxed text-white/90 sm:text-2xl">
                    "{stats.todayVerse.text?.slice(0, 200) || 'Loading verse...'}..."
                  </p>
                  <p className="text-sm text-white/50">— {stats.todayVerse.source || 'Sacred Text'}</p>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="mb-10">
              <h2 className="mb-6 text-2xl font-bold text-white">Quick Actions</h2>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <ActionCard
                  href="/chat"
                  icon={<MessageSquare className="h-8 w-8" />}
                  title="Start Chat"
                  description="Get spiritual guidance"
                  gradient="from-orange-500 to-pink-500"
                />
                <ActionCard
                  href="/daily-verse"
                  icon={<BookOpen className="h-8 w-8" />}
                  title="Daily Verse"
                  description="Read today's wisdom"
                  gradient="from-purple-500 to-blue-500"
                />
                <ActionCard
                  href="/saved"
                  icon={<Bookmark className="h-8 w-8" />}
                  title="Saved Verses"
                  description="Review your favorites"
                  gradient="from-green-500 to-emerald-500"
                />
              </div>
            </div>

            {/* Continue Journey */}
            <div>
              <h2 className="mb-6 text-2xl font-bold text-white">Continue Your Journey</h2>
              <div className="grid gap-6 sm:grid-cols-2">
                <Link
                  href="/collections"
                  className="group overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 backdrop-blur-xl transition-all hover:border-purple-500/30 hover:shadow-lg hover:shadow-purple-500/10"
                >
                  <h3 className="mb-2 text-lg font-semibold text-white transition-colors group-hover:text-purple-400">
                    Explore Collections
                  </h3>
                  <p className="text-sm text-white/60">
                    Organize your spiritual readings
                  </p>
                </Link>
                <Link
                  href="/reading-plans"
                  className="group overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 backdrop-blur-xl transition-all hover:border-pink-500/30 hover:shadow-lg hover:shadow-pink-500/10"
                >
                  <h3 className="mb-2 text-lg font-semibold text-white transition-colors group-hover:text-pink-400">
                    Reading Plans
                  </h3>
                  <p className="text-sm text-white/60">
                    Follow structured spiritual paths
                  </p>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({ icon, label, value, gradient }: any) {
  return (
    <div className="group overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 backdrop-blur-xl transition-all hover:scale-105 hover:border-white/20 hover:shadow-xl">
      <div className={`mb-3 inline-flex rounded-lg bg-gradient-to-r ${gradient} p-3 text-white shadow-lg`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-white">{value}</div>
      <div className="text-sm text-white/60">{label}</div>
    </div>
  )
}

function ActionCard({ href, icon, title, description, gradient }: any) {
  return (
    <Link
      href={href}
      className="group overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 backdrop-blur-xl transition-all hover:scale-105 hover:border-white/20 hover:shadow-2xl"
    >
      <div className={`mb-4 inline-flex rounded-lg bg-gradient-to-r ${gradient} p-3 text-white shadow-lg transition-transform group-hover:scale-110`}>
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm text-white/60">{description}</p>
      <ArrowRight className="mt-4 h-5 w-5 text-white/40 transition-all group-hover:translate-x-2 group-hover:text-white" />
    </Link>
  )
}
