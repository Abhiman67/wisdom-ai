'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { FlaggedComment } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

const AlertTriangleIcon = dynamic(() => import('lucide-react').then(m => m.AlertTriangle), { ssr: false })
const CheckIcon = dynamic(() => import('lucide-react').then(m => m.Check), { ssr: false })
const XIcon = dynamic(() => import('lucide-react').then(m => m.X), { ssr: false })

export default function AdminModerationPage() {
  const [flaggedComments, setFlaggedComments] = useState<FlaggedComment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFlaggedContent()
  }, [])

  const loadFlaggedContent = async () => {
    try {
      const data = await apiClient.get<FlaggedComment[]>('/admin/moderation/flagged')
      setFlaggedComments(data)
    } catch (error) {
      console.error('Failed to load flagged content:', error)
    } finally {
      setLoading(false)
    }
  }

  const approveComment = async (id: number) => {
    try {
      await apiClient.post(`/admin/moderation/${id}/approve`, {})
      setFlaggedComments(prev => prev.filter(c => c.id !== id))
    } catch (error) {
      console.error('Failed to approve comment:', error)
    }
  }

  const deleteComment = async (id: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return
    
    try {
      await apiClient.delete(`/admin/moderation/${id}/delete`)
      setFlaggedComments(prev => prev.filter(c => c.id !== id))
    } catch (error) {
      console.error('Failed to delete comment:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-white/60">Loading moderation queue...</div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />
      
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-5xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                Content Moderation
              </h1>
              <p className="text-white/60 mt-2">{flaggedComments.length} items pending review</p>
            </div>

            {flaggedComments.length === 0 ? (
              <Card className="bg-white/5 border-white/10 p-12 text-center">
                <CheckIcon className="w-16 h-16 mx-auto mb-4 text-green-400" />
                <p className="text-white/60">No flagged content to review</p>
              </Card>
            ) : (
              <div className="space-y-4">
                {flaggedComments.map((comment) => (
                  <Card key={comment.id} className="bg-white/5 border-white/10 p-6">
                    <div className="flex items-start gap-4">
                      <AlertTriangleIcon className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div>
                            <p className="text-sm text-white/60">
                              Comment by <span className="text-white font-medium">{comment.user_name}</span> ({comment.user_email})
                            </p>
                            <p className="text-sm text-white/60 mt-1">
                              On verse: <span className="text-purple-400">{comment.verse_id}</span>
                            </p>
                          </div>
                          <span className="text-xs text-white/50">
                            {new Date(comment.created_at).toLocaleString()}
                          </span>
                        </div>
                        
                        <div className="bg-white/5 rounded-lg p-4 mb-4">
                          <p className="text-white/90">{comment.comment}</p>
                        </div>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => approveComment(comment.id)}
                            className="bg-green-500/20 text-green-400 hover:bg-green-500/30"
                          >
                            <CheckIcon className="w-4 h-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deleteComment(comment.id)}
                            className="text-red-400 hover:text-red-300 border-red-400/20"
                          >
                            <XIcon className="w-4 h-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
