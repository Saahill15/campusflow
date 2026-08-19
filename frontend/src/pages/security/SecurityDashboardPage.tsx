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

  return <main className="security-screen px-4 py-5 sm:px-6"><div className="mx-auto max-w-2xl space-y-5"><header className="flex items-start justify-between gap-4"><div><p className="security-eyebrow">Pragyarambh 2026 / Security operations</p><h1 className="mt-3 text-3xl font-semibold tracking-[-.04em]">Today's check-in</h1><p className="mt-2 text-sm text-[#b9a891]">{stats.event_title || 'No active event'}</p></div><Button variant="ghost" className="admin-button admin-button-ghost" onClick={() => void logout()}>Log out</Button></header>{error ? <div className="admin-notice admin-notice-error">{error}</div> : null}<section className="security-panel p-7 text-center sm:p-10"><p className="security-eyebrow">Total checked in</p><p className="mt-4 font-[Space_Grotesk] text-7xl font-bold tracking-[-.08em] text-[#f4eadb] sm:text-9xl">{loading ? '—' : stats.total_checked_in.toLocaleString()}</p>{stats.approved_eligible > 0 ? <p className="mt-4 text-sm text-[#b9a891]">{stats.remaining_to_check_in.toLocaleString()} remaining of {stats.approved_eligible.toLocaleString()} approved</p> : null}</section><section className="security-panel p-5"><p className="security-eyebrow">Attendee profile</p><h2 className="mt-2 text-xl font-semibold">Gender breakdown</h2><div className="mt-5 grid grid-cols-3 gap-2 sm:gap-4">{[['Male', stats.male_checked_in], ['Female', stats.female_checked_in], ['Other', stats.other_checked_in]].map(([label, count]) => <div key={label} className="border border-[#d3a654]/15 px-2 py-5 text-center"><p className="text-xs text-[#a9957d]">{label}</p><p className="mt-2 text-2xl font-bold text-[#f4eadb] sm:text-3xl">{Number(count).toLocaleString()}</p></div>)}</div></section><Button size="lg" className="admin-button admin-button-primary w-full" onClick={() => navigate('/security/scanner')}>Scan pass</Button></div></main>
}