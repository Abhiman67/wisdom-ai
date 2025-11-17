export default function Loading() {
  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      {/* Sidebar Skeleton */}
      <aside className="hidden md:flex w-64 flex-col border-r border-white/10 bg-gradient-to-b from-[#13141f] to-[#0f1019] flex-shrink-0 shadow-2xl">
        <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
          <div className="h-10 w-10 rounded-xl bg-white/10 animate-pulse"></div>
          <div className="flex-1 space-y-2">
            <div className="h-3 w-24 bg-white/10 rounded animate-pulse"></div>
            <div className="h-2 w-16 bg-white/10 rounded animate-pulse"></div>
          </div>
        </div>
        <div className="px-4 pt-5 pb-4">
          <div className="h-11 w-full rounded-xl bg-white/10 animate-pulse"></div>
        </div>
        <div className="px-4 space-y-2 flex-1">
          <div className="h-9 w-full rounded-xl bg-white/5 animate-pulse"></div>
          <div className="h-9 w-full rounded-xl bg-white/5 animate-pulse"></div>
          <div className="h-9 w-full rounded-xl bg-white/5 animate-pulse"></div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8 space-y-2">
              <div className="h-10 w-48 bg-white/10 rounded animate-pulse"></div>
              <div className="h-4 w-64 bg-white/5 rounded animate-pulse"></div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-8 space-y-4">
              <div className="h-6 w-3/4 bg-white/10 rounded animate-pulse"></div>
              <div className="h-4 w-full bg-white/5 rounded animate-pulse"></div>
              <div className="h-4 w-5/6 bg-white/5 rounded animate-pulse"></div>
              <div className="h-4 w-4/5 bg-white/5 rounded animate-pulse"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
