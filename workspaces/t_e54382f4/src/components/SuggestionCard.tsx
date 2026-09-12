import { useStore } from '@/store'
import { cn, getStatusColor } from '@/lib/utils'
import type { Suggestion } from '@/types'
import {
  Check,
  X,
  AlertTriangle,
  ShieldAlert,
  Info,
  Lightbulb,
  Sparkles,
} from 'lucide-react'

interface SuggestionCardProps {
  suggestion: Suggestion
  reviewId: string
}

const typeIcons: Record<string, typeof Info> = {
  security: ShieldAlert,
  performance: Sparkles,
  bug: AlertTriangle,
  style: Lightbulb,
  refactor: Sparkles,
}

const severityBorder: Record<string, string> = {
  critical: 'border-l-red-500',
  warning: 'border-l-yellow-500',
  info: 'border-l-blue-500',
}

export function SuggestionCard({ suggestion, reviewId }: SuggestionCardProps) {
  const { acceptSuggestion, rejectSuggestion } = useStore()
  const Icon = typeIcons[suggestion.type] || Info
  const isDecided = suggestion.accepted !== null

  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-card p-3 transition-all',
        'border-l-4',
        severityBorder[suggestion.severity],
        isDecided && 'opacity-60'
      )}
    >
      <div className="flex items-start gap-2">
        <Icon
          size={16}
          className={cn(
            'mt-0.5 shrink-0',
            suggestion.severity === 'critical'
              ? 'text-red-400'
              : suggestion.severity === 'warning'
              ? 'text-yellow-400'
              : 'text-blue-400'
          )}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-medium leading-tight">
              {suggestion.message}
            </p>
            <span className="shrink-0 text-[10px] text-muted-foreground">
              L{suggestion.line}
            </span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {suggestion.suggestion}
          </p>
          <div className="mt-2 flex items-center gap-1">
            <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
              {suggestion.type}
            </span>
            <span
              className={cn(
                'rounded px-1.5 py-0.5 text-[10px] font-medium uppercase',
                suggestion.severity === 'critical'
                  ? 'bg-red-500/20 text-red-400'
                  : suggestion.severity === 'warning'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-blue-500/20 text-blue-400'
              )}
            >
              {suggestion.severity}
            </span>
          </div>
        </div>
      </div>

      {!isDecided && (
        <div className="mt-3 flex gap-2">
          <button
            onClick={() => acceptSuggestion(reviewId, suggestion.id)}
            className="flex flex-1 items-center justify-center gap-1 rounded-md bg-green-500/20 px-2 py-1.5 text-xs font-medium text-green-400 transition-colors hover:bg-green-500/30"
          >
            <Check size={12} />
            Accept
          </button>
          <button
            onClick={() => rejectSuggestion(reviewId, suggestion.id)}
            className="flex flex-1 items-center justify-center gap-1 rounded-md bg-red-500/20 px-2 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/30"
          >
            <X size={12} />
            Reject
          </button>
        </div>
      )}

      {isDecided && (
        <div className="mt-2 text-xs font-medium text-muted-foreground">
          {suggestion.accepted ? '✓ Accepted' : '✗ Rejected'}
        </div>
      )}
    </div>
  )
}
