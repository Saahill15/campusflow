import { useAuth } from '../context/AuthContext'

export const useRole = () => {
  const { user, hasRole } = useAuth()
  return {
    role: user?.role ?? 'guest',
    hasRole,
  }
}
