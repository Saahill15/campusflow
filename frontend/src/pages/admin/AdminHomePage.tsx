import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, CheckCircle2, Clock3, RefreshCw, ShieldCheck, UserCheck, UserX, Users, XCircle } from 'lucide-react'
import api from '../../lib/api'
import { useAuth } from '../../context/AuthContext'
import { AdminNotice, AdminPageHeader, AdminSectionHeading, AdminSurface } from '../../components/admin/AdminPrimitives'

type OverviewCount = { label: string; count: number }
type DashboardSummary = { total_registrations: number; pending_approval: number; approved: number; rejected: number; checked_in: number; not_checked_in: number; recent_registrations: Array<{ registration_number?: string | null; student_name: string; department?: string | null; status: string; created_at: string }>; department_overview: OverviewCount[]; academic_year_overview: OverviewCount[]; payment_overview: OverviewCount[] }

const cards = [
  ['total_registrations', 'Total registrations', Users, 'gold'], ['pending_approval', 'Awaiting review', Clock3, 'orange'], ['approved', 'Approved', CheckCircle2, 'green'], ['rejected', 'Rejected', XCircle, 'red'], ['checked_in', 'Checked in', UserCheck, 'gold'], ['not_checked_in', 'Not checked in', UserX, 'muted'],
] as const

const formatDate = (value: string) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })

function Distribution({ items }: { items: OverviewCount[] }) {
  if (!items.length) return <div className="admin-empty">No data available yet.</div>
  const maximum = Math.max(...items.map((item) => item.count), 1)
  return <div className="space-y-5">{items.map((item) => <div key={item.label}><div className="flex justify-between gap-4 text-sm"><span className="min-w-0 break-words text-[#d9cbb8]">{item.label}</span><strong className="text-[#f4eadb]">{item.count}</strong></div><div className="mt-2 h-1.5 bg-[#160e0a]"><div className="h-full bg-[#d3a654]" style={{ width: `${Math.max(item.count / maximum * 100, item.count ? 8 : 0)}%` }} /></div></div>)}</div>
}

export default function AdminHomePage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const loadSummary = async () => { setLoading(true); setError(''); try { const response = await api.get<DashboardSummary>('/admin/dashboard/summary'); setSummary(response.data) } catch (err: any) { setError(err?.response?.data?.detail || err?.message || 'Unable to load dashboard summary.') } finally { setLoading(false) } }
  useEffect(() => { void loadSummary() }, [])
  return <div className="space-y-7"><AdminPageHeader eyebrow="Overview / Live operations" title={`Good afternoon, ${user?.name || 'Admin'}`} description="A clear view of registration momentum, approval workload, and event-day attendance." action={<button className="admin-button admin-button-secondary" onClick={() => void loadSummary()} disabled={loading}><RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Refresh</button>} />{error ? <AdminNotice>{error}</AdminNotice> : null}<section className="admin-stat-grid">{cards.map(([key, label, Icon]) => <div key={key} className="admin-stat-card"><div className="admin-stat-icon"><Icon size={17} /></div><p className="admin-stat-value">{loading || !summary ? '—' : summary[key]}</p><p className="admin-stat-label">{label}</p></div>)}</section><div className="grid gap-5 xl:grid-cols-[1.35fr_.65fr]"><AdminSurface><AdminSectionHeading eyebrow="Latest activity" title="Recent registrations" action={<Link className="admin-button admin-button-ghost" to="/admin/registrations">View all <ArrowUpRight size={14} /></Link>} />{loading || !summary ? <div className="admin-empty">Loading registration activity...</div> : summary.recent_registrations.length ? <div className="space-y-2">{summary.recent_registrations.map((registration) => <Link key={`${registration.registration_number}-${registration.created_at}`} to={`/admin/registrations`} className="flex flex-col gap-2 border-b border-[#d3a654]/10 px-1 py-4 transition hover:bg-[#d3a654]/[.04] sm:flex-row sm:items-center sm:justify-between"><div><p className="font-semibold text-[#f4eadb]">{registration.student_name}</p><p className="mt-1 text-xs text-[#a9957d]">{registration.registration_number || 'No number'} · {registration.department || 'Department not set'}</p></div><div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end"><span className="admin-badge admin-badge-neutral">{registration.status.replace('_', ' ')}</span><span className="text-xs text-[#8e7963]">{formatDate(registration.created_at)}</span></div></Link>)}</div> : <div className="admin-empty">No registrations yet.</div>}</AdminSurface><AdminSurface><AdminSectionHeading eyebrow="Distribution" title="By department" /><Distribution items={summary?.department_overview || []} /></AdminSurface></div><div className="grid gap-5 lg:grid-cols-2"><AdminSurface><AdminSectionHeading eyebrow="Student profile" title="Academic year" /><Distribution items={summary?.academic_year_overview || []} /></AdminSurface><AdminSurface><AdminSectionHeading eyebrow="Registration finance" title="Payment overview" /><Distribution items={summary?.payment_overview || []} /></AdminSurface></div><AdminSurface><AdminSectionHeading eyebrow="Quick actions" title="Move the day forward" /><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Link className="admin-button admin-button-secondary justify-between" to="/admin/registrations?status=pending">Review pending <ArrowUpRight size={14} /></Link><Link className="admin-button admin-button-secondary justify-between" to="/admin/security-volunteers">Security team <ShieldCheck size={14} /></Link><Link className="admin-button admin-button-secondary justify-between" to="/admin/settings">System settings <ArrowUpRight size={14} /></Link><Link className="admin-button admin-button-secondary justify-between" to="/admin/registrations?checked_in=false">Attendance queue <UserCheck size={14} /></Link></div></AdminSurface></div>
}
