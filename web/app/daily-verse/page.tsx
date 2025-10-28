import { cookies } from 'next/headers'
import { AppShell } from '@/components/shell/app-shell'
import { DailyVerseResponse } from '@/types/api'
import DailyVerseClient from './daily-verse-client'

export default async function DailyVersePage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: DailyVerseResponse | null = null
  try {
    const res = await fetch(`${apiBase}/daily-verse-with-save`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      data = (await res.json()) as DailyVerseResponse
    }
  } catch (e) {
    // swallow to render error UI below
  }

  return (
    <AppShell>
      <div className="relative">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/10 via-transparent to-transparent" />
      </div>
      <div className="container py-8">
        <h1 className="mb-6 text-2xl font-semibold">Your daily verse</h1>
        {!data && (
          <div className="rounded-md border p-6">Failed to load daily verse.</div>
        )}
        {data && <DailyVerseClient initialData={data} />}
      </div>
    </AppShell>
  )
}
