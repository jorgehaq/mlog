import React, { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function App() {
  const [out, setOut] = useState('(sin datos)')

  async function fetchPath(path: string) {
    setOut('Cargando...')
    try {
      const res = await fetch(`${API}${path}`)
      const txt = await res.text()
      setOut(`${res.status} ${res.statusText}\n\n${txt}`)
    } catch (e: any) {
      setOut('Error: ' + e?.message)
    }
  }

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', margin: '2rem' }}>
      <h1>mlog — Frontend de prueba</h1>
      <p>API: <code>{API}</code></p>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button onClick={() => fetchPath('/')}>Fetch /</button>
        <button onClick={() => fetchPath('/health')}>Fetch /health</button>
      </div>
      <h3>Respuesta</h3>
      <pre>{out}</pre>
    </div>
  )
}

