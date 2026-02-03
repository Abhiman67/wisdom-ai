"use client"
import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar
} from 'recharts'

type Analytics = {
  active_users_last_30_days: number
  mood_distribution_last_7_days: Record<string, number>
  peak_usage_hours: Array<[number, number]>
  popular_verses: Array<[string, number]>
  total_users: number
  total_verses: number
}

export default function AdminClient({ data }: { data: Analytics }) {
  const moodCounts = useMemo(() => {
    return Object.entries(data?.mood_distribution_last_7_days || {}).map(([mood, count]) => ({ mood, count }))
  }, [data])

  const peakHours = useMemo(() => {
    const arr = data?.peak_usage_hours || []
    return arr.map(([hour, count]) => ({ hour, count }))
  }, [data])

  const popularVerses = useMemo(() => {
    const arr = data?.popular_verses || []
    return arr.map(([verse_id, count]) => ({ verse_id, count }))
  }, [data])

  return (
    <div className="container space-y-6 py-8">
      <h1 className="text-2xl font-semibold">Admin Analytics</h1>
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-sm">Total Users</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{data.total_users}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Total Verses</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{data.total_verses}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Active Users (30d)</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{data.active_users_last_30_days}</CardContent>
        </Card>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Mood distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={moodCounts}>
                <XAxis dataKey="mood" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Peak usage hours (last 7d)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={peakHours}>
                <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#7C3AED" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Popular verses (last 7d)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {popularVerses.slice(0, 9).map((v) => (
                <div key={v.verse_id} className="flex items-center justify-between rounded-md border p-2 text-sm">
                  <span className="truncate" title={v.verse_id}>{v.verse_id}</span>
                  <span className="font-medium">{v.count}</span>
                </div>
              ))}
              {popularVerses.length === 0 && (
                <div className="text-sm text-muted-foreground">No data yet.</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
