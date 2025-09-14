import axios from 'axios'

const base = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000'

export const api = axios.create({
  baseURL: base,
})
