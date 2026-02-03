'use client'
import { useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { ChatResponse } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

const Sparkles = dynamic(() => import('lucide-react').then(m => m.Sparkles), { ssr: false })
const Database = dynamic(() => import('lucide-react').then(m => m.Database), { ssr: false })
const Zap = dynamic(() => import('lucide-react').then(m => m.Zap), { ssr: false })

export default function AdminComparisonPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [withRag, setWithRag] = useState<ChatResponse | null>(null)
  const [withoutRag, setWithoutRag] = useState<ChatResponse | null>(null)

  const runComparison = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    setWithRag(null)
    setWithoutRag(null)

    try {
      const [ragResponse, noRagResponse] = await Promise.all([
        apiClient.post<ChatResponse>('/chat', {
          message: query,
          rag: true,
          persona: true,
          max_new_tokens: 300,
          temperature: 0.6,
        }),
        apiClient.post<ChatResponse>('/chat', {
          message: query,
          rag: false,
          persona: true,
          max_new_tokens: 300,
          temperature: 0.6,
        })
      ])
      
      setWithRag(ragResponse)
      setWithoutRag(noRagResponse)
    } catch (error) {
      console.error('Comparison failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />
      
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent mb-2">
                RAG Comparison Tool
              </h1>
              <p className="text-white/60">
                Compare model responses with and without RAG context retrieval
              </p>
            </div>

            <Card className="bg-white/5 border-white/10 p-6 mb-6">
              <label className="block text-sm font-medium text-white/80 mb-3">
                Test Query
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about the Bhagavad Gita..."
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-orange-500/50 resize-none"
                rows={3}
              />
              
              <Button
                onClick={runComparison}
                disabled={loading || !query.trim()}
                className="mt-4 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 text-white font-medium px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <>
                    <Zap className="w-4 h-4 mr-2 animate-pulse" />
                    Running Comparison...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Compare Responses
                  </>
                )}
              </Button>
            </Card>

            {(withRag || withoutRag) && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* RAG ON */}
                <Card className="bg-gradient-to-br from-orange-500/10 to-orange-500/5 border-orange-500/20 p-6">
                  <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/10">
                    <Database className="w-5 h-5 text-orange-400" />
                    <h3 className="text-lg font-semibold text-white">RAG Enabled</h3>
                    <span className="ml-auto text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded">
                      WITH CONTEXT
                    </span>
                  </div>

                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="animate-pulse text-white/60">Loading...</div>
                    </div>
                  ) : withRag ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-white/60 mb-2">Response:</p>
                        <p className="text-white/90 leading-relaxed">{withRag.reply}</p>
                      </div>
                      
                      {withRag.verse_id && (
                        <div className="mt-4 pt-4 border-t border-white/10">
                          <p className="text-xs text-white/60 mb-2">Context Used:</p>
                          <div className="bg-white/5 rounded-lg p-3">
                            <p className="text-xs text-orange-400 font-medium mb-1">
                              {withRag.verse_source}
                            </p>
                            <p className="text-sm text-white/80">{withRag.verse_text}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex gap-2 text-xs text-white/60">
                        <span>Mood: {withRag.detected_mood}</span>
                      </div>
                    </div>
                  ) : null}
                </Card>

                {/* RAG OFF */}
                <Card className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20 p-6">
                  <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/10">
                    <Zap className="w-5 h-5 text-purple-400" />
                    <h3 className="text-lg font-semibold text-white">RAG Disabled</h3>
                    <span className="ml-auto text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                      NO CONTEXT
                    </span>
                  </div>

                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="animate-pulse text-white/60">Loading...</div>
                    </div>
                  ) : withoutRag ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-white/60 mb-2">Response:</p>
                        <p className="text-white/90 leading-relaxed">{withoutRag.reply}</p>
                      </div>

                      {withoutRag.verse_id && (
                        <div className="mt-4 pt-4 border-t border-white/10">
                          <p className="text-xs text-white/60 mb-2">Context Used:</p>
                          <div className="bg-white/5 rounded-lg p-3">
                            <p className="text-xs text-purple-400 font-medium mb-1">
                              {withoutRag.verse_source}
                            </p>
                            <p className="text-sm text-white/80">{withoutRag.verse_text}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex gap-2 text-xs text-white/60">
                        <span>Mood: {withoutRag.detected_mood}</span>
                      </div>
                    </div>
                  ) : null}
                </Card>
              </div>
            )}

            {!loading && !withRag && !withoutRag && (
              <Card className="bg-white/5 border-white/10 p-12 text-center">
                <Sparkles className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/60">
                  Enter a query above and click &quot;Compare Responses&quot; to see the difference
                </p>
              </Card>
            )}

            <Card className="bg-white/5 border-white/10 p-6 mt-6">
              <h3 className="text-lg font-semibold mb-3 text-white">Understanding the Comparison</h3>
              <div className="space-y-3 text-sm text-white/70">
                <div className="flex gap-3">
                  <Database className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white">RAG Enabled:</strong> Retrieves relevant passages from your Gita dataset, 
                    then feeds them as context to Mistral-7B + LoRA. More grounded, factually accurate responses with verse citations.
                  </div>
                </div>
                <div className="flex gap-3">
                  <Zap className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white">RAG Disabled:</strong> Uses only Mistral-7B + your fine-tuned LoRA adapter 
                    without external context. May hallucinate or provide more general knowledge-based answers.
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
