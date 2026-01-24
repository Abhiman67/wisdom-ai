"use client"
import { useEffect, useRef, useState } from 'react'
import { Markdown } from '@/components/chat/markdown'
import { Sidebar } from '@/components/shell/sidebar'
import dynamic from 'next/dynamic'
const SendIcon = dynamic(() => import('lucide-react').then(m => m.Send), { ssr: false })
const SparklesIcon = dynamic(() => import('lucide-react').then(m => m.Sparkles), { ssr: false })

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  type Msg = { role: 'user' | 'ai'; text: string; at: number }
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<Msg[]>([])
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const bottomRef = useRef<HTMLDivElement | null>(null)

  const send = async () => {
    if (!message.trim() || loading) return
    const userText = message.trim()
    
    // Add user message to display
    setHistory(h => [...h, { role: 'user', text: userText, at: Date.now() }])
    setMessage('')
    setLoading(true)
    
    // Build history for context
    const historyForApi = [...chatHistory, { role: 'user' as const, content: userText }]
    
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userText,
          history: historyForApi
        })
      })
      
      const data = await res.json()
      const aiResponse = data.response || data.reply || "I'm having trouble responding right now."
      
      // Update chat history for context
      setChatHistory([
        ...historyForApi,
        { role: 'assistant', content: aiResponse }
      ])
      
      // Add AI response to display
      setHistory(h => [...h, { role: 'ai', text: aiResponse, at: Date.now() }])
    } catch (e) {
      console.error(e)
      setHistory(h => [...h, { role: 'ai', text: "I apologize, but I'm having trouble connecting right now. Please try again.", at: Date.now() }])
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    setHistory([])
    setChatHistory([])
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
      <Sidebar onNewChat={handleNewChat} showNewChatButton={true} />

      {/* Main Chat Area */}
      <main className="flex flex-1 flex-col min-w-0 relative">
        {/* Animated Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
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
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-black flex-shrink-0 shadow-lg ${m.role === 'ai' ? 'bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-orange-500/30' : 'bg-gradient-to-br from-[#3a3a5c] to-[#2d2d4a] text-white shadow-purple-500/20'}`}>
                    {m.role === 'ai' ? 'W' : 'A'}
                  </div>
                  <div className={`group max-w-[75%] rounded-2xl px-5 py-4 shadow-xl backdrop-blur-sm transition-all duration-200 ${m.role === 'user' ? 'bg-gradient-to-br from-[#2d2d50] to-[#25253f] text-white border border-white/5' : 'bg-gradient-to-br from-[#252640] to-[#1f1f35] text-white/90 border border-orange-500/10'}`}>
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
                }}
                autoComplete="off"
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
