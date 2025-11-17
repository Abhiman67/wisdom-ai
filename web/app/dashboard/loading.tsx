export default function Loading() {
  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36]">
      <div className="text-center">
        <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent"></div>
        <p className="text-sm text-white/60">Loading your dashboard...</p>
      </div>
    </div>
  )
}
