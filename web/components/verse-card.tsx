"use client"
import Image from 'next/image'
import { Button } from '@/components/ui/button'

export function VerseCard({
  verseId,
  text,
  source,
  imageUrl,
  audioUrl,
  isSaved,
  onSave,
  saving
}: {
  verseId: string
  text: string
  source: string
  imageUrl?: string
  audioUrl?: string
  isSaved?: boolean
  onSave?: () => void
  saving?: boolean
}) {
  return (
    <div className="overflow-hidden rounded-xl border bg-card shadow-sm">
      {imageUrl && (
        <div className="relative aspect-[1200/630] w-full">
          <Image src={imageUrl} alt={verseId} fill className="object-cover" sizes="100vw" priority={false} />
          <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-background/20 to-transparent" />
        </div>
      )}
      <div className="space-y-3 p-5">
        <div className="prose prose-lg max-w-none dark:prose-invert">
          <blockquote>“{text}”</blockquote>
        </div>
        <div className="flex items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">— {source}</div>
          {onSave && (
            <Button onClick={onSave} disabled={isSaved || saving} size="sm" variant="outline" className="rounded-full">
              {saving ? 'Saving…' : isSaved ? '✓ Saved' : 'Save'}
            </Button>
          )}
        </div>
        {audioUrl && (
          <audio controls src={audioUrl} className="w-full" />
        )}
      </div>
    </div>
  )
}
