import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useStore } from '@/store'
import { aiService } from '@/services/ai'
import { cn } from '@/lib/utils'
import {
  Send,
  Trash2,
  Bot,
  User,
  Sparkles,
  X,
} from 'lucide-react'

export function ChatPanel() {
  const { messages, addMessage, isChatLoading, setChatLoading, clearChat } = useStore()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const controller = new AbortController()
      abortRef.current = controller
      setChatLoading(true)
      return aiService.chat(message, controller.signal)
    },
    onSuccess: (data) => {
      addMessage(data)
      setChatLoading(false)
    },
    onError: (error) => {
      if (error instanceof DOMException && error.name === 'AbortError') {
        addMessage({
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: 'Request cancelled.',
          timestamp: new Date().toISOString(),
        })
      } else {
        addMessage({
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: 'Sorry, an error occurred. Please try again.',
          timestamp: new Date().toISOString(),
        })
      }
      setChatLoading(false)
    },
  })

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!input.trim() || isChatLoading) return

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user' as const,
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }
    addMessage(userMessage)
    setInput('')
    chatMutation.mutate(userMessage.content)
  }

  const handleCancel = () => {
    abortRef.current?.abort()
    chatMutation.reset()
    setChatLoading(false)
  }

  const quickPrompts = [
    'Check for security issues',
    'Review performance',
    'Find potential bugs',
    'Suggest improvements',
  ]

  return (
    <div className="flex h-full flex-col border-t border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <Bot size={18} className="text-primary" />
          <h3 className="text-sm font-semibold">AI Assistant</h3>
          <Sparkles size={14} className="text-yellow-400" />
        </div>
        <button
          onClick={clearChat}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          title="Clear chat"
        >
          <Trash2 size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <Bot size={40} className="text-muted-foreground/50" />
            <p className="mt-3 text-sm text-muted-foreground">
              Ask the AI assistant about your code
            </p>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {quickPrompts.map(prompt => (
                <button
                  key={prompt}
                  onClick={() => setInput(prompt)}
                  className="rounded-md border border-border px-3 py-2 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg: any) => (
          <div
            key={msg.id}
            className={cn(
              'flex gap-3',
              msg.role === 'user' ? 'flex-row-reverse' : ''
            )}
          >
            <div
              className={cn(
                'flex h-7 w-7 shrink-0 items-center justify-center rounded-full',
                msg.role === 'user' ? 'bg-primary/20' : 'bg-secondary'
              )}
            >
              {msg.role === 'user' ? (
                <User size={14} className="text-primary" />
              ) : (
                <Bot size={14} />
              )}
            </div>
            <div
              className={cn(
                'max-w-[80%] rounded-lg px-3 py-2 text-sm',
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary'
              )}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isChatLoading && (
          <div className="flex gap-3">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary">
              <Bot size={14} />
            </div>
            <div className="rounded-lg bg-secondary px-3 py-2">
              <div className="flex gap-1">
                <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: '0ms' }} />
                <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: '150ms' }} />
                <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-border p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your code..."
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {isChatLoading ? (
            <button
              onClick={handleCancel}
              className="flex items-center gap-1 rounded-md bg-destructive px-3 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90"
            >
              <X size={16} />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
