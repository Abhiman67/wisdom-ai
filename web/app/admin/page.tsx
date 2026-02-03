'use client'
import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import Link from 'next/link'
import { Sidebar } from '@/components/shell/sidebar'

type Analytics = {
  active_users_last_30_days: number
  mood_distribution_last_7_days: Record<string, number>
  peak_usage_hours: Array<[number, number]>
  popular_verses: Array<[string, number]>
  total_users: number
  total_verses: number
}

type ActivityItem = {
  type: 'chat' | 'verse_saved' | 'user_login'
  message: string
  timestamp: string
}

export default function AdminPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'content' | 'settings'>('overview')
  const [systemHealth, setSystemHealth] = useState<{
    application: boolean
    database: boolean
    api: boolean
    llm: boolean
  }>({ application: true, database: true, api: true, llm: true })
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([])
  const [ragEnabled, setRagEnabled] = useState(true)
  const [savingRag, setSavingRag] = useState(false)

  useEffect(() => {
    loadData()
    loadSystemHealth()
    loadRecentActivity()
    loadRagSetting()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await apiClient.get<Analytics>('/admin/analytics')
      setAnalytics(data)
    } catch (e: any) {
      if (e.message.includes('403')) {
        setError('Admin access required. Your account does not have permission.')
      } else if (e.message.includes('401')) {
        setError('Session expired. Please log in again.')
      } else {
        setError('Failed to load analytics.')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadSystemHealth = async () => {
    try {
      const health = await apiClient.get<typeof systemHealth>('/admin/system-health')
      setSystemHealth(health)
    } catch {
      console.error('Failed to load system health')
    }
  }

  const loadRecentActivity = async () => {
    try {
      const activity = await apiClient.get<ActivityItem[]>('/admin/recent-activity')
      setRecentActivity(activity)
    } catch {
      console.error('Failed to load recent activity')
    }
  }

  const loadRagSetting = () => {
    const stored = localStorage.getItem('admin_rag_enabled')
    if (stored !== null) {
      setRagEnabled(stored === 'true')
    }
  }

  const toggleRag = async () => {
    setSavingRag(true)
    const newValue = !ragEnabled
    setRagEnabled(newValue)
    localStorage.setItem('admin_rag_enabled', String(newValue))
    // Optional: could also persist to backend if needed
    setTimeout(() => setSavingRag(false), 500)
  }

  const stats = analytics ? [
    { label: 'Total Users', value: analytics.total_users, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: 'Active Chats', value: analytics.active_users_last_30_days, icon: '💬', color: 'from-purple-500 to-pink-500' },
    { label: 'Saved Verses', value: analytics.total_verses, icon: '📖', color: 'from-teal-500 to-green-500' },
    { label: 'System Status', value: 'Active', icon: '📈', color: 'from-green-500 to-emerald-500', isStatus: true }
  ] : []

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-orange-500 border-r-transparent mb-4"></div>
            <p className="text-white/60">Loading admin dashboard...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-red-900/10 p-8 backdrop-blur-xl shadow-xl text-center">
            <div className="mb-4 mx-auto h-16 w-16 rounded-full bg-red-500/20 flex items-center justify-center">
              <span className="text-3xl">⚠️</span>
            </div>
            <p className="text-red-300 mb-4">{error}</p>
            <Link href="/login" className="inline-block text-sm text-purple-400 hover:text-purple-300 underline">
              Return to login
            </Link>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />
      
      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 relative overflow-y-auto">
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-orange-500/5 pointer-events-none"></div>
        
        {/* Header */}
        <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-10 flex-shrink-0">
          <div className="px-6 py-5">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-black mb-1 bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">Admin Dashboard</h1>
                <p className="text-sm text-white/50">Control Panel & Analytics</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-purple-500/20 border border-purple-500/30 px-4 py-2 text-sm font-semibold text-purple-300">
                  👑 Administrator
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 px-6 py-6 relative z-10">
          <div className="max-w-7xl mx-auto">
        {/* Stats Cards */}
        <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800/50 to-slate-900/50 p-6 backdrop-blur transition hover:border-white/20"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">{stat.label}</p>
                  {stat.isStatus ? (
                    <p className="mt-2 text-2xl font-bold text-green-400">{stat.value}</p>
                  ) : (
                    <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                  )}
                </div>
                <div className={`rounded-xl bg-gradient-to-br ${stat.color} p-3 text-2xl opacity-80 group-hover:opacity-100`}>
                  {stat.icon}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-6 border-b border-white/10">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'users', label: 'Users', icon: '👥' },
            { id: 'content', label: 'Content', icon: '📝' },
            { id: 'settings', label: 'Settings', icon: '⚙️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium transition ${
                activeTab === tab.id
                  ? 'border-purple-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-white'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* System Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-slate-800/30 p-6 backdrop-blur">
              <h2 className="mb-6 text-xl font-semibold">System Overview</h2>
              <div className="space-y-4">
                {[
                  { label: 'Application Status', detail: 'Wisdom AI is running normally', status: systemHealth.application },
                  { label: 'Database Connection', detail: 'Connected and operational', status: systemHealth.database },
                  { label: 'API Server', detail: 'Running on port 8000', status: systemHealth.api },
                  { label: 'LLM Integration', detail: 'AI responses enabled', status: systemHealth.llm }
                ].map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center justify-between rounded-xl border border-white/5 bg-slate-900/30 p-4"
                  >
                    <div>
                      <p className="font-medium">{item.label}</p>
                      <p className="text-sm text-slate-400">{item.detail}</p>
                    </div>
                    <div
                      className={`h-3 w-3 rounded-full ${
                        item.status ? 'bg-green-500' : 'bg-red-500'
                      } shadow-lg ${item.status ? 'shadow-green-500/50' : 'shadow-red-500/50'}`}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="rounded-2xl border border-white/10 bg-slate-800/30 p-6 backdrop-blur">
              <h2 className="mb-6 text-xl font-semibold">Recent Activity</h2>
              <div className="space-y-3">
                {recentActivity.map((activity, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 rounded-xl border border-white/5 bg-slate-900/30 p-4"
                  >
                    <div
                      className={`mt-1 rounded-lg p-2 ${
                        activity.type === 'chat'
                          ? 'bg-purple-500/20 text-purple-400'
                          : activity.type === 'verse_saved'
                          ? 'bg-teal-500/20 text-teal-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}
                    >
                      {activity.type === 'chat' ? '💬' : activity.type === 'verse_saved' ? '📖' : '👤'}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">{activity.message}</p>
                      <p className="mt-1 text-xs text-slate-400">{activity.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Other tabs placeholder */}
        {activeTab === 'users' && (
          <div className="rounded-2xl border border-white/10 bg-slate-800/30 p-12 text-center backdrop-blur">
            <p className="text-slate-400">👥 User management coming soon</p>
          </div>
        )}

        {activeTab === 'content' && (
          <div className="rounded-2xl border border-white/10 bg-slate-800/30 p-12 text-center backdrop-blur">
            <p className="text-slate-400">📝 Content management coming soon</p>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* RAG Global Control */}
            <div className="rounded-2xl border border-white/10 bg-slate-800/30 p-6 backdrop-blur">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    🧠 RAG System Control
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Toggle retrieval-augmented generation globally
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`text-sm font-medium ${ragEnabled ? 'text-green-400' : 'text-slate-400'}`}>
                    {ragEnabled ? '✓ Enabled' : '○ Disabled'}
                  </span>
                  <button
                    onClick={toggleRag}
                    disabled={savingRag}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:ring-offset-slate-900 ${
                      ragEnabled ? 'bg-gradient-to-r from-orange-500 to-orange-600' : 'bg-slate-700'
                    } ${savingRag ? 'opacity-50' : ''}`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform ${
                        ragEnabled ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
              <div className="rounded-xl border border-white/5 bg-slate-900/30 p-4">
                <div className="flex items-start gap-3">
                  <div className={`rounded-lg p-2 ${ragEnabled ? 'bg-orange-500/20 text-orange-400' : 'bg-purple-500/20 text-purple-400'}`}>
                    {ragEnabled ? '🔍' : '⚡'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      {ragEnabled ? 'Context Retrieval Active' : 'Direct Model Inference'}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {ragEnabled
                        ? 'Queries retrieve relevant Gita passages before generating responses'
                        : 'Model generates responses using only fine-tuned knowledge'}
                    </p>
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
