import { useState } from 'react'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import {
  Sun,
  Moon,
  Key,
  Zap,
  Eye,
  EyeOff,
  Save,
  RotateCcw,
} from 'lucide-react'

export function SettingsPanel() {
  const { settings, updateSettings, theme, toggleTheme } = useStore()
  const [apiKey, setApiKey] = useState(settings.apiKey)
  const [showKey, setShowKey] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    updateSettings({ apiKey })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    const defaults = {
      apiKey: '',
      theme: 'dark' as const,
      model: 'gpt-4',
      autoReview: true,
      showInlineSuggestions: true,
    }
    setApiKey(defaults.apiKey)
    updateSettings(defaults)
    if (theme !== defaults.theme) toggleTheme()
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border p-6">
        <h1 className="text-xl font-bold">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Configure your AI code review experience
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="mx-auto max-w-2xl space-y-6">
          <section className="rounded-lg border border-border bg-card p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold">
              <Key size={16} className="text-primary" />
              API Configuration
            </h2>
            <div className="mt-4 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  API Key
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type={showKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={e => setApiKey(e.target.value)}
                      placeholder="sk-..."
                      className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                    <button
                      onClick={() => setShowKey(!showKey)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Your API key is stored locally and never sent to our servers.
                </p>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">Model</label>
                <select
                  value={settings.model}
                  onChange={e => updateSettings({ model: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="gemini-pro">Gemini Pro</option>
                </select>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-border bg-card p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold">
              {theme === 'dark' ? (
                <Moon size={16} className="text-primary" />
              ) : (
                <Sun size={16} className="text-primary" />
              )}
              Appearance
            </h2>
            <div className="mt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Theme</p>
                  <p className="text-xs text-muted-foreground">
                    Toggle between light and dark mode
                  </p>
                </div>
                <button
                  onClick={toggleTheme}
                  className={cn(
                    'relative h-6 w-11 rounded-full transition-colors',
                    theme === 'dark' ? 'bg-primary' : 'bg-muted-foreground'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform',
                      theme === 'dark' ? 'left-5' : 'left-0.5'
                    )}
                  />
                </button>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-border bg-card p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold">
              <Zap size={16} className="text-primary" />
              Review Preferences
            </h2>
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Auto-review on paste</p>
                  <p className="text-xs text-muted-foreground">
                    Automatically trigger AI review when code is pasted
                  </p>
                </div>
                <button
                  onClick={() =>
                    updateSettings({ autoReview: !settings.autoReview })
                  }
                  className={cn(
                    'relative h-6 w-11 rounded-full transition-colors',
                    settings.autoReview ? 'bg-primary' : 'bg-muted-foreground'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform',
                      settings.autoReview ? 'left-5' : 'left-0.5'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Inline suggestions</p>
                  <p className="text-xs text-muted-foreground">
                    Show suggestion highlights directly in the code viewer
                  </p>
                </div>
                <button
                  onClick={() =>
                    updateSettings({
                      showInlineSuggestions: !settings.showInlineSuggestions,
                    })
                  }
                  className={cn(
                    'relative h-6 w-11 rounded-full transition-colors',
                    settings.showInlineSuggestions
                      ? 'bg-primary'
                      : 'bg-muted-foreground'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform',
                      settings.showInlineSuggestions ? 'left-5' : 'left-0.5'
                    )}
                  />
                </button>
              </div>
            </div>
          </section>

          <div className="flex gap-3">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              <Save size={16} />
              {saved ? 'Saved!' : 'Save Changes'}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 rounded-md border border-border px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            >
              <RotateCcw size={16} />
              Reset to Defaults
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
