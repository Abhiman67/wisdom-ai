'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { EngagementMetrics, VersePopularity } from '@/types/api'
import { Card } from '@/components/ui/card'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import dynamic from 'next/dynamic'

const TrendingUpIcon = dynamic(() => import('lucide-react').then(m => m.TrendingUp), { ssr: false })
const UsersIcon = dynamic(() => import('lucide-react').then(m => m.Users), { ssr: false })
const ActivityIcon = dynamic(() => import('lucide-react').then(m => m.Activity), { ssr: false })

const COLORS = ['#f97316', '#a855f7', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function AdminAnalyticsPage() {
  const [engagement, setEngagement] = useState<EngagementMetrics | null>(null)
  const [popularity, setPopularity] = useState<VersePopularity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const [engagementData, popularityData] = await Promise.all([
        apiClient.get<EngagementMetrics>('/admin/analytics/engagement'),
        apiClient.get<VersePopularity[]>('/admin/analytics/verse-popularity')
      ])
      setEngagement(engagementData)
      setPopularity(popularityData)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6">
              <div className="h-8 w-48 bg-white/10 rounded animate-pulse mb-2"></div>
              <div className="h-4 w-64 bg-white/10 rounded animate-pulse"></div>
            </div>
            
            {/* Stats Cards Skeleton */}
            <div className="grid gap-6 mb-8 md:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-6 animate-pulse">
                  <div className="flex items-start justify-between mb-4">
                    <div className="h-12 w-12 rounded-lg bg-white/10"></div>
                    <div className="h-4 w-12 bg-white/10 rounded"></div>
                  </div>
                  <div className="h-8 w-20 bg-white/10 rounded mb-2"></div>
                  <div className="h-4 w-32 bg-white/10 rounded"></div>
                </div>
              ))}
            </div>
            
            {/* Chart Skeletons */}
            <div className="grid gap-6 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-6 animate-pulse">
                  <div className="h-5 w-40 bg-white/10 rounded mb-4"></div>
                  <div className="h-64 bg-white/5 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    )
  }

  const eventData = engagement ? Object.entries(engagement.event_counts).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    count: value
  })) : []

  const dauData = engagement ? Object.entries(engagement.daily_active_users).map(([date, users]) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    users
  })).slice(-14) : []

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />
      
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent mb-8">
              Analytics Dashboard
            </h1>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-3 mb-2">
                  <ActivityIcon className="w-8 h-8 text-orange-400" />
                  <div>
                    <p className="text-sm text-white/60">Total Events</p>
                    <p className="text-2xl font-bold text-white">{engagement?.total_events.toLocaleString()}</p>
                  </div>
                </div>
              </Card>

              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-3 mb-2">
                  <UsersIcon className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-sm text-white/60">Avg Daily Users</p>
                    <p className="text-2xl font-bold text-white">
                      {engagement ? Math.round(Object.values(engagement.daily_active_users).reduce((a, b) => a + b, 0) / Object.keys(engagement.daily_active_users).length) : 0}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="bg-white/5 border-white/10 p-6">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUpIcon className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-sm text-white/60">Event Types</p>
                    <p className="text-2xl font-bold text-white">{engagement ? Object.keys(engagement.event_counts).length : 0}</p>
                  </div>
                </div>
              </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <Card className="bg-white/5 border-white/10 p-6">
                <h3 className="text-lg font-semibold mb-4">Daily Active Users (Last 14 Days)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={dauData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="date" stroke="rgba(255,255,255,0.6)" />
                    <YAxis stroke="rgba(255,255,255,0.6)" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1a1b2e', border: '1px solid rgba(255,255,255,0.1)' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Line type="monotone" dataKey="users" stroke="#a855f7" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              <Card className="bg-white/5 border-white/10 p-6">
                <h3 className="text-lg font-semibold mb-4">Events by Type</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={eventData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {eventData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1a1b2e', border: '1px solid rgba(255,255,255,0.1)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            <Card className="bg-white/5 border-white/10 p-6">
              <h3 className="text-lg font-semibold mb-4">Most Popular Verses</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={popularity.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="verse_id" stroke="rgba(255,255,255,0.6)" />
                  <YAxis stroke="rgba(255,255,255,0.6)" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1a1b2e', border: '1px solid rgba(255,255,255,0.1)' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="views" fill="url(#colorGradient)" />
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0.8}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
              
              <div className="mt-6 space-y-3">
                {popularity.slice(0, 5).map((verse, idx) => (
                  <div key={verse.verse_id} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                    <span className="text-2xl font-bold text-white/40">#{idx + 1}</span>
                    <div className="flex-1">
                      <p className="text-sm text-white/90">{verse.text}</p>
                      <p className="text-xs text-white/60 mt-1">
                        {verse.source} • {verse.views} views
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
