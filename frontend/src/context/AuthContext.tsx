import React, { createContext, useCallback, useContext, useEffect, useMemo, useState, ReactNode } from 'react'
import { registerRefreshSessionHandler } from '../lib/api'
import { resolveApiUrl } from '../utils/env'

export type Role = 'student' | 'committee' | 'admin' | 'security_volunteer' | 'scanner' | 'guest'
export type Permission = 'view_dashboard' | 'manage_students' | 'scan' | 'manage_system' | 'review_access'

export type User = {
  id: string
  name: string
  email: string
  role: Role
  permissions: Permission[]
}

type Credentials = {
  email: string
  password: string
}

type LegacyLoginPayload = {
  id: string
  name: string
  email: string
  role: Role
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
  login: (credentials: Credentials | LegacyLoginPayload, remember?: boolean) => Promise<User>
  logout: () => Promise<void>
  refreshSession: () => Promise<boolean>
  hasRole: (roles: Role | Role[]) => boolean
  hasPermission: (permission: Permission) => boolean
}

const STORAGE_KEY = 'campusflow_auth'

const rolePriority: Role[] = ['admin', 'security_volunteer', 'committee', 'scanner', 'student', 'guest']

const rolePermissions: Record<Role, Permission[]> = {
  student: ['view_dashboard'],
  committee: ['view_dashboard', 'scan'],
  admin: ['view_dashboard', 'manage_students', 'manage_system', 'review_access'],
  security_volunteer: ['scan'],
  scanner: ['view_dashboard', 'scan'],
  guest: [],
}

const mapRole = (roles: string[] | undefined | null): Role => {
  const normalized = new Set((roles ?? []).map((role) => role.toLowerCase()))
  return rolePriority.find((role) => normalized.has(role)) ?? 'student'
}

const mapPermissions = (permissions: string[] | undefined | null): Permission[] => {
  const allowed = new Set<Permission>(['view_dashboard', 'manage_students', 'scan', 'manage_system', 'review_access'])
  return (permissions ?? []).filter((permission): permission is Permission => allowed.has(permission as Permission))
}

const requestJson = async (url: string, init?: RequestInit) => {
  const resolvedUrl = resolveApiUrl(url)

  const response = await fetch(resolvedUrl, {
    credentials: 'same-origin',
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(payload?.detail || payload?.error || 'Request failed')
  }
  return payload
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
    return JSON.parse(raw) as AuthSession
  } catch {
    return null
  }
}

const readStoredToken = () => {
  const stored = loadStoredSession()
  return stored?.token ?? null
}

const getResponseData = <T,>(payload: T | { data?: T } | null | undefined): T | null => {
  if (!payload) return null
  if (typeof payload === 'object' && 'data' in payload && payload.data !== undefined) {
    return payload.data as T
  }
  return payload as T
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const buildUser = (me: { id: string | number; email: string; roles?: string[]; permissions?: string[] }): User => ({
  id: String(me.id),
  name: me.email.split('@')[0],
  email: me.email,
  role: mapRole(me.roles),
  permissions: mapPermissions(me.permissions),
})

const buildSession = (me: { id: string | number; email: string; roles?: string[]; permissions?: string[] }, token: string, refreshToken: string, remember: boolean): AuthSession => ({
  user: buildUser(me),
  token,
  refreshToken,
  expiresAt: Date.now() + 15 * 60 * 1000,
  remember,
})

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

  const logout = useCallback(async () => {
    const currentRefreshToken = refreshToken ?? loadStoredSession()?.refreshToken
    if (currentRefreshToken) {
      try {
        await requestJson('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: currentRefreshToken }),
        })
      } catch {
        // best-effort logout; always clear local state
      }
    }

    setUser(null)
    setToken(null)
    setRefreshToken(null)
    setPermissions([])
    clearStoredSession()
  }, [refreshToken])

  const fetchMe = useCallback(async (accessToken: string) => {
    const payload = await requestJson('/auth/me', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })

    const me = getResponseData<{
      id: string | number
      email: string
      roles?: string[]
      permissions?: string[]
    } | null>(payload)

    if (!me) {
      throw new Error('User profile response was empty')
    }

    return me
  }, [])

  const login = useCallback(async (credentials: Credentials | LegacyLoginPayload, remember = true) => {
    if ('id' in credentials && 'role' in credentials) {
      const permissions = rolePermissions[credentials.role] ?? []
      const session: AuthSession = {
        user: { ...credentials, permissions },
        token: `legacy-${Math.random().toString(36).slice(2)}`,
        refreshToken: `legacy-${Math.random().toString(36).slice(2)}`,
        expiresAt: Date.now() + 15 * 60 * 1000,
        remember,
      }
      setSession(session, remember)
      return session.user
    }

    const loginPayload = await requestJson('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })

    const authData = getResponseData<{ access_token: string; refresh_token: string } | null>(loginPayload)
    if (!authData) {
      throw new Error('Login response was empty')
    }

    const me = await fetchMe(authData.access_token)
    const session = buildSession(me, authData.access_token, authData.refresh_token, remember)
    setSession(session, remember)
    return session.user
  }, [fetchMe, setSession])

  const refreshSession = useCallback(async (): Promise<boolean> => {
    const stored = loadStoredSession()
    const currentRefreshToken = refreshToken ?? stored?.refreshToken
    if (!currentRefreshToken) {
      await logout()
      return false
    }

    if (stored && stored.expiresAt > Date.now()) {
      setSession(stored, stored.remember)
      return true
    }

    try {
      const refreshed = await requestJson('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: currentRefreshToken }),
      })
      const authData = getResponseData<{ access_token: string; refresh_token: string } | null>(refreshed)
      if (!authData) {
        throw new Error('Refresh response was empty')
      }
      const me = await fetchMe(authData.access_token)
      const session = buildSession(me, authData.access_token, authData.refresh_token, stored?.remember ?? true)
      setSession(session, session.remember)
      return true
    } catch {
      await logout()
      return false
    }
  }, [fetchMe, logout, refreshToken, setSession])

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
      if (!refreshed) {
        await logout()
      }
      setIsInitialized(true)
    }

    restore()
  }, [logout, refreshSession, setSession])

  useEffect(() => {
    registerRefreshSessionHandler(refreshSession)
  }, [refreshSession])

  useEffect(() => {
    const storedToken = readStoredToken()
    if (storedToken && !token) {
      // keep the axios helper aligned with the active auth session
    }
  }, [token])

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
