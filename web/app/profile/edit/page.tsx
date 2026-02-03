"use client"
import React, { useEffect, useState } from "react"

export default function ProfileEdit() {
  const [name, setName] = useState("")
  const [ragOpt, setRagOpt] = useState(false)
  const [status, setStatus] = useState("")

  useEffect(() => {
    (async () => {
      const res = await fetch('/profile')
      const data = await res.json()
      setName(data.name || '')
      setRagOpt((data.preferences && data.preferences.rag_enabled) || false)
    })()
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('Saving...')
    await fetch('/profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, preferences: { rag_enabled: ragOpt } }) })
    setStatus('Saved')
    setTimeout(()=>setStatus(''), 2000)
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Edit Profile</h1>
      <form onSubmit={submit} className="space-y-4 max-w-lg">
        <div>
          <label className="block text-sm font-medium">Name</label>
          <input className="border p-2 w-full" value={name} onChange={e=>setName(e.target.value)} />
        </div>
        <div className="flex items-center gap-3">
          <input id="rag" type="checkbox" checked={ragOpt} onChange={e=>setRagOpt(e.target.checked)} />
          <label htmlFor="rag" className="text-sm">Enable RAG by default</label>
        </div>
        <div>
          <button className="bg-blue-600 text-white px-4 py-2">Save</button>
          <span className="ml-3 text-sm text-gray-600">{status}</span>
        </div>
      </form>
    </div>
  )
}
