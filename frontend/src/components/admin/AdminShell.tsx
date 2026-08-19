import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'

const navItems = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/registrations', label: 'Registrations' },
  { to: '/admin/settings', label: 'Settings' },
  { to: '/admin/security-volunteers', label: 'Security Volunteers' },
]

export default function AdminShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/admin/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex bg-slate-950 text-white">
      <aside className="hidden w-72 border-r border-white/10 bg-slate-900/90 px-5 py-6 md:block">
        <div className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 3.0</div>
        <div className="mt-2 text-xl font-semibold">Admin Portal</div>
        <nav className="mt-8 flex flex-col gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `rounded-2xl px-4 py-3 text-sm transition ${isActive ? 'bg-cyan-400 text-slate-950' : 'text-slate-300 hover:bg-white/5'}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1">
        <header className="flex items-center justify-between border-b border-white/10 bg-slate-900/80 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Admin</p>
            <h1 className="text-lg font-semibold">Pragyarambh 3.0</h1>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-300">
            <span>{user?.email ?? 'admin'}</span>
            <button onClick={handleLogout} className="rounded-full border border-white/10 px-4 py-2 text-white transition hover:bg-white/5">Logout</button>
          </div>
        </header>
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
