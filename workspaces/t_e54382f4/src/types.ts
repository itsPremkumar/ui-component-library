export interface Review {
  id: string
  filename: string
  language: string
  status: 'pending' | 'reviewing' | 'approved' | 'rejected'
  originalCode: string
  suggestedCode: string | null
  suggestions: Suggestion[]
  createdAt: string
  updatedAt: string
}

export interface Suggestion {
  id: string
  type: 'security' | 'performance' | 'style' | 'bug' | 'refactor'
  severity: 'critical' | 'warning' | 'info'
  line: number
  message: string
  suggestion: string
  accepted: boolean | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  suggestions?: Suggestion[]
}

export interface ReviewHistory {
  id: string
  filename: string
  status: Review['status']
  suggestionCount: number
  createdAt: string
}

export interface FileNode {
  name: string
  path: string
  type: 'file' | 'folder'
  children?: FileNode[]
  status?: Review['status']
}

export interface AppSettings {
  apiKey: string
  theme: 'dark' | 'light'
  model: string
  autoReview: boolean
  showInlineSuggestions: boolean
}

export type ReviewFilter = 'all' | 'pending' | 'approved' | 'rejected' | 'reviewing'
