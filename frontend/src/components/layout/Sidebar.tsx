import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Megaphone,
  Bot,
  Search,
  Sparkles,
  FileVideo,
  Clapperboard,
  GitBranch,
  FolderOpen,
  Settings2,
  Terminal,
  LogOut,
  Sun,
  Moon,
  ShieldCheck,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { CrowdWisdomLogo } from '@/components/branding'

const NAV_ITEMS = [
  { name: 'Executive Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Campaign Management', path: '/campaigns', icon: Megaphone },
  { name: 'Agent Command Center', path: '/agents', icon: Bot },
  { name: 'Ads Research', path: '/research', icon: Search },
  { name: 'Marketing Intelligence', path: '/insights', icon: Sparkles },
  { name: 'Script Studio', path: '/scripts', icon: FileVideo },
  { name: 'Video Production', path: '/videos', icon: Clapperboard },
  { name: 'Workflow & Pipeline', path: '/workflow', icon: GitBranch },
  { name: 'Assets Library', path: '/assets', icon: FolderOpen },
  { name: 'Integrations & API', path: '/settings', icon: Settings2 },
  { name: 'Execution Logs', path: '/logs', icon: Terminal },
]

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()

  return (
    <aside className="w-64 flex-shrink-0 border-r border-[#292E37] bg-[#0C0F14] flex flex-col h-screen select-none z-30">
      {/* Official Brand Header */}
      <div className="p-4 px-5 border-b border-[#292E37] flex items-center justify-between">
        <CrowdWisdomLogo variant="sidebar" asLink href="/" />
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        <div className="px-3 pb-2 text-[10px] font-semibold text-[#727B89] tracking-wider uppercase">
          Platform Workspace
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150',
                  isActive
                    ? 'bg-[#1B2028] text-[#F2F3F5] border border-[#292E37] border-l-2 border-l-[#547DB8] shadow-sm font-semibold'
                    : 'text-[#A0A7B2] hover:bg-[#15191F] hover:text-[#F2F3F5]'
                )
              }
            >
              <Icon className="h-4 w-4 flex-shrink-0 text-[#727B89] group-hover:text-[#F2F3F5]" />
              <span className="truncate">{item.name}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Institutional Security Notice */}
      <div className="px-4 py-2 border-t border-[#292E37]/60">
        <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-[4px] bg-[#0E1218] border border-[#202734] text-[10px] text-[#8C94A0] font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F] flex-shrink-0" />
          <span className="truncate">Hermes v0.1 • TLS Verified</span>
        </div>
      </div>

      {/* User Footer & Theme Switch */}
      <div className="p-3.5 px-4 border-t border-[#292E37] bg-[#0A0D12]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="h-7 w-7 rounded-md bg-[#1B2028] border border-[#292E37] text-[#547DB8] flex items-center justify-center text-xs font-semibold uppercase flex-shrink-0">
              {user?.username?.[0] || 'A'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-medium text-[#F2F3F5] truncate leading-tight">
                {user?.full_name || user?.username || 'Executive Admin'}
              </p>
              <p className="text-[10px] text-[#727B89] capitalize truncate font-mono">
                {user?.role?.replace('_', ' ') || 'Marketing Manager'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-[#727B89] hover:text-[#F2F3F5]"
              onClick={toggleTheme}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-[#727B89] hover:text-[#D66C73]"
              onClick={logout}
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </aside>
  )
}
