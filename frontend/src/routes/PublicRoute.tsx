import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function PublicRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated, user } = useAuth()

  if (isAuthenticated && user) {
    if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />
    if (user.role === 'committee') return <Navigate to="/committee/dashboard" replace />
    if (user.role === 'scanner') return <Navigate to="/scanner" replace />
    return <Navigate to="/student/dashboard" replace />
  }

  return children
}
