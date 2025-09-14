import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { HealthSchema, RootSchema } from './types'
import { EventForm } from './components/EventForm'
import { Dashboard } from './components/Dashboard'

const API = '/api'

async function getJson<T>(path: string, schema: { parse: (v: unknown) => T }): Promise<T> {
  const res = await fetch(`${API}${path}`)
  const data = await res.json()
  return schema.parse(data)
}

export function App() {
  const [view, setView] = useState<'home' | 'form' | 'dash'>('home')
  const rootQ = useQuery({
    queryKey: ['root'],
    queryFn: () => getJson('/', RootSchema),
  })
  const healthQ = useQuery({
    queryKey: ['health'],
    queryFn: () => getJson('/health', HealthSchema),
  })

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', margin: '2rem' }}>
      <h1>mlog — Frontend de prueba</h1>
      <p>API: <code>{API}</code></p>
      <nav style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <button onClick={() => setView('home')}>Home</button>
        <button onClick={() => setView('form')}>Crear evento</button>
        <button onClick={() => setView('dash')}>Dashboard</button>
      </nav>
      {view === 'home' && (
        <>
          <section>
            <h3>Root</h3>
            {rootQ.isLoading ? (<div>Cargando...</div>) : rootQ.isError ? (
              <div>Error</div>
            ) : (
              <pre>{JSON.stringify(rootQ.data, null, 2)}</pre>
            )}
          </section>
          <section>
            <h3>Health</h3>
            {healthQ.isLoading ? (<div>Cargando...</div>) : healthQ.isError ? (
              <div>Error</div>
            ) : (
              <pre>{JSON.stringify(healthQ.data, null, 2)}</pre>
            )}
          </section>
        </>
      )}
      {view === 'form' && <EventForm />}
      {view === 'dash' && <Dashboard />}
    </div>
  )
}
