const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`)
  return data
}
export const getItems = () => request('/items')
export const ingest = (payload) => request('/ingest', { method: 'POST', body: JSON.stringify(payload) })
export const askQuestion = (payload) => request('/query', { method: 'POST', body: JSON.stringify(payload) })
