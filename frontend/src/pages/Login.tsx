import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Mail, Lock, ArrowRight, CircleDollarSign } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Button, Input } from '../components/ui'
import PageContainer from '../components/PageContainer'

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  remember: z.boolean().optional(),
})

type LoginValues = z.infer<typeof loginSchema>

type Role = 'student' | 'committee' | 'admin'

const getRoleFromEmail = (email: string): Role => {
  const local = email.split('@')[0].toLowerCase()
  if (local.includes('admin')) return 'admin'
  if (local.includes('committee')) return 'committee'
  return 'student'
}

const getRedirectPath = (role: Role) => {
  switch (role) {
    case 'admin':
      return '/admin/dashboard'
    case 'committee':
      return '/committee/dashboard'
    default:
      return '/student/dashboard'
  }
}

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [authError, setAuthError] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { remember: true },
  })

  const onSubmit = ({ email, password, remember }: LoginValues) => {
    setAuthError('')
    setLoading(true)

    setTimeout(() => {
      const validPassword = password === 'campusflow'
      if (!validPassword) {
        setAuthError('Invalid email or password.')
        setLoading(false)
        return
      }

      const role = getRoleFromEmail(email)
      login({ id: `user-${Date.now()}`, name: 'CampusFlow User', email, role })
      toast.success(`Welcome back, ${role === 'student' ? 'Student' : role === 'committee' ? 'Committee' : 'Admin'}!`)
      navigate(getRedirectPath(role), { replace: true })
      setLoading(false)
    }, 800)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4 py-10">
      <PageContainer>
        <div className="mx-auto flex w-full max-w-2xl flex-col gap-8">
          <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-10 shadow-2xl shadow-black/40 backdrop-blur-xl">
            <div className="mb-10 flex flex-col gap-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm text-slate-100 ring-1 ring-white/10">
                <CircleDollarSign className="h-4 w-4" />
                CampusFlow Premium Login
              </div>
              <div>
                <p className="text-lg font-semibold text-white">Sign in to your campus workspace</p>
                <p className="mt-2 text-sm text-slate-400">Secure access for students, committee, and admin users.</p>
              </div>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid gap-4">
                <label className="block text-sm font-medium text-slate-200">
                  Email
                  <div className="mt-2 relative">
                    <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                    <Input
                      type="email"
                      placeholder="you@campusflow.com"
                      className="pl-11"
                      {...register('email')}
                    />
                  </div>
                </label>
                {errors.email ? <p className="text-sm text-red-400">{errors.email.message}</p> : null}

                <label className="block text-sm font-medium text-slate-200">
                  Password
                  <div className="mt-2 relative">
                    <Lock className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      className="pl-11"
                      {...register('password')}
                    />
                  </div>
                </label>
                {errors.password ? <p className="text-sm text-red-400">{errors.password.message}</p> : null}
              </div>

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <label className="inline-flex items-center gap-3 text-sm text-slate-300">
                  <input type="checkbox" className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-400" {...register('remember')} />
                  Remember me
                </label>
                <a href="#" className="text-sm text-slate-300 transition hover:text-white">Forgot password?</a>
              </div>

              {authError ? <div className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-100">{authError}</div> : null}

              <Button type="submit" className="w-full justify-center" variant="primary" size="lg" isLoading={loading}>
                <span className="flex items-center gap-2">
                  Login <ArrowRight className="h-4 w-4" />
                </span>
              </Button>
            </form>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 text-sm text-slate-400 shadow-lg shadow-black/20">
            <p className="font-medium text-slate-200">Login tips</p>
            <ul className="mt-4 space-y-3 list-disc pl-5">
              <li>Use an email with <span className="text-slate-100">admin</span>, <span className="text-slate-100">committee</span>, or any other value to select your role.</li>
              <li>Password must be at least 8 characters. Use <span className="text-slate-100">campusflow</span> for demo login.</li>
              <li>Your session can be remembered for easier access on this device.</li>
            </ul>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
