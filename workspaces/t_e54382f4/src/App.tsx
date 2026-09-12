import { useState, useEffect } from 'react'
import { useStore } from './store'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { ReviewPanel } from './components/ReviewPanel'
import { HistoryView } from './components/HistoryView'
import { SettingsPanel } from './components/SettingsPanel'
import { ShortcutsModal } from './components/ShortcutsModal'

export default function App() {
  const { activeTab, theme } = useStore()
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault()
        setShortcutsOpen(prev => !prev)
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        useStore.getState().toggleTheme()
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault()
        useStore.getState().toggleSidebar()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onOpenShortcuts={() => setShortcutsOpen(true)} />
        <main className="flex-1 overflow-auto">
          {activeTab === 'review' && <ReviewPanel />}
          {activeTab === 'history' && <HistoryView />}
          {activeTab === 'settings' && <SettingsPanel />}
        </main>
      </div>
      <ShortcutsModal
        isOpen={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
      />
    </div>
  )
}
