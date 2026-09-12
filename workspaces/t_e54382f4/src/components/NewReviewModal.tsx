import { useState, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useStore } from '@/store'
import { aiService } from '@/services/ai'
import { cn } from '@/lib/utils'
import { Upload, X, FileCode, Loader2, AlertCircle } from 'lucide-react'

interface NewReviewModalProps {
  onClose: () => void
}

export function NewReviewModal({ onClose }: NewReviewModalProps) {
  const { addReview } = useStore()
  const [code, setCode] = useState('')
  const [filename, setFilename] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const reviewMutation = useMutation({
    mutationFn: async () => {
      if (!code.trim() || !filename.trim()) {
        throw new Error('Please provide both code and filename')
      }
      return aiService.reviewCode(code, filename)
    },
    onSuccess: (data) => {
      addReview(data)
      onClose()
    },
  })

  const handleSubmit = () => {
    reviewMutation.mutate()
  }

  const handleFileUpload = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setCode(content)
      if (!filename) {
        setFilename(file.name)
      }
    }
    reader.readAsText(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(true)
  }

  const handleDragLeave = () => {
    setDragActive(false)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileUpload(file)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl rounded-xl border border-border bg-card p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">New Code Review</h2>
          <button
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-4 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">
              Filename
            </label>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="example.tsx"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Code</label>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={cn(
                'relative rounded-md border-2 border-dashed transition-colors',
                dragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-border'
              )}
            >
              {code ? (
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  rows={10}
                  className="w-full resize-none rounded-md bg-transparent p-3 font-mono text-sm focus:outline-none"
                  placeholder="Paste your code here..."
                />
              ) : (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                  <FileCode size={32} className="text-muted-foreground/50" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Paste your code or drag & drop a file
                  </p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-3 flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  >
                    <Upload size={14} />
                    Upload File
                  </button>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileInput}
                accept=".ts,.tsx,.js,.jsx,.py,.go,.rs,.java,.rb,.php"
                className="hidden"
              />
            </div>
          </div>

          {reviewMutation.isError && (
            <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              <AlertCircle size={16} />
              {reviewMutation.error instanceof Error
                ? reviewMutation.error.message
                : 'An error occurred'}
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-md border border-border px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!code.trim() || !filename.trim() || reviewMutation.isPending}
            className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {reviewMutation.isPending ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              'Start Review'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
