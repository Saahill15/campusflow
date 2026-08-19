import React from 'react'
import { Check, CircleAlert, Clock3, X } from 'lucide-react'

export function AdminPageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description?: string; action?: React.ReactNode }) {
  return <header className="admin-page-header"><div><p className="admin-eyebrow">{eyebrow}</p><h1>{title}</h1>{description ? <p className="admin-page-description">{description}</p> : null}</div>{action ? <div className="admin-page-action">{action}</div> : null}</header>
}

export function AdminSurface({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <section className={`admin-surface ${className}`}>{children}</section>
}

export function AdminBadge({ value, fallback = 'Not set' }: { value?: string | null; fallback?: string }) {
  const normalized = String(value ?? '').toLowerCase()
  const tone = ['approved', 'verified', 'issued', 'active', 'checked_in', 'true', 'paid'].includes(normalized) ? 'success' : ['rejected', 'inactive', 'false', 'cancelled'].includes(normalized) ? 'danger' : ['pending', 'awaiting'].includes(normalized) ? 'warning' : 'neutral'
  const Icon = tone === 'success' ? Check : tone === 'danger' ? X : tone === 'warning' ? Clock3 : CircleAlert
  return <span className={`admin-badge admin-badge-${tone}`}><Icon size={12} aria-hidden />{value ? value.replaceAll('_', ' ') : fallback}</span>
}

export function AdminNotice({ tone = 'error', children }: { tone?: 'error' | 'success' | 'warning'; children: React.ReactNode }) {
  return <div className={`admin-notice admin-notice-${tone}`} role="status">{children}</div>
}

export function AdminSectionHeading({ eyebrow, title, action }: { eyebrow?: string; title: string; action?: React.ReactNode }) {
  return <div className="admin-section-heading"><div>{eyebrow ? <p className="admin-eyebrow">{eyebrow}</p> : null}<h2>{title}</h2></div>{action}</div>
}
