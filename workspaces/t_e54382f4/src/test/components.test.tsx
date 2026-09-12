import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StatusBadge } from '../components/StatusBadge'
import { CodeViewer } from '../components/CodeViewer'
import { DiffView } from '../components/DiffView'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('StatusBadge', () => {
  it('renders pending status correctly', () => {
    render(<StatusBadge status="pending" />)
    expect(screen.getByText('Pending')).toBeInTheDocument()
  })

  it('renders approved status correctly', () => {
    render(<StatusBadge status="approved" />)
    expect(screen.getByText('Approved')).toBeInTheDocument()
  })

  it('renders rejected status correctly', () => {
    render(<StatusBadge status="rejected" />)
    expect(screen.getByText('Rejected')).toBeInTheDocument()
  })

  it('renders with sm size', () => {
    const { container } = render(<StatusBadge status="reviewing" size="sm" />)
    expect(container.querySelector('span')).toHaveClass('text-[10px]')
  })
})

describe('CodeViewer', () => {
  it('renders code content', () => {
    const code = 'const x = 42;\nconsole.log(x);'
    const { container } = render(
      <CodeViewer
        code={code}
        language="javascript"
        suggestions={[]}
      />
    )
    expect(container.textContent).toContain('const x = 42;')
  })

  it('renders line numbers', () => {
    const code = 'line1\nline2\nline3'
    const { container } = render(
      <CodeViewer
        code={code}
        language="typescript"
        suggestions={[]}
      />
    )
    expect(container.querySelector('.linenumber')).toBeInTheDocument()
  })
})

describe('DiffView', () => {
  it('renders diff with added lines', () => {
    const original = 'line1\nline2'
    const modified = 'line1\nline2\nline3'
    render(
      <DiffView
        original={original}
        modified={modified}
        language="typescript"
      />
    )
    expect(screen.getByText('line3')).toBeInTheDocument()
  })

  it('renders diff with removed lines', () => {
    const original = 'line1\nline2\nline3'
    const modified = 'line1\nline3'
    render(
      <DiffView
        original={original}
        modified={modified}
        language="typescript"
      />
    )
    expect(screen.getByText('line2')).toBeInTheDocument()
  })
})
