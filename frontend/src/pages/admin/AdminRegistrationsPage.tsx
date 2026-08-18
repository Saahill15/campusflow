import React, { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import api from '../../lib/api'
import { useAuth } from '../../context/AuthContext'

type RegistrationItem = {
  id: string
  registration_number?: string
  first_name?: string
  last_name?: string
  department?: string
  academic_year?: string
  roll_number?: string
  phone?: string
  email?: string
  gender?: string
  status: string
  payment_status?: string
  pass_number?: string | null
  pass_status?: string | null
  checked_in: boolean
  created_at: string
}

type ResponseShape = {
  items: RegistrationItem[]
  meta: { total: number; page: number; per_page: number }
  filters?: {
    departments: string[]
    academic_years: string[]
    payment_statuses: string[]
  }
}

const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
]

const checkinOptions = [
  { label: 'All check-in states', value: 'all' },
  { label: 'Checked In', value: 'true' },
  { label: 'Not Checked In', value: 'false' },
]

const humanize = (value?: string | null) => value ? value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) : 'Not Set'

const badgeStyles = (value?: string | null) => {
  if (value === 'approved' || value === 'verified' || value === 'issued' || value === 'true') return 'border-emerald-300/20 bg-emerald-400/10 text-emerald-200'
  if (value === 'rejected' || value === 'false') return 'border-rose-300/20 bg-rose-400/10 text-rose-200'
  if (value === 'pending') return 'border-amber-300/20 bg-amber-400/10 text-amber-200'
  return 'border-white/10 bg-white/5 text-slate-300'
}

function StatusBadge({ value, fallback = 'Not Set' }: { value?: string | null; fallback?: string }) {
  return <span className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-xs ${badgeStyles(value)}`}>{value ? humanize(value) : fallback}</span>
}

export default function AdminRegistrationsPage() {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [items, setItems] = useState<RegistrationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchInput, setSearchInput] = useState(searchParams.get('q') ?? '')
  const [search, setSearch] = useState(searchParams.get('q') ?? '')
  const [status, setStatus] = useState(searchParams.get('status') ?? 'all')
  const [paymentStatus, setPaymentStatus] = useState(searchParams.get('payment_status') ?? 'all')
  const [department, setDepartment] = useState(searchParams.get('department') ?? 'all')
  const [academicYear, setAcademicYear] = useState(searchParams.get('academic_year') ?? 'all')
  const [checkinStatus, setCheckinStatus] = useState(searchParams.get('checked_in') ?? 'all')
  const [dateFrom, setDateFrom] = useState(searchParams.get('date_from') ?? '')
  const [dateTo, setDateTo] = useState(searchParams.get('date_to') ?? '')
  const [page, setPage] = useState(Number(searchParams.get('page') ?? '1') || 1)
  const [meta, setMeta] = useState<ResponseShape['meta']>({ total: 0, page: 1, per_page: 10 })
  const [filterOptions, setFilterOptions] = useState<ResponseShape['filters']>({ departments: [], academic_years: [], payment_statuses: [] })
  const [reloadKey, setReloadKey] = useState(0)

  const totalPages = useMemo(() => Math.max(1, Math.ceil(meta.total / meta.per_page)), [meta])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const nextSearch = searchInput.trim()
      setSearch(nextSearch)
      setPage(1)
      setSearchParams((current) => {
        const next = new URLSearchParams(current)
        if (nextSearch) next.set('q', nextSearch)
        else next.delete('q')
        next.set('page', '1')
        return next
      })
    }, 350)
    return () => window.clearTimeout(timer)
  }, [searchInput, setSearchParams])

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const params = new URLSearchParams()
        params.set('page', String(page))
        params.set('per_page', '10')
        if (status !== 'all') params.set('status', status)
        if (search.trim()) params.set('search', search.trim())
        if (paymentStatus !== 'all') params.set('payment_status', paymentStatus)
        if (department !== 'all') params.set('department', department)
        if (academicYear !== 'all') params.set('academic_year', academicYear)
        if (checkinStatus !== 'all') params.set('checked_in', checkinStatus)
        if (dateFrom) params.set('date_from', dateFrom)
        if (dateTo) params.set('date_to', dateTo)
        const response = await api.get<ResponseShape>(`/admin/registrations?${params.toString()}`)
        setItems(response.data.items)
        setMeta(response.data.meta)
        if (response.data.filters) setFilterOptions(response.data.filters)
      } catch (err) {
        setError((err as any)?.response?.data?.detail || (err instanceof Error ? err.message : 'Failed to load registrations'))
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [page, search, status, paymentStatus, department, academicYear, checkinStatus, dateFrom, dateTo, reloadKey])

  const updateFilter = (key: string, value: string, setter: (value: string) => void) => {
    setter(value)
    setPage(1)
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      if (value && value !== 'all') next.set(key, value)
      else next.delete(key)
      next.set('page', '1')
      return next
    })
  }

  const goToPage = (nextPage: number) => {
    setPage(nextPage)
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      next.set('page', String(nextPage))
      return next
    })
  }

  const clearFilters = () => {
    setSearchInput('')
    setSearch('')
    setStatus('all')
    setPaymentStatus('all')
    setDepartment('all')
    setAcademicYear('all')
    setCheckinStatus('all')
    setDateFrom('')
    setDateTo('')
    setPage(1)
    setSearchParams({ page: '1' })
  }

  const activeFilterCount = [search, status, paymentStatus, department, academicYear, checkinStatus, dateFrom, dateTo].filter((value) => value && value !== 'all').length

  return (
    <div className="min-w-0 space-y-6 text-slate-100">
      <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Registrations</p>
            <h1 className="text-3xl font-semibold">Review student submissions</h1>
            <p className="mt-2 text-sm text-slate-400">Logged in as {user?.email ?? 'admin'}</p>
            </div>
            <Link to="/admin" className="text-sm text-cyan-300 hover:text-cyan-200">Back to Dashboard</Link>
          </div>
          <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <input value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Search name, email, number, roll, pass" className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 sm:col-span-2 xl:col-span-2" />
            <select value={status} onChange={(e) => updateFilter('status', e.target.value, setStatus)} className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              {statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <select value={paymentStatus} onChange={(e) => updateFilter('payment_status', e.target.value, setPaymentStatus)} className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              <option value="all">All payment statuses</option>
              {filterOptions?.payment_statuses.map((option) => <option key={option} value={option}>{humanize(option)}</option>)}
            </select>
            <select value={department} onChange={(e) => updateFilter('department', e.target.value, setDepartment)} className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              <option value="all">All departments</option>
              {filterOptions?.departments.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
            <select value={academicYear} onChange={(e) => updateFilter('academic_year', e.target.value, setAcademicYear)} className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              <option value="all">All academic years</option>
              {filterOptions?.academic_years.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
            <select value={checkinStatus} onChange={(e) => updateFilter('checked_in', e.target.value, setCheckinStatus)} className="min-w-0 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              {checkinOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <label className="min-w-0 text-xs text-slate-400">From<input type="date" value={dateFrom} onChange={(e) => updateFilter('date_from', e.target.value, setDateFrom)} className="mt-1 block w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white" /></label>
            <label className="min-w-0 text-xs text-slate-400">To<input type="date" value={dateTo} onChange={(e) => updateFilter('date_to', e.target.value, setDateTo)} className="mt-1 block w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white" /></label>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
            <span>{activeFilterCount ? `${activeFilterCount} active filter${activeFilterCount === 1 ? '' : 's'}` : 'Showing all registrations'} · Newest first</span>
            {activeFilterCount ? <button onClick={clearFilters} className="rounded-xl border border-white/10 px-3 py-2 text-slate-200 hover:bg-white/5">Clear filters</button> : null}
          </div>
        </div>
      </div>

      {error ? <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-100"><span>{error}</span><button onClick={() => setReloadKey((value) => value + 1)} className="rounded-xl border border-red-200/20 px-3 py-2 hover:bg-red-200/10">Retry</button></div> : null}

      <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/80 shadow-xl shadow-black/20">
        <div className="max-w-full overflow-x-auto">
          <table className="min-w-[1180px] divide-y divide-white/10 text-left text-sm">
            <thead className="bg-white/5 text-slate-300">
              <tr>
                <th className="px-6 py-4">Registration Number</th>
                <th className="px-6 py-4">Student Name</th>
                <th className="px-6 py-4">Department</th>
                <th className="px-6 py-4">Academic Year</th>
                <th className="px-6 py-4">Payment</th>
                <th className="px-6 py-4">Registration Status</th>
                <th className="px-6 py-4">Pass Number</th>
                <th className="px-6 py-4">Check-in</th>
                <th className="px-6 py-4">Registered</th>
                <th className="px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10 text-slate-100">
              {loading ? (
                <tr><td className="px-6 py-8" colSpan={10}>Loading registrations...</td></tr>
              ) : items.length === 0 ? (
                <tr><td className="px-6 py-8" colSpan={10}>No registrations found. Try clearing the active filters.</td></tr>
              ) : items.map((item) => (
                <tr key={item.id} className="hover:bg-white/5">
                  <td className="px-6 py-4 font-medium text-cyan-300">{item.registration_number}</td>
                  <td className="px-6 py-4">{`${item.first_name ?? ''} ${item.last_name ?? ''}`.trim()}</td>
                  <td className="max-w-[220px] px-6 py-4">{item.department || 'Not Set'}</td>
                  <td className="px-6 py-4">{item.academic_year || 'Not Set'}</td>
                  <td className="px-6 py-4"><StatusBadge value={item.payment_status} /></td>
                  <td className="px-6 py-4">
                    <StatusBadge value={item.status} />
                  </td>
                  <td className="px-6 py-4"><div className="space-y-1"><div>{item.pass_number || 'Not Issued'}</div><StatusBadge value={item.pass_number ? item.pass_status : undefined} fallback="Not Issued" /></div></td>
                  <td className="px-6 py-4"><StatusBadge value={String(item.checked_in)} fallback="Not Checked In" /></td>
                  <td className="whitespace-nowrap px-6 py-4">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <Link to={`/admin/registrations/${item.id}`} className="inline-flex rounded-xl border border-white/10 px-3 py-2 text-sm text-cyan-300 transition hover:bg-white/5">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between border-t border-white/10 px-6 py-4 text-sm text-slate-400">
          <span>Total {meta.total}</span>
          <div className="flex items-center gap-2">
            <button disabled={page <= 1} onClick={() => goToPage(Math.max(1, page - 1))} className="rounded-xl border border-white/10 px-3 py-2 disabled:opacity-40">Prev</button>
            <span>Page {page} of {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => goToPage(page + 1)} className="rounded-xl border border-white/10 px-3 py-2 disabled:opacity-40">Next</button>
          </div>
        </div>
      </div>
    </div>
  )
}
