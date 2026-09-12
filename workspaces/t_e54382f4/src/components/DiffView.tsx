import { useMemo } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useStore } from '@/store'

interface DiffViewProps {
  original: string
  modified: string
  language: string
}

export function DiffView({ original, modified, language }: DiffViewProps) {
  const { theme } = useStore()

  const diffLines = useMemo(() => {
    const originalLines = original.split('\n')
    const modifiedLines = modified.split('\n')
    const result: Array<{ type: 'added' | 'removed' | 'unchanged'; content: string; lineNumber: number }> = []

    let oi = 0, mi = 0
    while (oi < originalLines.length || mi < modifiedLines.length) {
      if (oi >= originalLines.length) {
        result.push({ type: 'added', content: modifiedLines[mi], lineNumber: mi + 1 })
        mi++
      } else if (mi >= modifiedLines.length) {
        result.push({ type: 'removed', content: originalLines[oi], lineNumber: oi + 1 })
        oi++
      } else if (originalLines[oi] === modifiedLines[mi]) {
        result.push({ type: 'unchanged', content: originalLines[oi], lineNumber: oi + 1 })
        oi++
        mi++
      } else {
        result.push({ type: 'removed', content: originalLines[oi], lineNumber: oi + 1 })
        result.push({ type: 'added', content: modifiedLines[mi], lineNumber: mi + 1 })
        oi++
        mi++
      }
    }
    return result
  }, [original, modified])

  const highlightStyle = theme === 'dark' ? oneDark : oneLight

  return (
    <div className="h-full overflow-auto p-4">
      <div className="space-y-0 rounded-lg border border-border overflow-hidden font-mono text-xs">
        {diffLines.map((line, idx) => (
          <div
            key={idx}
            className={`flex ${
              line.type === 'added'
                ? 'bg-green-500/10'
                : line.type === 'removed'
                ? 'bg-red-500/10'
                : 'bg-transparent'
            }`}
          >
            <span className="w-8 shrink-0 select-none border-r border-border px-2 text-right text-muted-foreground">
              {line.lineNumber}
            </span>
            <span
              className={`w-4 shrink-0 select-none text-center ${
                line.type === 'added'
                  ? 'text-green-400'
                  : line.type === 'removed'
                  ? 'text-red-400'
                  : 'text-muted-foreground'
              }`}
            >
              {line.type === 'added' ? '+' : line.type === 'removed' ? '-' : ' '}
            </span>
            <SyntaxHighlighter
              language={language}
              style={highlightStyle}
              customStyle={{
                margin: 0,
                padding: '0.125rem 0.5rem',
                background: 'transparent',
                fontSize: '0.75rem',
              }}
            >
              {line.content || ' '}
            </SyntaxHighlighter>
          </div>
        ))}
      </div>
    </div>
  )
}
