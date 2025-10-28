"use client"
import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '@/components/ui/button'

function CodeBlock({ inline, className, children }: any) {
  const [copied, setCopied] = useState(false)
  const code = String(children).replace(/\n$/, '')
  if (inline) {
    return <code className={`rounded bg-muted px-1 py-0.5 ${className || ''}`}>{children}</code>
  }
  const lang = (className || '').replace('language-', '')
  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {}
  }
  return (
    <div className="group relative">
      <pre className="overflow-x-auto rounded-md bg-zinc-950 p-3 text-zinc-50"><code className={className}>{code}</code></pre>
      <div className="absolute right-2 top-2 flex items-center gap-2 text-xs text-muted-foreground">
        {lang && <span className="hidden rounded bg-zinc-800/70 px-2 py-0.5 sm:inline">{lang}</span>}
        <Button size="sm" variant="outline" onClick={onCopy} className="h-7 px-2">
          {copied ? 'Copied' : 'Copy'}
        </Button>
      </div>
    </div>
  )
}

export function Markdown({ text }: { text: string }) {
  return (
    <div className="prose prose-sm max-w-none dark:prose-invert">
      {React.createElement(ReactMarkdown as any, {
        remarkPlugins: [remarkGfm],
        components: { code: CodeBlock as any }
      } as any, text)}
    </div>
  )
}
