import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Review, ChatMessage, ReviewHistory, FileNode, AppSettings, ReviewFilter } from './types'
import { mockReviews, mockHistory, mockFiles } from './services/ai'

interface AppState {
  theme: 'dark' | 'light'
  toggleTheme: () => void

  settings: AppSettings
  updateSettings: (settings: Partial<AppSettings>) => void

  reviews: Review[]
  activeReviewId: string | null
  activeReview: Review | null
  filter: ReviewFilter
  setFilter: (filter: ReviewFilter) => void
  setActiveReview: (id: string | null) => void
  addReview: (review: Review) => void
  updateReview: (id: string, updates: Partial<Review>) => void
  acceptSuggestion: (reviewId: string, suggestionId: string) => void
  rejectSuggestion: (reviewId: string, suggestionId: string) => void

  messages: ChatMessage[]
  isChatLoading: boolean
  addMessage: (message: ChatMessage) => void
  setChatLoading: (loading: boolean) => void
  clearChat: () => void

  history: ReviewHistory[]

  files: FileNode[]
  selectedFile: string | null
  setSelectedFile: (path: string | null) => void

  sidebarOpen: boolean
  toggleSidebar: () => void
  activeTab: 'review' | 'history' | 'settings'
  setActiveTab: (tab: 'review' | 'history' | 'settings') => void
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      toggleTheme: () => set(state => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),

      settings: {
        apiKey: '',
        theme: 'dark',
        model: 'gpt-4',
        autoReview: true,
        showInlineSuggestions: true,
      },
      updateSettings: (settings) => set(state => ({ settings: { ...state.settings, ...settings } })),

      reviews: mockReviews,
      activeReviewId: mockReviews[0]?.id || null,
      activeReview: mockReviews[0] || null,
      filter: 'all',
      setFilter: (filter) => set({ filter }),
      setActiveReview: (id) => {
        const review = get().reviews.find(r => r.id === id) || null
        set({ activeReviewId: id, activeReview: review })
      },
      addReview: (review) => set(state => ({ reviews: [review, ...state.reviews] })),
      updateReview: (id, updates) => set(state => ({
        reviews: state.reviews.map(r => r.id === id ? { ...r, ...updates } : r),
        activeReview: state.activeReview?.id === id ? { ...state.activeReview, ...updates } : state.activeReview,
      })),
      acceptSuggestion: (reviewId, suggestionId) => set(state => ({
        reviews: state.reviews.map(r =>
          r.id === reviewId
            ? { ...r, suggestions: r.suggestions.map((s: any) => s.id === suggestionId ? { ...s, accepted: true } : s) }
            : r
        ),
        activeReview: state.activeReview?.id === reviewId
          ? { ...state.activeReview, suggestions: state.activeReview.suggestions.map((s: any) => s.id === suggestionId ? { ...s, accepted: true } : s) }
          : state.activeReview,
      })),
      rejectSuggestion: (reviewId, suggestionId) => set(state => ({
        reviews: state.reviews.map(r =>
          r.id === reviewId
            ? { ...r, suggestions: r.suggestions.map((s: any) => s.id === suggestionId ? { ...s, accepted: false } : s) }
            : r
        ),
        activeReview: state.activeReview?.id === reviewId
          ? { ...state.activeReview, suggestions: state.activeReview.suggestions.map((s: any) => s.id === suggestionId ? { ...s, accepted: false } : s) }
          : state.activeReview,
      })),

      messages: [],
      isChatLoading: false,
      addMessage: (message) => set(state => ({ messages: [...state.messages, message] })),
      setChatLoading: (loading) => set({ isChatLoading: loading }),
      clearChat: () => set({ messages: [] }),

      history: mockHistory,

      files: mockFiles,
      selectedFile: null,
      setSelectedFile: (path) => set({ selectedFile: path }),

      sidebarOpen: true,
      toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
      activeTab: 'review',
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    {
      name: 'code-review-storage',
      partialize: (state) => ({ theme: state.theme, settings: state.settings }),
    }
  )
)
