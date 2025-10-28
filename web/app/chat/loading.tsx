import { AppShell } from '@/components/shell/app-shell'
import { Skeleton } from '@/components/ui/skeleton'

export default function Loading() {
  return (
    <AppShell>
      <div className="container flex h-[calc(100vh-64px)] flex-col py-4">
        <div className="flex-1 space-y-3 overflow-y-auto rounded-md border p-4">
          <div className="flex justify-end">
            <Skeleton className="h-8 w-40" />
          </div>
          <div className="flex justify-start">
            <Skeleton className="h-8 w-64" />
          </div>
          <div className="flex justify-end">
            <Skeleton className="h-8 w-52" />
          </div>
        </div>
        <div className="mt-3 flex items-end gap-2">
          <Skeleton className="h-11 flex-1" />
          <Skeleton className="h-10 w-20" />
        </div>
      </div>
    </AppShell>
  )
}
