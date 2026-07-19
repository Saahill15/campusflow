import React from 'react'
import { NavLink } from 'react-router-dom'

const items = [
  { to: '/', label: 'Home' },
  { to: '/student', label: 'Student' },
  { to: '/committee', label: 'Committee' },
  { to: '/admin', label: 'Admin' },
  { to: '/scanner', label: 'Scanner' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-4 hidden md:block">
      <div className="mb-6 text-xl font-semibold">CampusFlow</div>
      <nav className="flex flex-col space-y-2">
        {items.map((it) => (
          <NavLink key={it.to} to={it.to} className={({ isActive }) => `px-3 py-2 rounded ${isActive ? 'bg-amber-100 text-amber-700' : 'text-slate-700 hover:bg-gray-50'}`}>
            {it.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
