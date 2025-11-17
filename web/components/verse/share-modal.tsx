'use client'
import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { ShareResponse } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

const ShareIcon = dynamic(() => import('lucide-react').then(m => m.Share2), { ssr: false })
const CopyIcon = dynamic(() => import('lucide-react').then(m => m.Copy), { ssr: false })
const CheckIcon = dynamic(() => import('lucide-react').then(m => m.Check), { ssr: false })

interface ShareModalProps {
  verseId: string
  verseText: string
  source: string
  onClose: () => void
}

export function ShareModal({ verseId, verseText, source, onClose }: ShareModalProps) {
  const [shareData, setShareData] = useState<ShareResponse | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)

  const generateShareLink = async () => {
    setLoading(true)
    try {
      const data = await apiClient.post<ShareResponse>(`/verses/${verseId}/share`, {})
      setShareData(data)
    } catch (error) {
      console.error('Failed to generate share link:', error)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    if (shareData) {
      navigator.clipboard.writeText(shareData.share_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <Card className="bg-[#1a1b2e] border-white/10 p-6 max-w-2xl w-full" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-3 mb-4">
          <ShareIcon className="w-6 h-6 text-orange-400" />
          <h2 className="text-2xl font-bold text-white">Share Verse</h2>
        </div>

        <div className="bg-white/5 rounded-lg p-4 mb-6">
          <p className="text-white/90 mb-2">{verseText}</p>
          <p className="text-sm text-white/60">— {source}</p>
        </div>

        {!shareData ? (
          <Button 
            onClick={generateShareLink} 
            disabled={loading}
            className="w-full bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700"
          >
            {loading ? 'Generating Link...' : 'Generate Shareable Link'}
          </Button>
        ) : (
          <div className="space-y-4">
            <div className="bg-white/5 rounded-lg p-4">
              <p className="text-sm text-white/60 mb-2">Shareable Link:</p>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={shareData.share_url}
                  readOnly
                  className="flex-1 bg-white/10 border border-white/20 rounded px-3 py-2 text-white text-sm"
                />
                <Button onClick={copyToClipboard} size="sm">
                  {copied ? <CheckIcon className="w-4 h-4" /> : <CopyIcon className="w-4 h-4" />}
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button
                onClick={() => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(verseText + ' - ' + source)}&url=${encodeURIComponent(shareData.share_url)}`, '_blank')}
                className="bg-[#1DA1F2] hover:bg-[#1a8cd8]"
              >
                Share on Twitter
              </Button>
              <Button
                onClick={() => window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareData.share_url)}`, '_blank')}
                className="bg-[#1877F2] hover:bg-[#166fe5]"
              >
                Share on Facebook
              </Button>
            </div>
          </div>
        )}

        <Button variant="outline" onClick={onClose} className="w-full mt-4">
          Close
        </Button>
      </Card>
    </div>
  )
}
