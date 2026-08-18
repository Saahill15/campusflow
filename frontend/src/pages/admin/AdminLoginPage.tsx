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
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/90 p-8 shadow-2xl shadow-black/40">
        <div className="mb-8 space-y-2">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 3.0</p>
          <h1 className="text-3xl font-semibold">Admin Login</h1>
          <p className="text-sm text-slate-400">Sign in with an admin account to access registration management.</p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <label className="block text-sm text-slate-200">
            Email
            <div className="mt-2 relative">
              <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <Input className="pl-11" type="email" placeholder="admin@example.com" {...register('email')} />
            </div>
            {errors.email ? <p className="mt-1 text-sm text-red-400">{errors.email.message}</p> : null}
          </label>

          <label className="block text-sm text-slate-200">
            Password
            <div className="mt-2 relative">
              <Lock className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <Input className="pl-11" type="password" placeholder="Enter your password" {...register('password')} />
            </div>
            {errors.password ? <p className="mt-1 text-sm text-red-400">{errors.password.message}</p> : null}
          </label>

          {error ? <div className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-100">{error}</div> : null}

          <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={loading}>
            Continue
          </Button>
        </form>
      </div>
    </div>
  )
}
