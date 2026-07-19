import { useAuth } from '../context/AuthContext'

export const usePermissions = () => {
  const { permissions, hasPermission } = useAuth()
  return {
    permissions,
    hasPermission,
  }
}
