import React from 'react'
import { Link } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'

export default function AdminHomePage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-8 text-white shadow-xl shadow-black/20">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Admin Portal</p>
        <h1 className="mt-2 text-3xl font-semibold">Welcome{user ? `, ${user.name}` : ''}</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-300">Use the registrations section to review student submissions. Approval and pass generation will be added in a later phase.</p>
        <div className="mt-6">
          <Link to="/admin/registrations" className="inline-flex items-center rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
            Open Registrations
          </Link>
        </div>
      </div>
    </div>
  )
}
