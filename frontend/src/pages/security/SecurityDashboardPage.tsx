import React, { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'

import { Button } from '../../components/ui'
import api from '../../lib/api'
import { useAuth } from '../../context/AuthContext'

type DashboardStats = {
  event_title: string | null
  total_checked_in: number
  male_checked_in: number
  female_checked_in: number
  other_checked_in: number
  approved_eligible: number
  remaining_to_check_in: number
}

const emptyStats: DashboardStats = {
  event_title: null,
  total_checked_in: 0,
  male_checked_in: 0,
  female_checked_in: 0,
  other_checked_in: 0,
  approved_eligible: 0,
  remaining_to_check_in: 0,
}

export default function SecurityDashboardPage() {
  const navigate = useNavigate()
  const { isInitialized, user, logout } = useAuth()
  const [stats, setStats] = useState<DashboardStats>(emptyStats)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return
    let active = true
    const loadStats = async () => {
      try {
        const response = await api.get<DashboardStats>('/security/dashboard')
        if (active) {
          setStats(response.data)
          setError('')
        }
      } catch (err: any) {
        if (active) setError(err?.response?.data?.detail || 'Unable to load dashboard statistics.')
      } finally {
        if (active) setLoading(false)
      }
    }
    void loadStats()
    const refresh = window.setInterval(() => void loadStats(), 15_000)
    return () => {
      active = false
      window.clearInterval(refresh)
    }
  }, [user])

  if (!isInitialized) return <div className="min-h-screen bg-slate-950 p-6 text-white">Loading...</div>
  if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return <Navigate to="/security/login" replace />

  return <main className="min-h-screen bg-slate-950 px-4 py-5 text-white sm:px-6"><div className="mx-auto max-w-2xl space-y-5"><header className="flex items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 2026</p><h1 className="mt-2 text-2xl font-semibold">Security Dashboard</h1><p className="mt-1 text-sm text-slate-400">{stats.event_title || 'No active event'}</p></div><Button variant="ghost" onClick={() => void logout()}>Log out</Button></header>{error ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}<section className="rounded-3xl border border-cyan-300/20 bg-slate-900/90 p-6 text-center shadow-2xl sm:p-8"><p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-300">Total checked in</p><p className="mt-3 text-6xl font-black leading-none tracking-tight sm:text-8xl">{loading ? '...' : stats.total_checked_in.toLocaleString()}</p>{stats.approved_eligible > 0 ? <p className="mt-4 text-sm text-slate-400">{stats.remaining_to_check_in.toLocaleString()} remaining of {stats.approved_eligible.toLocaleString()} eligible</p> : null}</section><section className="rounded-3xl border border-white/10 bg-slate-900/70 p-5"><h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-300">Gender breakdown</h2><div className="mt-4 grid grid-cols-3 gap-2 text-center sm:gap-4">{[['Male', stats.male_checked_in], ['Female', stats.female_checked_in], ['Other', stats.other_checked_in]].map(([label, count]) => <div key={label} className="rounded-2xl bg-slate-800/80 px-2 py-4"><p className="text-xs text-slate-400">{label}</p><p className="mt-2 text-2xl font-bold sm:text-3xl">{count.toLocaleString()}</p></div>)}</div></section><Button size="lg" className="w-full" onClick={() => navigate('/security/scanner')}>Scan Pass</Button></div></main>
}