import { AppShell } from '@/components/shell/app-shell'
import { Skeleton } from '@/components/ui/skeleton'

export default function Loading() {
  return (
    <AppShell>
      <div className="container py-8">
        <div className="mb-6 h-7 w-28"><Skeleton className="h-7 w-28" /></div>
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-md border p-4">
            <Skeleton className="mb-2 h-5 w-24" />
            <Skeleton className="mb-1 h-4 w-40" />
            <Skeleton className="mb-1 h-4 w-60" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="rounded-md border p-4">
            <Skeleton className="mb-2 h-5 w-32" />
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="mb-2 h-10 w-full" />
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
