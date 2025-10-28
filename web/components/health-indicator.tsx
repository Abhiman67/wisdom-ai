"use client"
import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'

export function HealthIndicator() {
  const [ok, setOk] = useState<boolean | null>(null)
  useEffect(() => {
    let mounted = true
    apiClient.get('/health')
      .then(() => mounted && setOk(true))
      .catch(() => mounted && setOk(false))
    return () => { mounted = false }
  }, [])

  const color = ok == null ? 'bg-muted-foreground/40' : ok ? 'bg-emerald-500' : 'bg-red-500'
  const label = ok == null ? 'Checking…' : ok ? 'Backend: Online' : 'Backend: Offline'

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground" title={label}>
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />
      <span className="hidden sm:inline">{label}</span>
    </div>
  )
}
