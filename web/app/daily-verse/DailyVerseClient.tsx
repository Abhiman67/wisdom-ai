"use client"
import { useState } from 'react'
import { VerseCard } from '@/components/verse-card'
import { apiClient } from '@/lib/api'
import { DailyVerseResponse } from '@/types/api'

export default function DailyVerseClient({ initialData }: { initialData: DailyVerseResponse }) {
  const [data, setData] = useState<DailyVerseResponse>(initialData)
  const [saving, setSaving] = useState(false)

  const onSave = async () => {
    try {
      setSaving(true)
      const res = await apiClient.post('/save-verse-from-daily', {})
      if (res?.success) {
        setData({ ...data, is_saved: true } as any)
      }
    } catch (e) {
      console.error(e)
      alert('Failed to save verse')
    } finally {
      setSaving(false)
    }
  }

  return (
    <VerseCard
      verseId={data.verse_id}
      text={data.text}
      source={data.source}
      imageUrl={data.image_url ?? undefined}
      audioUrl={data.audio_url ?? undefined}
      isSaved={(data as any).is_saved ?? false}
      onSave={onSave}
      saving={saving}
    />
  )
}
