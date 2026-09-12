import { useState } from 'react'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import {
  Sun,
  Moon,
  Keyboard,
  Code2,
  Search,
  Bell,
} from 'lucide-react'

interface HeaderProps {
  onOpenShortcuts: () => void
}

export function Header({ onOpenShortcuts }: HeaderProps) {
  const { theme, toggleTheme } = useStore()
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search reviews..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="h-9 w-64 rounded-md border border-input bg-background pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onOpenShortcuts}
          className={cn(
            'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors',
            'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <Keyboard size={16} />
          <span className="hidden sm:inline">Shortcuts</span>
        </button>

        <button
          onClick={toggleTheme}
          className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <button
          className="relative rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          aria-label="Notifications"
        >
          <Bell size={18} />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-primary" />
        </button>

        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <Code2 size={18} />
        </a>
      </div>
    </header>
  )
}
