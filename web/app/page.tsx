'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  
  useEffect(() => {
    // Check if user is authenticated
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/profile')
        if (res.ok) {
          // User is authenticated, go to dashboard
          router.push('/dashboard')
        } else {
          // Not authenticated, go to welcome
          router.push('/welcome')
        }
      } catch {
        router.push('/welcome')
      }
    }
    
    checkAuth()
  }, [router])
  
  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36]">
      <div className="text-center">
        <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent"></div>
        <p className="text-sm text-white/60">Loading...</p>
      </div>
    </div>
  )
}
