import React, { useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Activity, LayoutDashboard, LogOut, Menu, Settings2, ShieldCheck, Users, X } from 'lucide-react'

import { useAuth } from '../../context/AuthContext'

const navGroups = [
  { label: 'Overview', items: [{ to: '/admin', label: 'Dashboard', icon: LayoutDashboard }] },
  { label: 'Registrations', items: [{ to: '/admin/registrations', label: 'All Registrations', icon: Users }] },
  { label: 'Operations', items: [{ to: '/admin/check-in', label: 'Check-in Overview', icon: Activity }, { to: '/admin/security-volunteers', label: 'Security Volunteers', icon: ShieldCheck }, { to: '/security/scanner', label: 'Security Scanner', icon: ShieldCheck }] },
  { label: 'System', items: [{ to: '/admin/settings', label: 'Settings', icon: Settings2 }] },
]

export default function AdminShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/admin/login', { replace: true })
  }

  const pageTitle = location.pathname === '/admin' ? 'Command center' : location.pathname.includes('registrations') ? 'Registrations' : location.pathname.includes('check-in') ? 'Check-in overview' : location.pathname.includes('security-volunteers') ? 'Security volunteers' : location.pathname.includes('settings') ? 'Settings' : 'Operations'
  return <div className="admin-app"><aside className={`admin-sidebar ${mobileOpen ? 'open' : ''}`}><div className="admin-brand"><span className="admin-brand-mark">P3</span><span>PRAGYARAMBH <small className="text-[10px] text-[#d3a654]">ADMIN</small></span></div><nav className="admin-nav">{navGroups.map((group) => <React.Fragment key={group.label}><p className="admin-nav-group">{group.label}</p>{group.items.map((item) => { const Icon = item.icon; return <NavLink key={item.to} to={item.to} end={item.to === '/admin'} onClick={() => setMobileOpen(false)} className={({ isActive }) => `admin-nav-link ${isActive ? 'active' : ''}`}><Icon size={17} strokeWidth={1.7} /><span>{item.label}</span></NavLink> })}</React.Fragment>)}</nav><div className="admin-sidebar-footer"><p className="truncate text-xs text-[#f4eadb]">{user?.email ?? 'admin'}</p><button className="admin-nav-link mt-3 w-full !border-0 !px-0" onClick={handleLogout}><LogOut size={17} /><span>Log out</span></button></div></aside><div className="admin-main"><header className="admin-topbar"><div className="flex min-w-0 items-center gap-3"><button className="admin-mobile-menu" aria-label={mobileOpen ? 'Close navigation' : 'Open navigation'} onClick={() => setMobileOpen((open) => !open)}>{mobileOpen ? <X size={19} /> : <Menu size={19} />}</button><div className="min-w-0"><p className="admin-topbar-kicker">Pragyarambh 2026 / Operations</p><p className="admin-topbar-title truncate">{pageTitle}</p></div></div><div className="hidden items-center gap-3 text-right sm:flex"><p className="text-xs text-[#b9a891]">Signed in as<br /><span className="text-[#f4eadb]">{user?.name || 'Admin'}</span></p><div className="grid h-9 w-9 place-items-center border border-[#d3a654]/35 bg-[#d3a654]/10 text-xs font-bold text-[#d3a654]">{(user?.name || 'A').slice(0, 1).toUpperCase()}</div></div></header><main className="admin-content"><Outlet /></main></div>{mobileOpen ? <button aria-label="Close navigation overlay" className="fixed inset-0 z-30 bg-black/50 md:hidden" onClick={() => setMobileOpen(false)} /> : null}</div>
}
