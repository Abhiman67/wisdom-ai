import { cookies } from 'next/headers'
import { AppShell } from '@/components/shell/app-shell'
import AdminClient from './admin-client'

type Analytics = {
  active_users_last_30_days: number
  mood_distribution_last_7_days: Record<string, number>
  peak_usage_hours: Array<[number, number]>
  popular_verses: Array<[string, number]>
  total_users: number
  total_verses: number
}

export default async function AdminPage() {
  const token = cookies().get('token')?.value
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  let data: Analytics | null = null
  let status: number | null = null
  try {
    const res = await fetch(`${apiBase}/admin/analytics`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: 'no-store'
    })
    status = res.status
    if (res.ok) {
      data = (await res.json()) as Analytics
    }
  } catch (e) {
    // fall through to error UI
  }
  return (
    <AppShell>
      {!data ? (
        <div className="container space-y-6 py-8">
          <h1 className="text-2xl font-semibold">Admin Analytics</h1>
          <div className="rounded-md border p-6">
            {status === 401 && 'Your session is invalid or expired. Please log in again.'}
            {status === 403 && 'Admins only. Your account does not have permission to view analytics.'}
            {!status || (status !== 401 && status !== 403) ? 'Failed to load analytics.' : null}
          </div>
        </div>
      ) : (
        <AdminClient data={data} />
      )}
    </AppShell>
  )
}
