import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import { Key, CornerDownLeft, X } from 'lucide-react'

interface ShortcutsModalProps {
  isOpen: boolean
  onClose: () => void
}

const shortcuts = [
  { keys: ['Ctrl', '/'], description: 'Open keyboard shortcuts' },
  { keys: ['Ctrl', 'N'], description: 'New review' },
  { keys: ['Ctrl', 'Enter'], description: 'Submit code for review' },
  { keys: ['Escape'], description: 'Close modal / Cancel request' },
  { keys: ['Ctrl', 'K'], description: 'Toggle theme' },
  { keys: ['Ctrl', 'B'], description: 'Toggle sidebar' },
  { keys: ['1'], description: 'Switch to Review tab' },
  { keys: ['2'], description: 'Switch to History tab' },
  { keys: ['3'], description: 'Switch to Settings tab' },
]

export function ShortcutsModal({ isOpen, onClose }: ShortcutsModalProps) {
  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Key size={20} className="text-primary" />
            <h2 className="text-lg font-semibold">Keyboard Shortcuts</h2>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-4 space-y-2">
          {shortcuts.map(shortcut => (
            <div
              key={shortcut.description}
              className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-accent/50"
            >
              <span className="text-sm text-muted-foreground">
                {shortcut.description}
              </span>
              <div className="flex items-center gap-1">
                {shortcut.keys.map((key, i) => (
                  <span key={i} className="flex items-center gap-1">
                    {i > 0 && <span className="text-xs text-muted-foreground">+</span>}
                    <kbd
                      className={cn(
                        'inline-flex h-6 min-w-6 items-center justify-center rounded border border-border bg-muted px-1.5 text-xs font-medium',
                        key === 'Enter' && 'px-2'
                      )}
                    >
                      {key === 'Enter' ? <CornerDownLeft size={12} /> : key}
                    </kbd>
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
