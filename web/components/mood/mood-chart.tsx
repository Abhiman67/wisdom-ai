'use client'
import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { MoodHistoryItem } from '@/types/api'
import { Card } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const moodColors: Record<string, string> = {
  happy: '#10b981',
  sad: '#3b82f6',
  anxious: '#f59e0b',
  grateful: '#a855f7',
  hopeful: '#06b6d4',
  angry: '#ef4444',
  neutral: '#6b7280'
}

export function MoodChart({ days = 30 }: { days?: number }) {
  const [moodHistory, setMoodHistory] = useState<MoodHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMoodHistory()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days])

  const loadMoodHistory = async () => {
    try {
      const data = await apiClient.get<MoodHistoryItem[]>(`/mood-history?days=${days}`)
      setMoodHistory(data)
    } catch (error) {
      console.error('Failed to load mood history:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="bg-white/5 border-white/10 p-6">
        <p className="text-white/60">Loading mood history...</p>
      </Card>
    )
  }

  if (moodHistory.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-6">
        <p className="text-white/60">No mood data available yet</p>
      </Card>
    )
  }

  // Group by date and count moods
  const moodByDate: Record<string, Record<string, number>> = {}
  moodHistory.forEach(item => {
    const date = new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    if (!moodByDate[date]) {
      moodByDate[date] = {}
    }
    moodByDate[date][item.mood] = (moodByDate[date][item.mood] || 0) + 1
  })

  // Convert to chart data
  const chartData = Object.entries(moodByDate).map(([date, moods]) => {
    const dominant = Object.entries(moods).sort((a, b) => b[1] - a[1])[0]
    return {
      date,
      mood: dominant[0],
      count: dominant[1]
    }
  }).slice(-14) // Last 14 days

  return (
    <Card className="bg-white/5 border-white/10 p-6">
      <h3 className="text-lg font-semibold mb-4 text-white">Mood Tracking</h3>
      
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="date" stroke="rgba(255,255,255,0.6)" />
          <YAxis stroke="rgba(255,255,255,0.6)" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1a1b2e', border: '1px solid rgba(255,255,255,0.1)' }}
            labelStyle={{ color: '#fff' }}
          />
          <Line 
            type="monotone" 
            dataKey="count" 
            stroke="#a855f7" 
            strokeWidth={2}
            dot={{ fill: '#a855f7', r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-4 gap-2">
        {Object.entries(moodColors).map(([mood, color]) => (
          <div key={mood} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-white/70 capitalize">{mood}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
