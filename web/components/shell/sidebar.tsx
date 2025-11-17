"use client"
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import { apiClient } from '@/lib/api'

const HomeIcon = dynamic(() => import('lucide-react').then(m => m.Home), { ssr: false })
const BookOpenIcon = dynamic(() => import('lucide-react').then(m => m.BookOpen), { ssr: false })
const MessageSquareIcon = dynamic(() => import('lucide-react').then(m => m.MessageSquare), { ssr: false })
const BookmarkIcon = dynamic(() => import('lucide-react').then(m => m.Bookmark), { ssr: false })
const FolderIcon = dynamic(() => import('lucide-react').then(m => m.Folder), { ssr: false })
const CalendarIcon = dynamic(() => import('lucide-react').then(m => m.Calendar), { ssr: false })
const BellIcon = dynamic(() => import('lucide-react').then(m => m.Bell), { ssr: false })
const UsersIcon = dynamic(() => import('lucide-react').then(m => m.Users), { ssr: false })
const ShieldIcon = dynamic(() => import('lucide-react').then(m => m.Shield), { ssr: false })
const TrendingUpIcon = dynamic(() => import('lucide-react').then(m => m.TrendingUp), { ssr: false })
const SettingsIcon = dynamic(() => import('lucide-react').then(m => m.Settings), { ssr: false })
const LogOutIcon = dynamic(() => import('lucide-react').then(m => m.LogOut), { ssr: false })
const PlusIcon = dynamic(() => import('lucide-react').then(m => m.Plus), { ssr: false })
const SparklesIcon = dynamic(() => import('lucide-react').then(m => m.Sparkles), { ssr: false })

interface SidebarProps {
  userName?: string
  userEmail?: string
  onNewChat?: () => void
  showNewChatButton?: boolean
}

export function Sidebar({ userName = "User", userEmail = "", onNewChat, showNewChatButton = false }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await apiClient.post('/logout')
      router.push('/welcome')
    } catch (e) {
      console.error('Logout failed:', e)
      router.push('/welcome')
    }
  }

  const navItems = [
    { href: '/', icon: HomeIcon, label: 'Home' },
    { href: '/daily-verse', icon: BookOpenIcon, label: 'Daily Verses' },
    { href: '/chat', icon: MessageSquareIcon, label: 'Chat' },
    { href: '/saved', icon: BookmarkIcon, label: 'Saved Verses' },
    { href: '/collections', icon: FolderIcon, label: 'Collections' },
    { href: '/reading-plans', icon: CalendarIcon, label: 'Reading Plans' },
    { href: '/notifications', icon: BellIcon, label: 'Notifications' },
  ]

  const adminItems = [
    { href: '/admin', icon: SettingsIcon, label: 'Admin Dashboard' },
    { href: '/admin/users', icon: UsersIcon, label: 'User Management' },
    { href: '/admin/moderation', icon: ShieldIcon, label: 'Moderation' },
    { href: '/admin/analytics', icon: TrendingUpIcon, label: 'Analytics' },
  ]

  const isActive = (href: string) => pathname === href

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-white/10 bg-gradient-to-b from-[#13141f] to-[#0f1019] flex-shrink-0 shadow-2xl">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10 bg-gradient-to-r from-orange-500/5 to-transparent">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 text-base font-black shadow-lg shadow-orange-500/30">
          <span className="relative z-10">W</span>
          <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/20 to-transparent"></div>
        </div>
        <div>
          <span className="font-bold text-base tracking-tight block">Wisdom AI</span>
          <span className="text-[10px] text-orange-400 font-medium">AI Assistant</span>
        </div>
      </div>

      {/* New Chat Button */}
      {showNewChatButton && (
        <div className="px-4 pt-5 pb-4">
          <button
            onClick={onNewChat}
            className="group relative w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all duration-200 hover:shadow-xl hover:shadow-orange-500/40 hover:scale-[1.02] active:scale-[0.98] overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <PlusIcon className="h-4 w-4 relative z-10" />
            <span className="relative z-10">New Chat</span>
          </button>
        </div>
      )}

      {!showNewChatButton && (
        <div className="px-4 pt-5 pb-4">
          <Link
            href="/chat"
            className="group relative w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all duration-200 hover:shadow-xl hover:shadow-orange-500/40 hover:scale-[1.02] active:scale-[0.98] overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <PlusIcon className="h-4 w-4 relative z-10" />
            <span className="relative z-10">New Chat</span>
          </Link>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-4 py-2">
        <div className="mb-3 text-[10px] font-bold uppercase tracking-widest text-white/30">Navigation</div>
        <div className="space-y-1.5">
          {navItems.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className={`group flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-200 ${
                isActive(href)
                  ? 'text-white bg-orange-500/5 border border-orange-500/20'
                  : 'text-white/70 hover:bg-gradient-to-r hover:from-orange-500/10 hover:to-transparent hover:text-white hover:pl-5'
              }`}
            >
              <Icon className={`h-4 w-4 flex-shrink-0 ${!isActive(href) && 'transition-transform group-hover:scale-110'}`} />
              <span>{label}</span>
            </Link>
          ))}
        </div>

        {/* Admin Section */}
        <div className="mt-6 mb-3 text-[10px] font-bold uppercase tracking-widest text-white/30">Admin</div>
        <div className="space-y-1.5">
          {adminItems.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className={`group flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-200 ${
                isActive(href)
                  ? 'text-white bg-purple-500/5 border border-purple-500/20'
                  : 'text-white/70 hover:bg-gradient-to-r hover:from-purple-500/10 hover:to-transparent hover:text-white hover:pl-5'
              }`}
            >
              <Icon className={`h-4 w-4 flex-shrink-0 ${!isActive(href) && 'transition-transform group-hover:scale-110'}`} />
              <span className="text-xs">{label}</span>
            </Link>
          ))}
        </div>

        {/* Recent Chats Section */}
        <div className="mt-8 mb-3 text-[10px] font-bold uppercase tracking-widest text-white/30">Recent Chats</div>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <div className="h-12 w-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
            <SparklesIcon className="h-5 w-5 text-white/30" />
          </div>
          <p className="text-xs text-white/30 font-medium">No recent chats</p>
          <p className="text-[10px] text-white/20 mt-1">Start a conversation!</p>
        </div>
      </nav>

      {/* Bottom Actions */}
      <div className="border-t border-white/10 px-4 py-3 space-y-1.5 flex-shrink-0">
        <Link href="/profile" className="group flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:bg-white/5 hover:text-white hover:pl-5">
          <SettingsIcon className="h-4 w-4 flex-shrink-0 transition-transform group-hover:rotate-90 duration-300" />
          <span>Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="group flex w-full items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium text-white/70 transition-all duration-200 hover:bg-red-500/10 hover:text-red-400 hover:pl-5 text-left"
        >
          <LogOutIcon className="h-4 w-4 flex-shrink-0 transition-transform group-hover:translate-x-0.5" />
          <span>Logout</span>
        </button>
      </div>

      {/* User Info */}
      <div className="border-t border-white/10 px-5 py-4 flex-shrink-0 bg-gradient-to-b from-transparent to-black/20">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-xs font-bold shadow-lg">
            {userName.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-white/80 truncate">{userName}</div>
            <div className="text-[10px] text-white/40 truncate">{userEmail}</div>
          </div>
        </div>
      </div>
    </aside>
  )
}
