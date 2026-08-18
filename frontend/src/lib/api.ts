import axios from 'axios'
import { resolveApiUrl } from '../utils/env'

let refreshHandler: (() => Promise<boolean>) | null = null

const baseURL = resolveApiUrl('/api/v1')

export const registerRefreshSessionHandler = (handler: () => Promise<boolean>) => {
  refreshHandler = handler
}

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('campusflow_auth')
    if (!raw) return config
    const session = JSON.parse(raw) as { token?: string }
    if (session?.token && config.headers) {
      config.headers.Authorization = `Bearer ${session.token}`
    }
  } catch (e) {
    // ignore parse errors
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const status = err.response?.status
    if (status === 401 && refreshHandler) {
      const refreshed = await refreshHandler()
      if (refreshed) {
        const originalRequest = err.config
        const raw = localStorage.getItem('campusflow_auth')
        if (raw) {
          const session = JSON.parse(raw) as { token?: string }
          if (session?.token) {
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${session.token}`
            return api(originalRequest)
          }
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api
