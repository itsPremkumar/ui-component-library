import type { Review, Suggestion, ChatMessage, ReviewHistory, FileNode } from '../types'

const MOCK_SUGGESTIONS: Suggestion[] = [
  {
    id: 's1',
    type: 'security',
    severity: 'critical',
    line: 12,
    message: 'Potential SQL injection vulnerability detected',
    suggestion: 'Use parameterized queries instead of string concatenation to prevent SQL injection attacks.',
    accepted: null,
  },
  {
    id: 's2',
    type: 'performance',
    severity: 'warning',
    line: 28,
    message: 'Inefficient loop with O(n²) complexity',
    suggestion: 'Consider using a Map or Set for O(1) lookups to improve performance on large datasets.',
    accepted: null,
  },
  {
    id: 's3',
    type: 'bug',
    severity: 'warning',
    line: 45,
    message: 'Possible null reference exception',
    suggestion: 'Add null check or use optional chaining (?.) to handle potential undefined values.',
    accepted: null,
  },
  {
    id: 's4',
    type: 'style',
    severity: 'info',
    line: 8,
    message: 'Inconsistent naming convention',
    suggestion: 'Use camelCase for variable names to follow the project style guide.',
    accepted: null,
  },
  {
    id: 's5',
    type: 'refactor',
    severity: 'info',
    line: 52,
    message: 'Function exceeds recommended length (45 lines)',
    suggestion: 'Extract helper functions to improve readability and maintainability.',
    accepted: null,
  },
]

const MOCK_FILES: FileNode[] = [
  {
    name: 'src',
    path: '/src',
    type: 'folder',
    children: [
      {
        name: 'components',
        path: '/src/components',
        type: 'folder',
        children: [
          { name: 'AuthForm.tsx', path: '/src/components/AuthForm.tsx', type: 'file', status: 'approved' },
          { name: 'Dashboard.tsx', path: '/src/components/Dashboard.tsx', type: 'file', status: 'pending' },
          { name: 'Header.tsx', path: '/src/components/Header.tsx', type: 'file', status: 'rejected' },
        ],
      },
      {
        name: 'services',
        path: '/src/services',
        type: 'folder',
        children: [
          { name: 'api.ts', path: '/src/services/api.ts', type: 'file', status: 'reviewing' },
          { name: 'auth.ts', path: '/src/services/auth.ts', type: 'file', status: 'pending' },
        ],
      },
      { name: 'App.tsx', path: '/src/App.tsx', type: 'file', status: 'approved' },
      { name: 'main.tsx', path: '/src/main.tsx', type: 'file', status: 'approved' },
    ],
  },
  {
    name: 'tests',
    path: '/tests',
    type: 'folder',
    children: [
      { name: 'auth.test.ts', path: '/tests/auth.test.ts', type: 'file', status: 'pending' },
      { name: 'api.test.ts', path: '/tests/api.test.ts', type: 'file', status: 'approved' },
    ],
  },
  { name: 'package.json', path: '/package.json', type: 'file', status: 'approved' },
  { name: 'README.md', path: '/README.md', type: 'file', status: 'approved' },
]

const MOCK_REVIEWS: Review[] = [
  {
    id: 'r1',
    filename: 'AuthForm.tsx',
    language: 'typescript',
    status: 'reviewing',
    originalCode: `import React, { useState } from 'react';

export function AuthForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const response = await fetch('/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('token', data.token);
      window.location.href = '/dashboard';
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}`,
    suggestedCode: `import React, { useState } from 'react';

export function AuthForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const response = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) {
        throw new Error('Authentication failed');
      }
      
      const data = await response.json();
      if (data.token) {
        sessionStorage.setItem('token', data.token);
        window.location.href = '/dashboard';
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div role="alert">{error}</div>}
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        minLength={8}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}`,
    suggestions: MOCK_SUGGESTIONS,
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'r2',
    filename: 'api.ts',
    language: 'typescript',
    status: 'pending',
    originalCode: `export async function fetchUsers() {
  const res = await fetch('/api/users');
  const users = await res.json();
  return users;
}

export async function deleteUser(id: string) {
  await fetch('/api/users/' + id, { method: 'DELETE' });
}`,
    suggestedCode: null,
    suggestions: [],
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
  },
]

const MOCK_HISTORY: ReviewHistory[] = [
  { id: 'h1', filename: 'AuthForm.tsx', status: 'approved', suggestionCount: 3, createdAt: new Date(Date.now() - 86400000).toISOString() },
  { id: 'h2', filename: 'Dashboard.tsx', status: 'rejected', suggestionCount: 5, createdAt: new Date(Date.now() - 172800000).toISOString() },
  { id: 'h3', filename: 'api.ts', status: 'approved', suggestionCount: 2, createdAt: new Date(Date.now() - 259200000).toISOString() },
  { id: 'h4', filename: 'auth.ts', status: 'approved', suggestionCount: 4, createdAt: new Date(Date.now() - 345600000).toISOString() },
  { id: 'h5', filename: 'Header.tsx', status: 'rejected', suggestionCount: 1, createdAt: new Date(Date.now() - 432000000).toISOString() },
]

// Simulated AI service
class AIService {
  private abortControllers = new Map<string, AbortController>()

  async reviewCode(code: string, filename: string, signal?: AbortSignal): Promise<Review> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        const existing = MOCK_REVIEWS.find(r => r.filename === filename)
        if (existing) {
          resolve({ ...existing, status: 'reviewing' })
        } else {
          resolve({
            id: `r-${Date.now()}`,
            filename,
            language: this.detectLanguage(filename),
            status: 'reviewing',
            originalCode: code,
            suggestedCode: this.generateSuggestedCode(code),
            suggestions: this.generateSuggestions(code),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          })
        }
      }, 2000 + Math.random() * 1500)

      if (signal) {
        signal.addEventListener('abort', () => {
          clearTimeout(timeout)
          reject(new DOMException('Aborted', 'AbortError'))
        })
      }
    })
  }

  async chat(message: string, signal?: AbortSignal): Promise<ChatMessage> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve({
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: this.generateChatResponse(message),
          timestamp: new Date().toISOString(),
        })
      }, 1000 + Math.random() * 2000)

      if (signal) {
        signal.addEventListener('abort', () => {
          clearTimeout(timeout)
          reject(new DOMException('Aborted', 'AbortError'))
        })
      }
    })
  }

  cancelRequest(id: string) {
    const controller = this.abortControllers.get(id)
    if (controller) {
      controller.abort()
      this.abortControllers.delete(id)
    }
  }

  private detectLanguage(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase()
    const langMap: Record<string, string> = {
      ts: 'typescript',
      tsx: 'typescript',
      js: 'javascript',
      jsx: 'javascript',
      py: 'python',
      go: 'go',
      rs: 'rust',
    }
    return langMap[ext || ''] || 'typescript'
  }

  private generateSuggestedCode(code: string): string {
    return code
      .replace(/localStorage\.setItem/g, 'sessionStorage.setItem')
      .replace(/var /g, 'const ')
  }

  private generateSuggestions(code: string): Suggestion[] {
    const suggestions: Suggestion[] = []
    if (code.includes('localStorage')) {
      suggestions.push({
        id: `s-${Date.now()}-1`,
        type: 'security',
        severity: 'critical',
        line: code.split('\n').findIndex(l => l.includes('localStorage')) + 1,
        message: 'Sensitive data stored in localStorage is vulnerable to XSS',
        suggestion: 'Use sessionStorage or secure cookies for sensitive data.',
        accepted: null,
      })
    }
    if (code.includes('fetch(') && !code.includes('try')) {
      suggestions.push({
        id: `s-${Date.now()}-2`,
        type: 'bug',
        severity: 'warning',
        line: code.split('\n').findIndex(l => l.includes('fetch(')) + 1,
        message: 'Network request without error handling',
        suggestion: 'Wrap fetch calls in try/catch to handle network errors gracefully.',
        accepted: null,
      })
    }
    if (code.includes('var ')) {
      suggestions.push({
        id: `s-${Date.now()}-3`,
        type: 'style',
        severity: 'info',
        line: code.split('\n').findIndex(l => l.includes('var ')) + 1,
        message: 'Use of var declaration',
        suggestion: 'Prefer const or let for block-scoped variable declarations.',
        accepted: null,
      })
    }
    if (suggestions.length === 0) {
      suggestions.push({
        id: `s-${Date.now()}-0`,
        type: 'refactor',
        severity: 'info',
        line: 1,
        message: 'Code looks good overall',
        suggestion: 'Consider adding JSDoc comments for public APIs.',
        accepted: null,
      })
    }
    return suggestions
  }

  private generateChatResponse(message: string): string {
    const lower = message.toLowerCase()
    if (lower.includes('security') || lower.includes('vulnerability')) {
      return 'I found a potential security issue: the code uses `localStorage` to store sensitive authentication tokens. This makes the application vulnerable to XSS attacks. Consider using `sessionStorage` or secure, httpOnly cookies instead.'
    }
    if (lower.includes('performance') || lower.includes('slow')) {
      return 'For performance optimization, I recommend: 1) Memoizing expensive computations with `useMemo`, 2) Using virtualization for long lists, 3) Code-splitting routes with React.lazy().'
    }
    if (lower.includes('error') || lower.includes('bug')) {
      return 'The main issue I see is missing error handling around the network request. Always wrap async operations in try/catch blocks and provide user-friendly error messages.'
    }
    return 'I\'ve analyzed the code and found a few areas for improvement. Check the suggestions panel for detailed recommendations. Would you like me to elaborate on any specific issue?'
  }
}

export const aiService = new AIService()
export const mockFiles = MOCK_FILES
export const mockReviews = MOCK_REVIEWS
export const mockHistory = MOCK_HISTORY
