import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { App } from './App'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { ErrorBoundary } from './components/ErrorBoundary'

describe('App', () => {
  it('renders title', () => {
    const qc = new QueryClient()
    render(
      <ErrorBoundary>
        <QueryClientProvider client={qc}>
          <App />
        </QueryClientProvider>
      </ErrorBoundary>
    )
    expect(screen.getByText(/mlog — Frontend de prueba/i)).toBeInTheDocument()
  })
})
