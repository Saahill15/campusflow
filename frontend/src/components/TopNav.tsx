import React from 'react'
import { useAuth } from '../context/AuthContext'

export default function TopNav() {
  const { user, logout } = useAuth()

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center px-6 justify-between">
      <div className="flex items-center space-x-4">
        <div className="text-lg font-semibold">{user ? `Welcome, ${user.name}` : 'CampusFlow'}</div>
      </div>
      <div className="flex items-center space-x-4">
        {user ? (
          <button onClick={logout} className="text-sm text-slate-600">Logout</button>
        ) : (
          <div className="text-sm text-slate-500">Not signed in</div>
        )}
      </div>
    </header>
  )
}
