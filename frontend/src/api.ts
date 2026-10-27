const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

export type MeasureResult = {
  status: 'met' | 'not_met' | 'excluded' | 'unresolved'
  reason: string
  category: string
  eligible: boolean
  rule_version: string
  source_fixture: string
  source_row: number
}

export type Patient = {
  id: string
  record: Record<string, string | number | boolean | null>
  original: Record<string, string | number | boolean | null>
  result: MeasureResult
  baseline_result: MeasureResult
  events: Array<{ id: number; actor: string; role: string; provenance: string; evidence: string; created_at: string }>
  assignment: null | { owner: string; role: string; due_date: string; barrier: string }
}

export type Dashboard = {
  current: { total: number; denominator: number; numerator: number; rate: number | null; excluded: number; unresolved: number; not_met: number; eligibility_questions: number }
  baseline: { total: number; denominator: number; numerator: number; rate: number | null; excluded: number; unresolved: number; not_met: number; eligibility_questions: number }
  changes: Record<string, number>
  open_import_errors: number
  specification: Record<string, any>
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  dashboard: () => request<Dashboard>('/dashboard'),
  patients: () => request<Patient[]>('/patients'),
  gaps: () => request<Patient[]>('/care-gaps'),
  equity: (dimension: string) => request<any>(`/equity?dimension=${encodeURIComponent(dimension)}`),
  reports: () => request<any[]>('/reports'),
  imports: () => request<any[]>('/imports'),
  measures: () => request<any[]>('/measures'),
  assign: (id: string, body: unknown) => request(`/care-gaps/${id}/assignment`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  workflow: (id: string, body: unknown) => request(`/workflows/${id}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  freeze: (body: unknown) => request<any>('/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  signoff: (id: number, body: unknown) => request<any>(`/reports/${id}/signoff`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  upload: (file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<any>('/imports', { method: 'POST', body })
  },
  disposition: (id: number, body: unknown) => request<any>(`/imports/${id}/disposition`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
}