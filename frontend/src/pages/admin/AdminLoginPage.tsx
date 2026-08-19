import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Lock, Mail } from 'lucide-react'

import { useAuth } from '../../context/AuthContext'
import { Button, Input } from '../../components/ui'

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormValues = z.infer<typeof schema>

export default function AdminLoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (values: FormValues) => {
    setError('')
    setLoading(true)
    try {
      const user = await login({ email: values.email, password: values.password })
      if (user.role !== 'admin') {
        setError('You do not have admin access.')
        return
      }
      toast.success('Admin login successful')
      navigate('/admin', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-app flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
      <div className="pointer-events-none absolute left-[-8rem] top-[-8rem] h-80 w-80 rounded-full border border-[#d3a654]/20" />
      <div className="pointer-events-none absolute bottom-[-10rem] right-[-4rem] h-96 w-96 rounded-full border border-[#d3a654]/10" />
      <div className="relative w-full max-w-md border border-[#d3a654]/25 bg-[#24150f]/90 p-7 shadow-2xl shadow-black/40 sm:p-10">
        <div className="mb-8 space-y-3">
          <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center border border-[#d3a654]/50 text-xs font-bold text-[#d3a654]">P3</div><p className="text-xs font-bold uppercase tracking-[0.25em] text-[#f4eadb]">Pragyarambh 2026</p></div>
          <p className="admin-eyebrow pt-5">Private operations desk</p>
          <h1 className="font-[Space_Grotesk] text-4xl font-semibold tracking-[-.04em] text-[#f4eadb]">Welcome back.</h1>
          <p className="text-sm leading-6 text-[#b9a891]">Sign in to oversee registrations, approvals, and event readiness.</p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <label className="admin-field-label">
            Email
            <div className="mt-2 relative">
              <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <Input className="pl-11" type="email" placeholder="admin@example.com" {...register('email')} />
            </div>
            {errors.email ? <p className="mt-1 text-sm text-red-400">{errors.email.message}</p> : null}
          </label>

          <label className="admin-field-label">
            Password
            <div className="mt-2 relative">
              <Lock className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <Input className="pl-11" type="password" placeholder="Enter your password" {...register('password')} />
            </div>
            {errors.password ? <p className="mt-1 text-sm text-red-400">{errors.password.message}</p> : null}
          </label>

          {error ? <div className="admin-notice admin-notice-error">{error}</div> : null}

          <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={loading}>
            Continue
          </Button>
        </form>
      </div>
    </div>
  )
}
