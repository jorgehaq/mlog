import React, { useEffect, useMemo, useState } from 'react'
import { Line, Bar } from 'react-chartjs-2'
import 'chart.js/auto'

const API_BASE = '/api'

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
          <div style={{ maxWidth: 520 }}>
            <Bar
              data={{
                labels: Object.keys(summary.by_action),
                datasets: [
                  {
                    label: 'Eventos por acción',
                    data: Object.values(summary.by_action),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
                  }
                ]
              }}
              options={{ responsive: true, plugins: { legend: { display: false } } }}
            />
          </div>
        </div>
      )}
      {timeline && (
        <div>
          <h4>Timeline (por minuto)</h4>
          <div style={{ maxWidth: 720 }}>
            <Line
              data={{
                labels: timeline.map(p => new Date(p.ts).toLocaleTimeString()),
                datasets: [
                  {
                    label: 'Eventos/minuto',
                    data: timeline.map(p => p.count),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)'
                  }
                ]
              }}
              options={{ responsive: true }}
            />
          </div>
        </div>
      )}
    </div>
  )}
