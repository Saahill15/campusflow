import React, { useEffect, useState } from 'react'

import api from '../../lib/api'
import { Button } from '../../components/ui'

type SystemSettings = {
  registration_enabled: boolean
  checkin_enabled: boolean
  email_enabled: boolean
  maintenance_mode: boolean
}

const settingItems: Array<{ key: keyof SystemSettings; label: string; description: string; danger?: boolean }> = [
  { key: 'registration_enabled', label: 'Registration', description: 'Controls whether new student registrations can be submitted.' },
  { key: 'checkin_enabled', label: 'Check-in', description: 'Controls whether attendance and check-in operations are currently allowed.' },
  { key: 'email_enabled', label: 'Email Sending', description: 'Controls application-generated registration and approval emails.' },
  { key: 'maintenance_mode', label: 'Maintenance Mode', description: 'Places the public application into maintenance mode.', danger: true },
]

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<keyof SystemSettings | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadSettings = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.get<SystemSettings>('/admin/settings')
      setSettings(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to load system settings.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSettings()
  }, [])

  const updateSetting = async (key: keyof SystemSettings) => {
    if (!settings || saving) return
    const nextValue = !settings[key]
    setSaving(key)
    setError('')
    setMessage('')
    try {
      const response = await api.patch<SystemSettings>('/admin/settings', { [key]: nextValue })
      setSettings(response.data)
      setMessage(`${settingItems.find((item) => item.key === key)?.label} setting updated.`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Unable to update system settings.')
    } finally {
      setSaving(null)
    }
  }

  return (
    <div className="space-y-6 text-slate-100">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Admin Controls</p>
        <h1 className="mt-2 text-3xl font-semibold text-white">Settings</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Manage the live controls for registration, attendance, email delivery, and public availability.</p>
      </div>

      {error ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{error}</div> : null}
      {message ? <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</div> : null}

      {loading ? <div className="h-80 animate-pulse rounded-3xl border border-white/10 bg-slate-900/80" /> : settings ? <div className="grid gap-4 lg:grid-cols-2">
        {settingItems.map((item) => {
          const enabled = settings[item.key]
          const isSaving = saving === item.key
          return <section key={item.key} className={`rounded-3xl border p-6 ${item.danger ? 'border-amber-300/30 bg-amber-400/[0.06]' : 'border-white/10 bg-slate-900/80'}`}>
            <div className="flex items-start justify-between gap-5">
              <div>
                <h2 className="text-lg font-semibold text-white">{item.label}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">{item.description}</p>
              </div>
              <span className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${enabled ? 'border-emerald-300/25 bg-emerald-400/10 text-emerald-200' : 'border-rose-300/25 bg-rose-400/10 text-rose-200'}`}>{enabled ? 'ON' : 'OFF'}</span>
            </div>
            <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4">
              <span className="text-sm text-slate-300">{enabled ? 'Currently enabled' : 'Currently disabled'}</span>
              <Button type="button" variant={enabled ? 'secondary' : 'success'} onClick={() => void updateSetting(item.key)} isLoading={isSaving} disabled={saving !== null}>{enabled ? 'Turn Off' : 'Turn On'}</Button>
            </div>
          </section>
        })}
      </div> : <Button variant="secondary" onClick={() => void loadSettings()}>Retry</Button>}
    </div>
  )
}
