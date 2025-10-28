export type TokenResponse = {
  access_token: string
  token_type: string
  user_id: string
  name: string
}

export type ChatResponse = {
  reply: string
  detected_mood: string
  verse_id: string
  verse_text: string
  verse_source: string
}

export type DailyVerseResponse = {
  verse_id: string
  text: string
  source: string
  audio_url?: string | null
  image_url?: string | null
  is_saved?: boolean
}

export type SavedVerse = {
  verse_id: string
  text: string
  source: string
  image_url: string
  audio_url: string
}

export type SavedVersesResponse = {
  saved_verses: SavedVerse[]
}

export type UserProfile = {
  user_id: string
  name: string
  email: string
  last_mood?: string | null
  recent_verses: Record<string, string[]>
  saved_verses: string[]
  chat_history: Array<{
    date: string
    mood?: string | null
    summary: string
    verse_id?: string | null
  }>
}
