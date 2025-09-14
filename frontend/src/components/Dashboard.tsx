import React, { useEffect, useState } from 'react'

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000'

type Summary = { by_action: Record<string, number>, total: number }
type Point = { ts: string; count: number }

export const Dashboard: React.FC = () => {
  const [service, setService] = useState('')
  const [summary, setSummary] = useState<Summary | null>(null)
  const [timeline, setTimeline] = useState<Point[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const qs = service ? `?service=${encodeURIComponent(service)}` : ''
      const [s, t] = await Promise.all([
        fetch(`${API_BASE}/analytics/summary${qs}`).then(r => r.json()),
        fetch(`${API_BASE}/analytics/timeline${qs}`).then(r => r.json()),
      ])
      setSummary(s)
      setTimeline(t.points || [])
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <h3>Dashboard</h3>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <label>Service
          <input value={service} onChange={e => setService(e.target.value)} placeholder="axi" />
        </label>
        <button onClick={load}>Actualizar</button>
      </div>
      {loading && <p>Cargando...</p>}
      {error && <p style={{ color: 'crimson' }}>Error: {error}</p>}
      {summary && (
        <div>
          <h4>Resumen</h4>
          <p>Total: {summary.total}</p>
          <ul>
            {Object.entries(summary.by_action).map(([k, v]) => (
              <li key={k}><code>{k}</code>: {v}</li>
            ))}
          </ul>
        </div>
      )}
      {timeline && (
        <div>
          <h4>Timeline (por minuto)</h4>
          <ul>
            {timeline.map((p, i) => (
              <li key={i}><code>{p.ts}</code>: {p.count}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )}

