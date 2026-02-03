"use client"
import { useEffect, useRef, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { ChatResponse } from '@/types/api'
import { Markdown } from '@/components/chat/markdown'
import { Sidebar } from '@/components/shell/sidebar'
import dynamic from 'next/dynamic'
const SendIcon = dynamic(() => import('lucide-react').then(m => m.Send), { ssr: false })
const SparklesIcon = dynamic(() => import('lucide-react').then(m => m.Sparkles), { ssr: false })
const LoaderIcon = dynamic(() => import('lucide-react').then(m => m.Loader2), { ssr: false })

// Inner component that uses useSearchParams
function ChatContent() {
  type Msg = { role: 'user' | 'ai'; text: string; at: number; error?: boolean }
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<Msg[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const bottomRef = useRef<HTMLDivElement | null>(null)
  
  const searchParams = useSearchParams()
  const router = useRouter()
  const chatId = searchParams.get('chatId')

  // Load previous chat if chatId is present
  useEffect(() => {
    if (!chatId) {
      console.log('[ChatPage] No chatId, showing empty chat')
      return
    }
    
    console.log('[ChatPage] Loading chat history for chatId:', chatId)
    setLoadingHistory(true)
    
    fetch(`/api/chat-history?chatId=${chatId}`, {
      cache: 'no-store',
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Failed to load chat: ${res.status}`)
        }
        const data = await res.json()
        console.log('[ChatPage] Loaded chat data:', data)
        
        if (data && data.question) {
          const loadedHistory: Msg[] = [
            { role: 'user', text: data.question, at: new Date(data.created_at).getTime() }
          ]
          
          // Check if response exists and has answer
          if (data.response && data.response.answer) {
            let answerText = data.response.answer
            // Add verse source if available
            if (data.response.verse_source) {
              answerText += `\n\n— ${data.response.verse_source}`
            }
            loadedHistory.push({
              role: 'ai',
              text: answerText,
              at: new Date(data.response.created_at || data.created_at).getTime()
            })
          }
          
          setHistory(loadedHistory)
          console.log('[ChatPage] Loaded history with', loadedHistory.length, 'messages')
        }
      })
      .catch((err) => {
        console.error('[ChatPage] Error loading chat history:', err)
        setError('Failed to load previous chat')
      })
      .finally(() => {
        setLoadingHistory(false)
      })
  }, [chatId])

  // Function to start a new chat
  const startNewChat = () => {
    setHistory([])
    setMessage('')
    setError(null)
    // Remove chatId from URL
    router.push('/chat')
  }

  const send = async (retryMsg?: string) => {
    const userText = retryMsg || message
    if (!userText.trim()) return
    
    if (!retryMsg) {
      setHistory(h => [...h, { role: 'user', text: userText, at: Date.now() }])
      setMessage('')
    }
    
    setError(null)
    try {
      setLoading(true)
      const res = await apiClient.post<ChatResponse>('/chat', { message: userText })
      const combined = res.verse_source ? `${res.reply}\n\n— ${res.verse_source}` : res.reply
      setHistory(h => [...h, { role: 'ai', text: combined, at: Date.now() }])
    } catch (e) {
      console.error('Chat error:', e)
      const errMsg = e instanceof Error ? e.message : 'Failed to send message'
      setError(errMsg)
      setHistory(h => [...h, { role: 'ai', text: 'Sorry, I encountered an error. Please try again.', at: Date.now(), error: true }])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, loading])

  const suggestions = [
    { emoji: '🕯️', text: 'What brings inner peace?' },
    { emoji: '💡', text: 'How to find purpose?' },
    { emoji: '📖', text: 'Share a spiritual insight' },
    { emoji: '🌱', text: 'Guide me through challenges' }
  ]

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar onNewChat={startNewChat} showNewChatButton={true} />

      {/* Main Chat Area */}
      <main className="flex flex-1 flex-col min-w-0 relative">
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        {/* Loading History Overlay */}
        {loadingHistory && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-[#1a1b2e]/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-3">
              <LoaderIcon className="h-8 w-8 text-orange-400 animate-spin" />
              <p className="text-sm text-white/60">Loading conversation...</p>
            </div>
          </div>
        )}
        
        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 md:py-8 relative z-10">
          {history.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center max-w-3xl mx-auto text-center px-4">
              {/* Animated Logo */}
              <div className="relative mb-3">
                <div className="absolute inset-0 bg-orange-500/20 blur-2xl rounded-full animate-pulse"></div>
                <div className="relative h-14 w-14 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-2xl font-black shadow-2xl shadow-orange-500/30 transform hover:scale-110 transition-transform duration-300">
                  W
                </div>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-black mb-2 bg-gradient-to-r from-white via-orange-200 to-white bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-4 duration-700">Hello there!</h1>
              <p className="text-sm md:text-base text-white/60 mb-5 animate-in fade-in slide-in-from-bottom-4 duration-700" style={{animationDelay: '100ms'}}>How can I help you today?</p>

              {/* Highlight Card */}
              <div className="mb-5 rounded-xl border border-orange-500/30 bg-gradient-to-br from-[#2a2440]/80 to-[#1f1a36]/60 p-3 max-w-md w-full backdrop-blur-xl shadow-xl shadow-orange-500/10 animate-in fade-in slide-in-from-bottom-4 duration-700 hover:scale-[1.02] transition-transform" style={{animationDelay: '200ms'}}>
                <div className="flex items-center gap-2 text-orange-400 font-bold mb-1.5">
                  <div className="h-6 w-6 rounded-lg bg-orange-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm">✨</span>
                  </div>
                  <span className="text-xs">Wisdom is a text away!</span>
                </div>
                <p className="text-[11px] text-white/70 leading-relaxed">Receive personalized spiritual guidance whenever you need it.</p>
              </div>

              {/* Suggestion Cards */}
              <div className="grid grid-cols-2 gap-2.5 w-full max-w-xl">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => setMessage(s.text)}
                    className="group relative flex flex-col items-start gap-1.5 rounded-lg border border-white/10 bg-gradient-to-br from-[#252640]/90 to-[#1f1f3a]/70 p-3 text-left transition-all duration-300 hover:border-orange-500/30 hover:shadow-lg hover:shadow-orange-500/10 hover:scale-[1.02] active:scale-[0.98] backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4"
                    style={{animationDelay: `${300 + idx * 50}ms`}}
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-500/0 to-orange-500/0 group-hover:from-orange-500/5 group-hover:to-transparent rounded-lg transition-all duration-300"></div>
                    <div className="relative z-10 h-7 w-7 rounded-lg bg-orange-500/10 flex items-center justify-center text-lg group-hover:scale-110 transition-transform duration-300">
                      {s.emoji}
                    </div>
                    <span className="relative z-10 text-[11px] font-semibold text-white/90 leading-tight group-hover:text-white transition-colors">{s.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6 pb-4">
              {history.map((m, i) => (
                <div key={i} className={`flex items-start gap-4 ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-in fade-in slide-in-from-bottom-2 duration-500`}>
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-black flex-shrink-0 shadow-lg ${m.role === 'ai' ? m.error ? 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-red-500/30' : 'bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-orange-500/30' : 'bg-gradient-to-br from-[#3a3a5c] to-[#2d2d4a] text-white shadow-purple-500/20'}`}>
                    {m.role === 'ai' ? 'W' : 'A'}
                  </div>
                  <div className={`group max-w-[75%] rounded-2xl px-5 py-4 shadow-xl backdrop-blur-sm transition-all duration-200 ${m.role === 'user' ? 'bg-gradient-to-br from-[#2d2d50] to-[#25253f] text-white border border-white/5' : m.error ? 'bg-gradient-to-br from-red-500/20 to-red-900/20 text-white/90 border border-red-500/30' : 'bg-gradient-to-br from-[#252640] to-[#1f1f35] text-white/90 border border-orange-500/10'}`}>
                    {m.role === 'ai' ? (
                      <div className="prose prose-sm prose-invert max-w-none [&>p]:leading-relaxed [&>p]:text-white/90">
                        <Markdown text={m.text} />
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap text-sm leading-relaxed font-medium">{m.text}</div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-4 animate-in fade-in duration-300">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 text-sm font-black shadow-lg shadow-orange-500/30">W</div>
                  <div className="flex items-center gap-2 bg-gradient-to-r from-[#252640] to-[#1f1f35] rounded-2xl px-5 py-3 shadow-lg border border-orange-500/10">
                    <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-gradient-to-br from-orange-400 to-orange-500 shadow-lg shadow-orange-500/50" style={{ animationDelay: '0ms' }} />
                    <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-gradient-to-br from-orange-400 to-orange-500 shadow-lg shadow-orange-500/50" style={{ animationDelay: '150ms' }} />
                    <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-gradient-to-br from-orange-400 to-orange-500 shadow-lg shadow-orange-500/50" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-white/10 bg-gradient-to-b from-[#13141f]/95 to-[#0f1019]/95 backdrop-blur-xl px-4 md:px-6 py-5 md:py-6 flex-shrink-0 shadow-2xl">
          <form onSubmit={e => { e.preventDefault(); send(); }} className="max-w-4xl mx-auto">
            <div className="group relative flex items-center gap-3 rounded-2xl border border-white/10 bg-gradient-to-br from-[#1f2037] to-[#181828] p-4 shadow-2xl transition-all duration-300 focus-within:border-orange-500/50 focus-within:shadow-orange-500/20 hover:border-white/20">
              {/* Glow effect on focus */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl opacity-0 group-focus-within:opacity-20 blur transition duration-300"></div>
              
              <input
                type="text"
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Send a message..."
                className="relative z-10 flex-1 bg-transparent text-sm md:text-base text-white placeholder:text-white/40 outline-none font-medium"
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                  if (e.key === 'Escape') {
                    setMessage('');
                  }
                }}
                autoComplete="off"
                disabled={loading}
                aria-label="Message input"
              />
              <button
                type="submit"
                disabled={loading || !message.trim()}
                className="relative z-10 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 text-white transition-all duration-300 hover:shadow-xl hover:shadow-orange-500/50 hover:scale-110 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:scale-100 flex-shrink-0 active:scale-95 group"
                aria-label="Send message"
              >
                <SendIcon className="h-5 w-5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </button>
            </div>
            <p className="mt-4 text-center text-[11px] md:text-xs text-white/30 px-2 font-medium">
              <span className="inline-flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-orange-500/50 animate-pulse"></span>
                Wisdom AI can make mistakes. Consider checking important information.
              </span>
            </p>
          </form>
        </div>
      </main>
    </div>
  )
}

// Loading fallback for Suspense
function ChatLoadingFallback() {
  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <LoaderIcon className="h-8 w-8 text-orange-400 animate-spin" />
        <p className="text-sm text-white/60">Loading chat...</p>
      </div>
    </div>
  )
}

// Main export with Suspense boundary for useSearchParams
export default function ChatPage() {
  return (
    <Suspense fallback={<ChatLoadingFallback />}>
      <ChatContent />
    </Suspense>
  )
}
