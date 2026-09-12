import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useStore } from '@/store'
import type { Suggestion } from '@/types'
import { AlertTriangle, Info, ShieldAlert } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeViewerProps {
  code: string
  language: string
  suggestions: Suggestion[]
}

const severityIcons: Record<string, typeof Info> = {
  critical: ShieldAlert,
  warning: AlertTriangle,
  info: Info,
}

const severityColors: Record<string, string> = {
  critical: 'border-red-500/50 bg-red-500/10 text-red-400',
  warning: 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400',
  info: 'border-blue-500/50 bg-blue-500/10 text-blue-400',
}

export function CodeViewer({ code, language, suggestions }: CodeViewerProps) {
  const { theme } = useStore()

  return (
    <div className="relative h-full overflow-auto">
      <SyntaxHighlighter
        language={language}
        style={theme === 'dark' ? oneDark : oneLight}
        showLineNumbers
        wrapLines
        lineProps={(lineNumber: number) => {
          const lineSuggestion = suggestions.find(s => s.line === lineNumber)
          const style: React.CSSProperties = {}
          if (lineSuggestion) {
            style.backgroundColor =
              lineSuggestion.severity === 'critical'
                ? 'rgba(239, 68, 68, 0.15)'
                : lineSuggestion.severity === 'warning'
                ? 'rgba(234, 179, 8, 0.15)'
                : 'rgba(59, 130, 246, 0.15)'
            style.borderLeft = `3px solid ${
              lineSuggestion.severity === 'critical'
                ? '#ef4444'
                : lineSuggestion.severity === 'warning'
                ? '#eab308'
                : '#3b82f6'
            }`
            style.display = 'block'
            style.width = '100%'
            style.paddingLeft = '0.5rem'
          }
          return { style }
        }}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'transparent',
          fontSize: '0.8125rem',
          lineHeight: '1.6',
          height: '100%',
        }}
      >
        {code}
      </SyntaxHighlighter>

      {suggestions
        .filter(s => s.accepted === null)
        .map(suggestion => {
          const Icon = severityIcons[suggestion.severity] || Info
          return (
            <div
              key={suggestion.id}
              className={cn(
                'absolute right-4 z-10 max-w-xs rounded-lg border p-3 shadow-lg',
                severityColors[suggestion.severity]
              )}
              style={{ top: `${suggestion.line * 22 + 48}px` }}
            >
              <div className="flex items-start gap-2">
                <Icon size={16} className="mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs font-medium">{suggestion.message}</p>
                  <p className="mt-1 text-xs opacity-80">{suggestion.suggestion}</p>
                </div>
              </div>
            </div>
          )
        })}
    </div>
  )
}
