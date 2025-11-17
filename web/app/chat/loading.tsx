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
        <div className="flex-1 flex items-center justify-center p-8 relative z-10">
          <div className="text-center">
            <div className="h-16 w-16 mx-auto rounded-2xl bg-orange-500/20 animate-pulse mb-4"></div>
            <div className="h-6 w-48 mx-auto bg-white/10 rounded animate-pulse mb-2"></div>
            <div className="h-4 w-64 mx-auto bg-white/5 rounded animate-pulse"></div>
          </div>
        </div>
      </main>
    </div>
  )
}
