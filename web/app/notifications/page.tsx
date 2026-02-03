'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { Notification } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import dynamic from 'next/dynamic'

const BellIcon = dynamic(() => import('lucide-react').then(m => m.Bell), { ssr: false })
const InfoIcon = dynamic(() => import('lucide-react').then(m => m.Info), { ssr: false })
const CheckCircleIcon = dynamic(() => import('lucide-react').then(m => m.CheckCircle), { ssr: false })
const AlertTriangleIcon = dynamic(() => import('lucide-react').then(m => m.AlertTriangle), { ssr: false })

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  useEffect(() => {
    loadNotifications()
  }, [filter])

  const loadNotifications = async () => {
    try {
      const data = await apiClient.get<Notification[]>(`/notifications?unread_only=${filter === 'unread'}`)
      setNotifications(data)
    } catch (error) {
      console.error('Failed to load notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      await apiClient.post(`/notifications/${id}/read`, {})
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="w-5 h-5 text-green-400" />
      case 'warning':
        return <AlertTriangleIcon className="w-5 h-5 text-yellow-400" />
      case 'verse_reminder':
        return <BellIcon className="w-5 h-5 text-purple-400" />
      default:
        return <InfoIcon className="w-5 h-5 text-blue-400" />
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-white/60">Loading notifications...</div>
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
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                  Notifications
                </h1>
                <p className="text-white/60 mt-2">Stay updated with your spiritual journey</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={filter === 'all' ? 'default' : 'outline'}
                  onClick={() => setFilter('all')}
                  size="sm"
                >
                  All
                </Button>
                <Button
                  variant={filter === 'unread' ? 'default' : 'outline'}
                  onClick={() => setFilter('unread')}
                  size="sm"
                >
                  Unread
                </Button>
              </div>
            </div>

            {notifications.length === 0 ? (
              <Card className="bg-white/5 border-white/10 p-12 text-center">
                <BellIcon className="w-16 h-16 mx-auto mb-4 text-white/40" />
                <p className="text-white/60">No notifications to display</p>
              </Card>
            ) : (
              <div className="space-y-3">
                {notifications.map((notification) => (
                  <Card
                    key={notification.id}
                    className={`p-4 border-white/10 transition-colors cursor-pointer ${
                      notification.is_read 
                        ? 'bg-white/5 hover:bg-white/10' 
                        : 'bg-white/10 hover:bg-white/15'
                    }`}
                    onClick={() => !notification.is_read && markAsRead(notification.id)}
                  >
                    <div className="flex items-start gap-3">
                      {getIcon(notification.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="font-semibold text-white">{notification.title}</h3>
                          {!notification.is_read && (
                            <span className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0 mt-2" />
                          )}
                        </div>
                        <p className="text-sm text-white/70 mt-1">{notification.message}</p>
                        <p className="text-xs text-white/50 mt-2">
                          {new Date(notification.created_at).toLocaleString()}
                        </p>
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
