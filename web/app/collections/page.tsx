'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { Collection, CollectionDetail } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import dynamic from 'next/dynamic'

const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })
const PlusIcon = dynamic(() => import('lucide-react').then(m => m.Plus), { ssr: false })
const FolderIcon = dynamic(() => import('lucide-react').then(m => m.Folder), { ssr: false })

export default function CollectionsPage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<CollectionDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newCollection, setNewCollection] = useState({ name: '', description: '', is_public: false })

  useEffect(() => {
    loadCollections()
  }, [])

  const loadCollections = async () => {
    try {
      const data = await apiClient.get<Collection[]>('/collections')
      setCollections(data)
    } catch (error) {
      console.error('Failed to load collections:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCollectionDetails = async (id: number) => {
    try {
      const data = await apiClient.get<CollectionDetail>(`/collections/${id}`)
      setSelectedCollection(data)
    } catch (error) {
      console.error('Failed to load collection details:', error)
    }
  }

  const createCollection = async () => {
    try {
      await apiClient.post('/collections', newCollection)
      setNewCollection({ name: '', description: '', is_public: false })
      setShowCreateForm(false)
      loadCollections()
    } catch (error) {
      console.error('Failed to create collection:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-white/60">Loading collections...</div>
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
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                  Verse Collections
                </h1>
                <p className="text-white/60 mt-2">Organize your favorite verses into collections</p>
              </div>
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                New Collection
              </Button>
            </div>

            {showCreateForm && (
              <Card className="bg-white/5 border-white/10 p-6 mb-6">
                <h3 className="text-lg font-semibold mb-4">Create New Collection</h3>
                <div className="space-y-4">
                  <Input
                    placeholder="Collection Name"
                    value={newCollection.name}
                    onChange={(e) => setNewCollection({ ...newCollection, name: e.target.value })}
                    className="bg-white/5 border-white/10 text-white"
                  />
                  <Textarea
                    placeholder="Description (optional)"
                    value={newCollection.description}
                    onChange={(e) => setNewCollection({ ...newCollection, description: e.target.value })}
                    className="bg-white/5 border-white/10 text-white"
                  />
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={newCollection.is_public}
                      onChange={(e) => setNewCollection({ ...newCollection, is_public: e.target.checked })}
                      className="rounded"
                    />
                    <label className="text-sm text-white/80">Make this collection public</label>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={createCollection}>Create Collection</Button>
                    <Button variant="outline" onClick={() => setShowCreateForm(false)}>Cancel</Button>
                  </div>
                </div>
              </Card>
            )}

            {collections.length === 0 ? (
              <Card className="bg-white/5 border-white/10 p-12 text-center">
                <FolderIcon className="w-16 h-16 mx-auto mb-4 text-white/40" />
                <p className="text-white/60 mb-4">You haven&apos;t created any collections yet</p>
                <Button onClick={() => setShowCreateForm(true)}>Create Your First Collection</Button>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {collections.map((collection) => (
                  <Card
                    key={collection.id}
                    className="bg-white/5 border-white/10 p-6 cursor-pointer hover:bg-white/10 transition-colors"
                    onClick={() => loadCollectionDetails(collection.id)}
                  >
                    <div className="flex items-start gap-3 mb-3">
                      <BookmarkIcon className="w-6 h-6 text-orange-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-white truncate">{collection.name}</h3>
                        {collection.description && (
                          <p className="text-sm text-white/60 mt-1 line-clamp-2">{collection.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-white/60">
                      <span>{collection.verse_count} verses</span>
                      {collection.is_public && <span className="text-purple-400">Public</span>}
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {selectedCollection && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50" onClick={() => setSelectedCollection(null)}>
                <Card className="bg-[#1a1b2e] border-white/10 p-6 max-w-3xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-white">{selectedCollection.name}</h2>
                      {selectedCollection.description && (
                        <p className="text-white/60 mt-2">{selectedCollection.description}</p>
                      )}
                    </div>
                    <Button variant="outline" onClick={() => setSelectedCollection(null)}>Close</Button>
                  </div>
                  
                  <div className="space-y-4">
                    {selectedCollection.verses.map((verse, idx) => (
                      <Card key={idx} className="bg-white/5 border-white/10 p-4">
                        <p className="text-white/90 mb-2">{verse.text}</p>
                        <p className="text-sm text-white/60">— {verse.source}</p>
                      </Card>
                    ))}
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
