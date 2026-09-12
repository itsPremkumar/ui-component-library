import { useStore } from '@/store'
import { cn, formatDate, getStatusColor } from '@/lib/utils'
import { CheckCircle2, XCircle, Clock, Loader2, FileText } from 'lucide-react'

const statusIcons: Record<string, typeof Clock> = {
  pending: Clock,
  reviewing: Loader2,
  approved: CheckCircle2,
  rejected: XCircle,
}

export function HistoryView() {
  const { history } = useStore()

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border p-6">
        <h1 className="text-xl font-bold">Review History</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Past code reviews and their outcomes
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {history.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <FileText size={48} className="text-muted-foreground/50" />
            <p className="mt-4 text-lg font-medium text-muted-foreground">
              No review history yet
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              Complete your first code review to see it here
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((item: any) => {
              const Icon = statusIcons[item.status] || Clock
              return (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-card p-4 transition-colors hover:bg-accent/50"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'flex h-10 w-10 items-center justify-center rounded-lg',
                        getStatusColor(item.status)
                      )}
                    >
                      <Icon size={20} />
                    </div>
                    <div>
                      <p className="font-medium">{item.filename}</p>
                      <p className="text-sm text-muted-foreground">
                        {item.suggestionCount} suggestions ·{' '}
                        {formatDate(item.createdAt)}
                      </p>
                    </div>
                  </div>
                  <span
                    className={cn(
                      'rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize',
                      getStatusColor(item.status)
                    )}
                  >
                    {item.status}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
