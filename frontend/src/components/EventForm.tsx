import React, { useState } from 'react'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000'

export const EventForm: React.FC = () => {
  const [timestamp, setTimestamp] = useState<string>(new Date().toISOString())
  const [service, setService] = useState('demo')
  const [userId, setUserId] = useState('user1')
  const [action, setAction] = useState('login')
  const [metadata, setMetadata] = useState('{}')
  const [apiKey, setApiKey] = useState('')
  const [status, setStatus] = useState<string>('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('Enviando...')
    try {
      const body = {
        timestamp,
        service,
        user_id: userId,
        action,
        metadata: JSON.parse(metadata || '{}'),
      }
      const res = await fetch(`${API_BASE}/events/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const t = await res.text()
        throw new Error(`HTTP ${res.status}: ${t}`)
      }
      const data = await res.json()
      setStatus(`OK: creado id=${data.id}`)
    } catch (err: any) {
      setStatus(`Error: ${err.message}`)
    }
  }

  return (
    <div>
      <h3>Crear evento</h3>
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: '0.5rem', maxWidth: 520 }}>
        <label>
          Timestamp
          <input value={timestamp} onChange={e => setTimestamp(e.target.value)} style={{ width: '100%' }} />
        </label>
        <label>
          Service
          <input value={service} onChange={e => setService(e.target.value)} />
        </label>
        <label>
          User ID
          <input value={userId} onChange={e => setUserId(e.target.value)} />
        </label>
        <label>
          Action
          <input value={action} onChange={e => setAction(e.target.value)} />
        </label>
        <label>
          Metadata (JSON)
          <textarea value={metadata} onChange={e => setMetadata(e.target.value)} rows={4} />
        </label>
        <label>
          API Key (opcional)
          <input value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="X-API-Key" />
        </label>
        <button type="submit">Enviar</button>
      </form>
      {status && <p><small>{status}</small></p>}
    </div>
  )
}

