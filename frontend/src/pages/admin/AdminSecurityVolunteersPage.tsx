import React, { useEffect, useState } from 'react'

import api from '../../lib/api'
import { Button, Input } from '../../components/ui'

type Volunteer = { id: number; email: string; is_active: boolean; created_at: string }

export default function AdminSecurityVolunteersPage() {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [changingId, setChangingId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadVolunteers = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.get<Volunteer[]>('/admin/security-volunteers')
      setVolunteers(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to load security volunteers.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void loadVolunteers() }, [])

  const createVolunteer = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setMessage('')
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setSaving(true)
    try {
      await api.post('/admin/security-volunteers', { email, password, confirm_password: confirmPassword })
      setEmail('')
      setPassword('')
      setConfirmPassword('')
      setMessage('Security volunteer created successfully.')
      await loadVolunteers()
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to create security volunteer.')
    } finally {
      setSaving(false)
    }
  }

  const setActive = async (volunteer: Volunteer) => {
    setChangingId(volunteer.id)
    setError('')
    setMessage('')
    try {
      await api.patch(`/admin/security-volunteers/${volunteer.id}`, { is_active: !volunteer.is_active })
      setMessage(volunteer.is_active ? 'Security volunteer deactivated.' : 'Security volunteer activated.')
      await loadVolunteers()
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to update volunteer status.')
    } finally {
      setChangingId(null)
    }
  }

  return <div className="space-y-6 text-slate-100"><div><p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Access Operations</p><h1 className="mt-2 text-3xl font-semibold text-white">Security Volunteers</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Manage the accounts used for event-day QR scanning and check-in.</p></div>{error ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}{message ? <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</div> : null}<section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6"><h2 className="text-xl font-semibold text-white">Create Volunteer</h2><form onSubmit={createVolunteer} className="mt-5 grid gap-4 sm:grid-cols-3"><Input type="email" placeholder="Volunteer email" value={email} onChange={(event) => setEmail(event.target.value)} required /><Input type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /><Input type="password" placeholder="Confirm password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} minLength={8} required /><div className="sm:col-span-3"><Button type="submit" isLoading={saving}>Create Volunteer</Button></div></form></section><section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6"><h2 className="text-xl font-semibold text-white">Existing Volunteers</h2>{loading ? <div className="mt-5 h-36 animate-pulse rounded-2xl bg-white/5" /> : <div className="mt-5 space-y-3">{volunteers.length ? volunteers.map((volunteer) => <div key={volunteer.id} className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between"><div><p className="break-all font-medium text-white">{volunteer.email}</p><p className="mt-1 text-xs text-slate-500">Created {new Date(volunteer.created_at).toLocaleString()}</p></div><div className="flex items-center gap-3"><span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${volunteer.is_active ? 'border-emerald-300/25 bg-emerald-400/10 text-emerald-200' : 'border-slate-300/20 bg-white/5 text-slate-400'}`}>{volunteer.is_active ? 'Active' : 'Inactive'}</span><Button variant={volunteer.is_active ? 'destructive' : 'secondary'} size="sm" isLoading={changingId === volunteer.id} onClick={() => void setActive(volunteer)}>{volunteer.is_active ? 'Deactivate' : 'Activate'}</Button></div></div>) : <p className="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-500">No security volunteers yet.</p>}</div>}</section></div>
}
