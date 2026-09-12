import { cn, getStatusColor } from '@/lib/utils'
import { Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react'

interface StatusBadgeProps {
  status: 'pending' | 'reviewing' | 'approved' | 'rejected'
  size?: 'sm' | 'md'
}

const statusConfig = {
  pending: { icon: Clock, label: 'Pending' },
  reviewing: { icon: Loader2, label: 'Reviewing' },
  approved: { icon: CheckCircle2, label: 'Approved' },
  rejected: { icon: XCircle, label: 'Rejected' },
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border font-medium capitalize',
        getStatusColor(status),
        size === 'sm'
          ? 'px-1.5 py-0.5 text-[10px]'
          : 'px-2.5 py-0.5 text-xs'
      )}
    >
      <Icon size={size === 'sm' ? 10 : 12} className={status === 'reviewing' ? 'animate-spin' : ''} />
      {config.label}
    </span>
  )
}
