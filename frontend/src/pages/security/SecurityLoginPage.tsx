import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button, Input } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'

export default function SecurityLoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const user = await login({ email, password })
      if (user.role !== 'security_volunteer' && user.role !== 'admin') {
        setError('You do not have security scanner access.')
        return
      }
      navigate('/security/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white"><section className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/90 p-8 shadow-2xl"><p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 3.0</p><h1 className="mt-3 text-3xl font-semibold">Security Scanner</h1><p className="mt-2 text-sm leading-6 text-slate-400">Sign in with your security volunteer account for event-day entry checks.</p><form onSubmit={submit} className="mt-8 space-y-5"><label className="block text-sm text-slate-200">Email<Input className="mt-2" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label className="block text-sm text-slate-200">Password<Input className="mt-2" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}<Button type="submit" className="w-full" size="lg" isLoading={loading}>Open Scanner</Button></form></section></main>
}
