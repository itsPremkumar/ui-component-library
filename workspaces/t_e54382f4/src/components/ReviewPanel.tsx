import { useState } from 'react'
import { useStore } from '@/store'
import { cn, getStatusColor } from '@/lib/utils'
import { CodeViewer } from './CodeViewer'
import { DiffView } from './DiffView'
import { StatusBadge } from './StatusBadge'
import { SuggestionCard } from './SuggestionCard'
import { NewReviewModal } from './NewReviewModal'
import {
  Plus,
  Filter,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
} from 'lucide-react'
import type { ReviewFilter } from '@/types'

const filterOptions: { value: ReviewFilter; label: string; icon: typeof Clock }[] = [
  { value: 'all', label: 'All', icon: Filter },
  { value: 'pending', label: 'Pending', icon: Clock },
  { value: 'reviewing', label: 'Reviewing', icon: Loader2 },
  { value: 'approved', label: 'Approved', icon: CheckCircle2 },
  { value: 'rejected', label: 'Rejected', icon: XCircle },
]

export function ReviewPanel() {
  const { reviews, activeReview, filter, setFilter, setActiveReview } = useStore()
  const [showNewReview, setShowNewReview] = useState(false)
  const [viewMode, setViewMode] = useState<'code' | 'diff'>('code')

  const filteredReviews = reviews.filter((r: any) =>
    filter === 'all' ? true : r.status === filter
  )

  return (
    <div className="flex h-full">
      <div className="w-72 border-r border-border bg-card">
        <div className="flex items-center justify-between border-b border-border p-4">
          <h2 className="text-sm font-semibold">Reviews</h2>
          <button
            onClick={() => setShowNewReview(true)}
            className="flex items-center gap-1 rounded-md bg-primary px-2.5 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Plus size={14} />
            New
          </button>
        </div>

        <div className="flex gap-1 border-b border-border p-2 overflow-x-auto">
          {filterOptions.map(opt => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={cn(
                'flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium whitespace-nowrap transition-colors',
                filter === opt.value
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent'
              )}
            >
              <opt.icon size={12} />
              {opt.label}
            </button>
          ))}
        </div>

        <div className="overflow-y-auto">
          {filteredReviews.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              No reviews found
            </div>
          ) : (
            filteredReviews.map((review: any) => (
              <button
                key={review.id}
                onClick={() => setActiveReview(review.id)}
                className={cn(
                  'w-full border-b border-border p-3 text-left transition-colors',
                  activeReview?.id === review.id
                    ? 'bg-primary/5'
                    : 'hover:bg-accent/50'
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate">{review.filename}</span>
                  <StatusBadge status={review.status} size="sm" />
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{review.suggestions.length} suggestions</span>
                  <span>·</span>
                  <span>{new Date(review.updatedAt).toLocaleTimeString()}</span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden">
        {activeReview ? (
          <>
            <div className="flex items-center justify-between border-b border-border bg-card px-4 py-2">
              <div className="flex items-center gap-3">
                <h2 className="font-semibold">{activeReview.filename}</h2>
                <StatusBadge status={activeReview.status} />
              </div>
              <div className="flex items-center gap-2">
                <div className="flex rounded-md border border-border overflow-hidden">
                  <button
                    onClick={() => setViewMode('code')}
                    className={cn(
                      'px-3 py-1 text-xs font-medium transition-colors',
                      viewMode === 'code'
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent'
                    )}
                  >
                    Code
                  </button>
                  <button
                    onClick={() => setViewMode('diff')}
                    className={cn(
                      'px-3 py-1 text-xs font-medium transition-colors',
                      viewMode === 'diff'
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent'
                    )}
                  >
                    Diff
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
              <div className="flex-1 overflow-auto">
                {viewMode === 'code' ? (
                  <CodeViewer
                    code={activeReview.originalCode}
                    language={activeReview.language}
                    suggestions={activeReview.suggestions}
                  />
                ) : (
                  <DiffView
                    original={activeReview.originalCode}
                    modified={activeReview.suggestedCode || activeReview.originalCode}
                    language={activeReview.language}
                  />
                )}
              </div>

              <div className="w-80 border-l border-border bg-card overflow-y-auto">
                <div className="border-b border-border p-3">
                  <h3 className="text-sm font-semibold">Suggestions</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {activeReview.suggestions.filter((s: any) => s.accepted === null).length} pending
                  </p>
                </div>
                <div className="space-y-2 p-2">
                  {activeReview.suggestions.map((suggestion: any) => (
                    <SuggestionCard
                      key={suggestion.id}
                      suggestion={suggestion}
                      reviewId={activeReview.id}
                    />
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-muted-foreground">No review selected</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Select a review from the list or create a new one
              </p>
              <button
                onClick={() => setShowNewReview(true)}
                className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                New Review
              </button>
            </div>
          </div>
        )}
      </div>

      {showNewReview && <NewReviewModal onClose={() => setShowNewReview(false)} />}
    </div>
  )
}
