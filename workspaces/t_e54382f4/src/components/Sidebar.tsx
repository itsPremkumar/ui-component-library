import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useStore } from '@/store'
import {
  GitBranch,
  History,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react'

const navItems = [
  { path: '/', icon: GitBranch, label: 'Review' },
  { path: '/history', icon: History, label: 'History' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  const location = useLocation()
  const { sidebarOpen, toggleSidebar } = useStore()

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-border bg-card transition-all duration-200',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-border px-4">
        {sidebarOpen && (
          <span className="text-lg font-bold text-foreground">AI Review</span>
        )}
        <button
          onClick={toggleSidebar}
          className="rounded-md p-1.5 hover:bg-accent"
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? (
            <PanelLeftClose size={20} />
          ) : (
            <PanelLeftOpen size={20} />
          )}
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map(item => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
