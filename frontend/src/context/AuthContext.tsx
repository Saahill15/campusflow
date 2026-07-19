import React, { createContext, useContext, useEffect, useMemo, useState, useCallback, ReactNode } from 'react'
import { registerRefreshSessionHandler } from '../lib/api'

export type Role = 'student' | 'committee' | 'admin' | 'scanner' | 'guest'
export type Permission = 'view_dashboard' | 'manage_students' | 'scan' | 'manage_system' | 'review_access'

export type User = {
  id: string
  name: string
  email: string
  role: Role
  permissions: Permission[]
}

type AuthSession = {
  user: User
  token: string
  refreshToken: string
  expiresAt: number
  remember: boolean
}

type AuthContextValue = {
  user: User | null
  token: string | null
  refreshToken: string | null
  permissions: Permission[]
  isAuthenticated: boolean
  isInitialized: boolean
  login: (user: Omit<User, 'permissions'>, remember?: boolean) => Promise<void>
  logout: () => void
  refreshSession: () => Promise<boolean>
  hasRole: (roles: Role | Role[]) => boolean
  hasPermission: (permission: Permission) => boolean
}

const STORAGE_KEY = 'campusflow_auth'

const rolePermissions: Record<Role, Permission[]> = {
  student: ['view_dashboard'],
  committee: ['view_dashboard', 'scan'],
  admin: ['view_dashboard', 'manage_students', 'manage_system'],
  scanner: ['view_dashboard', 'scan'],
  guest: [],
}

const createMockSession = (user: Omit<User, 'permissions'>): AuthSession => {
  const permissions = rolePermissions[user.role] ?? []
  return {
    user: { ...user, permissions },
    token: `jwt-${Math.random().toString(36).slice(2)}`,
    refreshToken: `refresh-${Math.random().toString(36).slice(2)}`,
    expiresAt: Date.now() + 15 * 60 * 1000,
    remember: true,
  }
}

const storeSession = (session: AuthSession) => {
  if (!session.remember) return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
}

const clearStoredSession = () => {
  localStorage.removeItem(STORAGE_KEY)
}

const loadStoredSession = (): AuthSession | null => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as AuthSession
    return parsed
  } catch {
    return null
  }
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [isInitialized, setIsInitialized] = useState(false)

  const setSession = useCallback((session: AuthSession, persist: boolean) => {
    setUser(session.user)
    setToken(session.token)
    setRefreshToken(session.refreshToken)
    setPermissions(session.user.permissions)
    if (persist) storeSession(session)
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    setRefreshToken(null)
    setPermissions([])
    clearStoredSession()
  }, [])

  const login = useCallback(async (userPayload: Omit<User, 'permissions'>, remember = true) => {
    const session = createMockSession(userPayload)
    session.remember = remember
    setSession(session, remember)
  }, [setSession])

  const refreshSession = useCallback(async (): Promise<boolean> => {
    const stored = loadStoredSession()
    if (!stored || !stored.refreshToken) {
      logout()
      return false
    }

    if (stored.expiresAt > Date.now()) {
      setSession(stored, stored.remember)
      return true
    }

    const refreshed: AuthSession = {
      ...stored,
      token: `jwt-${Math.random().toString(36).slice(2)}`,
      refreshToken: `refresh-${Math.random().toString(36).slice(2)}`,
      expiresAt: Date.now() + 15 * 60 * 1000,
    }

    setSession(refreshed, stored.remember)
    return true
  }, [logout, setSession])

  const hasRole = useCallback(
    (roles: Role | Role[]) => {
      if (!user) return false
      return Array.isArray(roles) ? roles.includes(user.role) : roles === user.role
    },
    [user]
  )

  const hasPermission = useCallback(
    (permission: Permission) => permissions.includes(permission),
    [permissions]
  )

  useEffect(() => {
    const restore = async () => {
      const stored = loadStoredSession()
      if (!stored) {
        setIsInitialized(true)
        return
      }

      if (stored.expiresAt > Date.now()) {
        setSession(stored, stored.remember)
        setIsInitialized(true)
        return
      }

      const refreshed = await refreshSession()
      if (!refreshed) logout()
      setIsInitialized(true)
    }

    restore()
  }, [logout, refreshSession, setSession])

  useEffect(() => {
    registerRefreshSessionHandler(refreshSession)
  }, [refreshSession])

  const value = useMemo(
    () => ({
      user,
      token,
      refreshToken,
      permissions,
      isAuthenticated: Boolean(user && token),
      isInitialized,
      login,
      logout,
      refreshSession,
      hasRole,
      hasPermission,
    }),
    [user, token, refreshToken, permissions, isInitialized, login, logout, refreshSession, hasRole, hasPermission]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
