import React, { useState } from 'react'
import { Link } from 'react-router-dom'

import { Button, Input } from '../../components/ui'
import api from '../../lib/api'

type StatusResponse = {
  found: boolean
  status?: string | null
  registration_number?: string | null
  message: string
  email_action_available?: boolean
}

type EmailResponse = {
  email_sent: boolean
  message: string
}

const statusTitle: Record<string, string> = {
  pending: 'Registration Pending',
  approved: 'Registration Approved',
  rejected: 'Registration Not Approved',
}

export default function CheckStatusPage() {
  const [email, setEmail] = useState('')
  const [result, setResult] = useState<StatusResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [error, setError] = useState('')
  const [emailMessage, setEmailMessage] = useState('')

  const checkStatus = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const normalizedEmail = email.trim().toLowerCase()
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(normalizedEmail)) {
      setError('Please enter a valid registered email address.')
      setResult(null)
      return
    }

    setLoading(true)
    setError('')
    setEmailMessage('')
    try {
      const response = await api.post<StatusResponse>('/registration/status', { email: normalizedEmail })
      setResult(response.data)
    } catch (err: any) {
      setResult(null)
      setError(err?.response?.data?.detail || err?.message || 'Unable to check registration status.')
    } finally {
      setLoading(false)
    }
  }

  const resendEmail = async () => {
    if (!result?.found) return
    setResendLoading(true)
    setEmailMessage('')
    setError('')
    const endpoint = result.status === 'approved' ? '/registration/status/resend-pass' : '/registration/status/resend-confirmation'
    try {
      const response = await api.post<EmailResponse>(endpoint, { email: email.trim().toLowerCase() })
      setEmailMessage(response.data.message)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to resend the email.')
    } finally {
      setResendLoading(false)
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#1A120D] px-4 py-8 text-[#E0D0B6] sm:px-6 lg:px-8">
      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-2xl items-center justify-center">
        <section className="w-full rounded-3xl border border-[#CC9E4C]/25 bg-[#21150F]/95 p-6 shadow-2xl sm:p-10">
          <Link to="/" className="text-xs font-black uppercase tracking-[0.2em] text-[#CC9E4C] hover:text-[#E0D0B6]">Back to Pragyarambh</Link>
          <p className="mt-10 text-xs font-black uppercase tracking-[0.3em] text-[#CC9E4C]">Pragyarambh 3.0</p>
          <h1 className="mt-3 text-4xl font-black leading-tight text-[#F7F0E8] sm:text-5xl">Check Status</h1>
          <p className="mt-4 max-w-xl text-sm leading-7 text-[#D4C5AC]">Enter the email address used during registration to view the latest registration status.</p>

          <form onSubmit={checkStatus} className="mt-8 space-y-4">
            <label className="block"><span className="mb-2 block text-sm text-[#D4C5AC]">Registered Email</span><Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="sahil@example.com" autoComplete="email" required /></label>
            <Button type="submit" variant="primary" className="w-full" isLoading={loading}>Check Status</Button>
          </form>

          {error ? <div className="mt-5 rounded-2xl border border-rose-300/25 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}
          {emailMessage ? <div className="mt-5 rounded-2xl border border-emerald-300/25 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{emailMessage}</div> : null}

          {result ? <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            {result.found ? <>
              <p className="text-xs uppercase tracking-[0.2em] text-[#CC9E4C]">{statusTitle[result.status || ''] || 'Registration Status'}</p>
              <h2 className="mt-2 text-2xl font-bold text-[#F7F0E8]">{result.status === 'approved' ? 'Registration Approved' : result.status === 'rejected' ? 'Registration Not Approved' : 'Registration Pending'}</h2>
              <p className="mt-3 text-sm leading-7 text-[#D4C5AC]">{result.message}</p>
              {result.registration_number ? <p className="mt-5 text-sm text-[#D4C5AC]">Registration Number <span className="ml-2 font-mono font-bold text-[#CC9E4C]">{result.registration_number}</span></p> : null}
              <div className="mt-6 border-t border-white/10 pt-5"><p className="text-sm font-semibold text-[#F7F0E8]">{result.status === 'approved' ? "Didn't receive your pass?" : "Didn't receive your confirmation email?"}</p><Button type="button" variant="secondary" className="mt-3" onClick={() => void resendEmail()} isLoading={resendLoading}>{result.status === 'approved' ? 'Send Pass Again' : 'Send Confirmation Again'}</Button></div>
            </> : <><p className="text-xs uppercase tracking-[0.2em] text-[#CC9E4C]">Status Lookup</p><p className="mt-3 text-sm leading-7 text-[#D4C5AC]">{result.message}</p></>}
          </div> : null}
        </section>
      </div>
    </main>
  )
}
