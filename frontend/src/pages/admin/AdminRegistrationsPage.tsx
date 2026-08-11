import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

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
  created_at: string
}

type ResponseShape = {
  items: RegistrationItem[]
  meta: { total: number; page: number; per_page: number }
}

const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
]

export default function AdminRegistrationsPage() {
  const { user, logout } = useAuth()
  const [items, setItems] = useState<RegistrationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [page, setPage] = useState(1)
  const [meta, setMeta] = useState<ResponseShape['meta']>({ total: 0, page: 1, per_page: 10 })

  const totalPages = useMemo(() => Math.max(1, Math.ceil(meta.total / meta.per_page)), [meta])

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
        const response = await api.get<ResponseShape>(`/admin/registrations?${params.toString()}`)
        setItems(response.data.items)
        setMeta(response.data.meta)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load registrations')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [page, search, status])

  useEffect(() => {
    setPage(1)
  }, [search, status])

  return (
    <div className="space-y-6 text-slate-100">
      <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Registrations</p>
            <h1 className="text-3xl font-semibold">Review student submissions</h1>
            <p className="mt-2 text-sm text-slate-400">Logged in as {user?.email ?? 'admin'}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by number, name, roll number, email" className="min-w-[280px] rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500" />
            <select value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white">
              {statusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <button onClick={() => logout()} className="rounded-2xl border border-white/10 px-4 py-3 text-sm text-slate-200 transition hover:bg-white/5">Logout</button>
          </div>
        </div>
      </div>

      {error ? <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">{error}</div> : null}

      <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/80 shadow-xl shadow-black/20">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/10 text-left text-sm">
            <thead className="bg-white/5 text-slate-300">
              <tr>
                <th className="px-6 py-4">Registration</th>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Department</th>
                <th className="px-6 py-4">Year</th>
                <th className="px-6 py-4">Roll Number</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10 text-slate-100">
              {loading ? (
                <tr><td className="px-6 py-8" colSpan={8}>Loading registrations...</td></tr>
              ) : items.length === 0 ? (
                <tr><td className="px-6 py-8" colSpan={8}>No registrations found.</td></tr>
              ) : items.map((item) => (
                <tr key={item.id} className="hover:bg-white/5">
                  <td className="px-6 py-4 font-medium text-cyan-300">{item.registration_number}</td>
                  <td className="px-6 py-4">{`${item.first_name ?? ''} ${item.last_name ?? ''}`.trim()}</td>
                  <td className="px-6 py-4">{item.department}</td>
                  <td className="px-6 py-4">{item.academic_year}</td>
                  <td className="px-6 py-4">{item.roll_number}</td>
                  <td className="px-6 py-4">
                    {item.status}
                    {item.status === 'approved' ? <div className="text-xs text-slate-400">Pass: Generated</div> : null}
                  </td>
                  <td className="px-6 py-4">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <Link to={`/admin/registrations/${item.id}`} className="rounded-full border border-white/10 px-3 py-2 text-sm text-cyan-300 transition hover:bg-white/5">
                      {item.status === 'pending' ? 'Review' : 'View'}
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
            <button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="rounded-xl border border-white/10 px-3 py-2 disabled:opacity-40">Prev</button>
            <span>Page {page} of {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)} className="rounded-xl border border-white/10 px-3 py-2 disabled:opacity-40">Next</button>
          </div>
        </div>
      </div>
    </div>
  )
}
