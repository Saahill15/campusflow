import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RoleRoute({ children, roles }: { children: JSX.Element; roles: string[] }) {
  const { isAuthenticated, user } = useAuth()

  if (!isAuthenticated || !user) return <Navigate to="/login" replace />
  if (!roles.includes(user.role)) return <Navigate to="/unauthorized" replace />
  return children
}
