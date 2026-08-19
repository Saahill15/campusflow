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

  return <main className="security-screen flex items-center justify-center px-4 py-8"><section className="security-panel w-full max-w-md p-7 sm:p-10"><div className="flex items-center gap-3"><span className="admin-brand-mark">P3</span><p className="security-brand text-xs font-bold">PRAGYARAMBH 2026</p></div><p className="security-eyebrow mt-10">Security operations</p><h1 className="mt-3 text-4xl font-semibold tracking-[-.04em]">Volunteer login</h1><p className="mt-3 text-sm leading-6 text-[#b9a891]">Authorized security personnel only. Sign in to open event check-in operations.</p><form onSubmit={submit} className="mt-8 space-y-5"><label className="admin-field-label">Email<Input className="admin-control mt-2" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label className="admin-field-label">Password<Input className="admin-control mt-2" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error ? <div className="admin-notice admin-notice-error">{error}</div> : null}<Button type="submit" className="admin-button admin-button-primary w-full" size="lg" isLoading={loading}>Sign in</Button></form></section></main>
}
