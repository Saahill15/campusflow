import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, Clock3, RefreshCw, UserCheck, UserX, Users, XCircle, type LucideIcon } from 'lucide-react'

import api from '../../lib/api'
import { useAuth } from '../../context/AuthContext'

type OverviewCount = { label: string; count: number }

type DashboardSummary = {
  total_registrations: number
  pending_approval: number
  approved: number
  rejected: number
  checked_in: number
  not_checked_in: number
  recent_registrations: Array<{
    registration_number?: string | null
    student_name: string
    department?: string | null
    status: string
    created_at: string
  }>
  department_overview: OverviewCount[]
  academic_year_overview: OverviewCount[]
  payment_overview: OverviewCount[]
}

type StatCardProps = {
  label: string
  count: number
  icon: LucideIcon
  tone: string
}

const statCards: Array<{ key: keyof Pick<DashboardSummary, 'total_registrations' | 'pending_approval' | 'approved' | 'rejected' | 'checked_in' | 'not_checked_in'>; label: string; icon: LucideIcon; tone: string }> = [
  { key: 'total_registrations', label: 'Total Registrations', icon: Users, tone: 'text-cyan-300 bg-cyan-400/10 border-cyan-300/20' },
  { key: 'pending_approval', label: 'Pending Approval', icon: Clock3, tone: 'text-amber-300 bg-amber-400/10 border-amber-300/20' },
  { key: 'approved', label: 'Approved', icon: CheckCircle2, tone: 'text-emerald-300 bg-emerald-400/10 border-emerald-300/20' },
  { key: 'rejected', label: 'Rejected', icon: XCircle, tone: 'text-rose-300 bg-rose-400/10 border-rose-300/20' },
  { key: 'checked_in', label: 'Checked In', icon: UserCheck, tone: 'text-violet-300 bg-violet-400/10 border-violet-300/20' },
  { key: 'not_checked_in', label: 'Not Checked In', icon: UserX, tone: 'text-slate-300 bg-white/5 border-white/10' },
]

const formatDate = (value: string) => new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })

const statusStyles: Record<string, string> = {
  pending: 'bg-amber-400/10 text-amber-200 border-amber-300/20',
  approved: 'bg-emerald-400/10 text-emerald-200 border-emerald-300/20',
  rejected: 'bg-rose-400/10 text-rose-200 border-rose-300/20',
  checked_in: 'bg-violet-400/10 text-violet-200 border-violet-300/20',
}

function StatCard({ label, count, icon: Icon, tone }: StatCardProps) {
  return (
    <div className="min-w-0 rounded-2xl border border-white/10 bg-slate-900/80 p-5 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-3">
        <div className={`rounded-xl border p-2.5 ${tone}`}><Icon size={19} strokeWidth={1.8} /></div>
        <span className="text-3xl font-semibold tracking-tight text-white">{count}</span>
      </div>
      <p className="mt-5 text-sm font-medium text-slate-300">{label}</p>
    </div>
  )
}

function CountList({ items, emptyLabel }: { items: OverviewCount[]; emptyLabel: string }) {
  if (!items.length) return <p className="text-sm text-slate-500">{emptyLabel}</p>
  const maximum = Math.max(...items.map((item) => item.count), 1)
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label} className="min-w-0">
          <div className="flex items-start justify-between gap-4 text-sm">
            <span className="min-w-0 break-words text-slate-300">{item.label}</span>
            <span className="shrink-0 font-semibold text-white">{item.count}</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
            <div className="h-full rounded-full bg-cyan-300" style={{ width: `${Math.max((item.count / maximum) * 100, item.count ? 8 : 0)}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}

export default function AdminHomePage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadSummary = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.get<DashboardSummary>('/admin/dashboard/summary')
      setSummary(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to load dashboard summary')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSummary()
  }, [])

  return (
    <div className="min-w-0 space-y-6 text-slate-100">
      <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-xl shadow-black/20 sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Admin Overview</p>
            <h1 className="mt-2 break-words text-3xl font-semibold tracking-tight text-white">Good to see you, {user?.name || 'Admin'}</h1>
            <p className="mt-2 text-sm text-slate-400">A live view of registration progress and event attendance.</p>
          </div>
          <button onClick={() => void loadSummary()} disabled={loading} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-2.5 text-sm text-slate-200 transition hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-50">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </section>

      {error ? (
        <div className="flex flex-col gap-3 rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-4 text-sm text-rose-100 sm:flex-row sm:items-center sm:justify-between">
          <span>{error}</span>
          <button onClick={() => void loadSummary()} className="self-start rounded-lg border border-rose-200/20 px-3 py-2 text-rose-100 hover:bg-rose-200/10 sm:self-auto">Try again</button>
        </div>
      ) : null}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {statCards.map((card) => (
          loading || !summary
            ? <div key={card.key} className="h-[137px] animate-pulse rounded-2xl border border-white/10 bg-slate-900/80" />
            : <StatCard key={card.key} label={card.label} count={summary[card.key]} icon={card.icon} tone={card.tone} />
        ))}
      </section>

      <section className="grid min-w-0 gap-6 xl:grid-cols-[1.4fr_1fr]">
        <div className="min-w-0 rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-black/10">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Latest activity</p>
              <h2 className="mt-1 text-xl font-semibold text-white">Recent Registrations</h2>
            </div>
            <Link to="/admin/registrations" className="text-sm font-medium text-cyan-300 hover:text-cyan-200">View All Registrations</Link>
          </div>
          <div className="mt-5 space-y-3">
            {loading || !summary ? (
              <div className="h-48 animate-pulse rounded-2xl bg-white/5" />
            ) : summary.recent_registrations.length ? summary.recent_registrations.map((registration) => (
              <div key={`${registration.registration_number}-${registration.created_at}`} className="grid min-w-0 gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
                <div className="min-w-0">
                  <p className="break-words font-medium text-white">{registration.student_name}</p>
                  <p className="mt-1 break-words text-sm text-slate-400">{registration.registration_number || 'No registration number'} · {registration.department || 'Department not specified'}</p>
                </div>
                <div className="flex items-center justify-between gap-3 sm:flex-col sm:items-end">
                  <span className={`rounded-full border px-2.5 py-1 text-xs capitalize ${statusStyles[registration.status] || 'border-white/10 bg-white/5 text-slate-300'}`}>{registration.status.replace('_', ' ')}</span>
                  <span className="text-xs text-slate-500">{formatDate(registration.created_at)}</span>
                </div>
              </div>
            )) : <p className="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-500">No registrations yet.</p>}
          </div>
        </div>

        <div className="min-w-0 rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-black/10">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Distribution</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Department Overview</h2>
          <div className="mt-6">{loading || !summary ? <div className="h-48 animate-pulse rounded-2xl bg-white/5" /> : <CountList items={summary.department_overview} emptyLabel="No department data yet." />}</div>
        </div>
      </section>

      <section className="grid min-w-0 gap-6 lg:grid-cols-2">
        <div className="min-w-0 rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-black/10">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Student profile</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Academic Year Overview</h2>
          <div className="mt-6">{loading || !summary ? <div className="h-32 animate-pulse rounded-2xl bg-white/5" /> : <CountList items={summary.academic_year_overview} emptyLabel="No academic year data yet." />}</div>
        </div>
        <div className="min-w-0 rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-black/10">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Registration finance</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Payment Overview</h2>
          <div className="mt-6">{loading || !summary ? <div className="h-32 animate-pulse rounded-2xl bg-white/5" /> : <CountList items={summary.payment_overview} emptyLabel="No payment data yet." />}</div>
        </div>
      </section>
    </div>
  )
}
