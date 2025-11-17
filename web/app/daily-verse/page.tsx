import { cookies } from 'next/headers'
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

  return <DailyVerseClient initialData={data} />
}
