"use client"
import { useEffect, useRef, useState } from 'react'
import { apiClient } from '@/lib/api'
import { ChatResponse } from '@/types/api'
import { AppShell } from '@/components/shell/app-shell'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Markdown } from '@/components/chat/markdown'
import dynamic from 'next/dynamic'
const CopyIcon = dynamic(() => import('lucide-react').then(m => m.Copy), { ssr: false })
const CheckIcon = dynamic(() => import('lucide-react').then(m => m.Check), { ssr: false })
const SendIcon = dynamic(() => import('lucide-react').then(m => m.Send), { ssr: false })

export default function ChatPage() {
  // minimal message type for local component
  type Msg = { role: 'user' | 'ai'; text: string; at: number }
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<Msg[]>([])
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  const send = async () => {
    if (!message.trim()) return
    const userText = message
    setHistory(h => [...h, { role: 'user', text: userText, at: Date.now() }])
    setMessage('')
    try {
      setLoading(true)
      const res = await apiClient.post<ChatResponse>('/chat', { message: userText })
      const combined = `${res.reply}\n\n— ${res.verse_source}`
      setHistory(h => [...h, { role: 'ai', text: combined, at: Date.now() }])
    } catch (e) {
      console.error(e)
      alert('Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, loading])

  const copyMessage = async (i: number, text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedIndex(i)
      setTimeout(() => setCopiedIndex(null), 1500)
    } catch {}
  }

  const formatTime = (ts: number) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  const suggestions = [
    'Share a verse about hope',
    'Help me calm anxiety',
    'Daily wisdom for today',
    'Encouragement for tough times'
  ]

  return (
    <AppShell>
      <div className="container flex h-[calc(100vh-64px)] items-center justify-center py-8">
        <div className="w-full max-w-4xl flex flex-col gap-4">
          <div className="rounded-2xl bg-card/70 border p-4 shadow-lg backdrop-blur">
              <div className="flex items-center justify-between px-2 pb-2">
              <div>
                <h2 className="text-lg font-semibold">Ask Wisdom AI</h2>
                <p className="text-sm text-muted-foreground">Thoughtful guidance with contextual verses.</p>
              </div>
            </div>

            <div className="relative">
              <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/5 via-transparent to-transparent" />
              <div className="flex h-[60vh] flex-col space-y-4 overflow-y-auto p-4">
                {history.length === 0 && (
                    <div className="mx-auto max-w-2xl text-center">
                    <h3 className="mb-2 text-lg font-semibold">Start a conversation</h3>
                    <p className="mb-4 text-sm text-muted-foreground">Ask for guidance and receive supportive verses.</p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {suggestions.map((s) => (
                        <button key={s} type="button" onClick={() => setMessage(s)} className="chat-chip bg-muted/80 hover:bg-muted/90">{s}</button>
                      ))}
                    </div>
                  </div>
                )}

                {history.map((m, i) => (
                  <div key={i} className={`group flex items-start gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {m.role === 'ai' && (
                      <div className="mt-1 flex h-9 w-9 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold text-white">AI</div>
                    )}
                    <div className={`inline-block max-w-[80%] rounded-2xl px-4 py-3 shadow-sm animate-fade-in ${m.role === 'user' ? 'bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white rounded-br-md' : 'bg-muted text-muted-foreground rounded-bl-md'}`}>
                      {m.role === 'ai' ? (
                        <Markdown text={m.text} />
                      ) : (
                        <div className="whitespace-pre-wrap">{m.text}</div>
                      )}
                      <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                        <span>{formatTime(m.at)}</span>
                        {m.role === 'ai' && (
                          <button
                            type="button"
                            onClick={() => copyMessage(i, m.text)}
                            className="inline-flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                            title="Copy"
                            aria-label="Copy AI message"
                          >
                            {copiedIndex === i ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                          </button>
                        )}
                      </div>
                    </div>
                    {m.role === 'user' && (
                      <div className="mt-1 flex h-9 w-9 items-center justify-center rounded-full bg-zinc-700 text-xs font-semibold text-white">You</div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-muted-foreground/70" />
                    Thinking…
                  </div>
                )}

                <div ref={bottomRef} />
              </div>
            </div>
          </div>

          <form className="mt-4 flex items-end gap-2 sticky bottom-6 z-30 p-3 rounded-2xl shadow-lg border backdrop-card" onSubmit={e => { e.preventDefault(); send(); }}>
            <div className="flex-1">
              <Textarea
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Write a message…"
                className="min-h-[48px] w-full"
                rows={2}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
              />
            </div>

            <div className="flex-shrink-0 flex items-center">
              <Button type="submit" disabled={loading} aria-label="Send message" className="h-10 w-10 p-0 rounded-full">
                {loading ? '…' : <SendIcon className="h-5 w-5" />}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </AppShell>
  )
}
