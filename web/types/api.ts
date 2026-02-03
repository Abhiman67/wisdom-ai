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
  created_at?: string | null
  streak?: number
  favorite_source?: string | null
}

export type Collection = {
  id: number
  name: string
  description?: string
  verse_count: number
  is_public: boolean
  created_at: string
}

export type CollectionDetail = Collection & {
  verses: Array<{
    verse_id: string
    text: string
    source: string
  }>
}

export type VerseNote = {
  id: number
  note: string
  created_at: string
  updated_at: string
}

export type ShareResponse = {
  share_url: string
  token: string
}

export type VerseRating = {
  average: number
  count: number
}

export type VerseComment = {
  id: number
  comment: string
  user_name: string
  created_at: string
}

export type MoodHistoryItem = {
  mood: string
  timestamp: string
}

export type ReadingPlan = {
  id: number
  name: string
  description: string
  duration_days: number
}

export type UserReadingPlan = {
  enrollment_id: number
  plan_name: string
  plan_description: string
  duration_days: number
  current_day: number
  completed: boolean
  start_date: string
}

export type Notification = {
  id: number
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export type ChatHistoryItem = {
  id: number
  date: string
  mood?: string
  summary: string
  verse_id?: string
}

export type AdminUser = {
  id: number
  uuid: string
  name: string
  email: string
  is_admin: boolean
  created_at: string
  last_mood?: string
}

export type AdminVerse = {
  id: number
  verse_id: string
  text: string
  source: string
  created_at: string
}

export type FlaggedComment = {
  id: number
  verse_id: string
  comment: string
  user_name: string
  user_email: string
  created_at: string
}

export type SystemLog = {
  id: number
  level: string
  message: string
  user_id?: number
  endpoint?: string
  timestamp: string
}

export type EngagementMetrics = {
  event_counts: Record<string, number>
  daily_active_users: Record<string, number>
  total_events: number
}

export type VersePopularity = {
  verse_id: string
  views: number
  text: string
  source: string
}
