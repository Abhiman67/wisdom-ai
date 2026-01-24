'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { AdminUser } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import dynamic from 'next/dynamic'

const UsersIcon = dynamic(() => import('lucide-react').then(m => m.Users), { ssr: false })
const ShieldIcon = dynamic(() => import('lucide-react').then(m => m.Shield), { ssr: false })
const TrashIcon = dynamic(() => import('lucide-react').then(m => m.Trash2), { ssr: false })
const SearchIcon = dynamic(() => import('lucide-react').then(m => m.Search), { ssr: false })

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async (searchQuery?: string) => {
    try {
      const url = searchQuery ? `/admin/users?search=${searchQuery}` : '/admin/users'
      const data = await apiClient.get<AdminUser[]>(url)
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleAdmin = async (userId: number, currentStatus: boolean) => {
    try {
      await apiClient.put(`/admin/users/${userId}`, { is_admin: !currentStatus })
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_admin: !currentStatus } : u))
    } catch (error) {
      console.error('Failed to update user:', error)
    }
  }

  const deleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return
    
    try {
      await apiClient.delete(`/admin/users/${userId}`)
      setUsers(prev => prev.filter(u => u.id !== userId))
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }

  const handleSearch = () => {
    loadUsers(search)
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6">
              <div className="h-8 w-48 bg-white/10 rounded animate-pulse mb-2"></div>
              <div className="h-4 w-64 bg-white/10 rounded animate-pulse"></div>
            </div>
            
            <div className="mb-6 h-10 w-full max-w-md rounded-lg bg-white/10 animate-pulse"></div>
            
            <div className="grid gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-6 animate-pulse">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <div className="h-5 w-32 bg-white/10 rounded"></div>
                      <div className="h-4 w-48 bg-white/10 rounded"></div>
                      <div className="flex gap-4">
                        <div className="h-4 w-24 bg-white/10 rounded"></div>
                        <div className="h-4 w-24 bg-white/10 rounded"></div>
                        <div className="h-4 w-24 bg-white/10 rounded"></div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <div className="h-9 w-24 bg-white/10 rounded"></div>
                      <div className="h-9 w-9 bg-white/10 rounded"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
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
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                  User Management
                </h1>
                <p className="text-white/60 mt-2">{users.length} total users</p>
              </div>
            </div>

            <Card className="bg-white/5 border-white/10 p-4 mb-6">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                  <Input
                    placeholder="Search by name or email..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="bg-white/5 border-white/10 text-white pl-10"
                  />
                </div>
                <Button onClick={handleSearch}>Search</Button>
              </div>
            </Card>

            <Card className="bg-white/5 border-white/10 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="text-left p-4 text-sm font-semibold text-white/80">User</th>
                      <th className="text-left p-4 text-sm font-semibold text-white/80">Email</th>
                      <th className="text-left p-4 text-sm font-semibold text-white/80">Last Mood</th>
                      <th className="text-left p-4 text-sm font-semibold text-white/80">Joined</th>
                      <th className="text-left p-4 text-sm font-semibold text-white/80">Role</th>
                      <th className="text-right p-4 text-sm font-semibold text-white/80">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-white/5 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <UsersIcon className="w-4 h-4 text-white/40" />
                            <span className="font-medium text-white">{user.name}</span>
                          </div>
                        </td>
                        <td className="p-4 text-white/70">{user.email}</td>
                        <td className="p-4">
                          {user.last_mood ? (
                            <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs">
                              {user.last_mood}
                            </span>
                          ) : (
                            <span className="text-white/40">—</span>
                          )}
                        </td>
                        <td className="p-4 text-white/60 text-sm">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="p-4">
                          {user.is_admin ? (
                            <span className="flex items-center gap-1 text-orange-400">
                              <ShieldIcon className="w-4 h-4" />
                              <span className="text-sm">Admin</span>
                            </span>
                          ) : (
                            <span className="text-white/60 text-sm">User</span>
                          )}
                        </td>
                        <td className="p-4">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => toggleAdmin(user.id, user.is_admin)}
                              disabled={user.is_admin}
                              title={user.is_admin ? "Cannot demote admin" : "Promote to admin"}
                            >
                              {user.is_admin ? 'Admin' : 'Make Admin'}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => deleteUser(user.id)}
                              disabled={user.is_admin}
                              className="text-red-400 hover:text-red-300"
                              title={user.is_admin ? "Cannot delete admin" : "Delete user"}
                            >
                              <TrashIcon className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
