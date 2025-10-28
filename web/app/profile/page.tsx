import { cookies } from 'next/headers'
import { AppShell } from '@/components/shell/app-shell'
import { UserProfile } from '@/types/api'

export default async function ProfilePage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: UserProfile | null = null
  try {
    const res = await fetch(`${apiBase}/profile`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    if (res.ok) {
      data = (await res.json()) as UserProfile
    }
  } catch (e) {
    // continue to fallback UI
  }

  return (
    <AppShell>
      <div className="container py-8">
        <h1 className="mb-6 text-2xl font-semibold">Profile</h1>
        {!data && (
          <div className="rounded-md border p-6">Failed to load profile.</div>
        )}
        {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-md border p-4">
            <h2 className="mb-2 font-medium">Account</h2>
            <p><span className="text-muted-foreground">Name:</span> {data.name}</p>
            <p><span className="text-muted-foreground">Email:</span> {data.email}</p>
            <p><span className="text-muted-foreground">Last mood:</span> {data.last_mood ?? '—'}</p>
          </div>
          <div className="rounded-md border p-4">
            <h2 className="mb-2 font-medium">Recent chats</h2>
            <ul className="space-y-2 text-sm">
              {data.chat_history.map((c, i: number) => (
                <li key={i} className="rounded bg-muted p-2">
                  <div className="text-muted-foreground">{new Date(c.date).toLocaleString()}</div>
                  <div className="font-medium">Mood: {c.mood ?? '—'}</div>
                  <div className="truncate">{c.summary}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>
        )}
      </div>
    </AppShell>
  )
}
