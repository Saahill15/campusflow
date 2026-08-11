import React, { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'

import api from '../../lib/api'
import { Button, ConfirmDialog, Modal, Textarea } from '../../components/ui'
function PassPreview({ item, pass, qrToken }: any) {
  const [dataUrl, setDataUrl] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const gen = async () => {
      if (!qrToken) return
      try {
        // @ts-ignore - dynamic import of a JS module without types
        const QRCodeLib = await import('qrcode')
        const url = await QRCodeLib.toDataURL(qrToken, { width: 256 })
        if (mounted) setDataUrl(url)
      } catch (e) {
        console.error(e)
      }
    }
    gen()
    return () => { mounted = false }
  }, [qrToken])

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Pass Preview</div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <div className="text-sm text-slate-200 font-semibold">PRAGYARAMBH 2026</div>
          <div className="mt-2 text-sm text-white">Student: {item.first_name} {item.last_name}</div>
          <div className="text-sm text-white">Department: {item.department || '-'}</div>
          <div className="text-sm text-white">Year: {item.academic_year || '-'}</div>
          <div className="text-sm text-white">Roll: {item.roll_number || '-'}</div>
          <div className="text-sm text-white">Registration: {item.registration_number || '-'}</div>
          <div className="text-sm text-white">Pass: {pass.pass_number || '-'}</div>
        </div>
        <div className="flex items-center justify-center">
          {dataUrl ? <img src={dataUrl} alt="QR code" className="w-40 h-40" /> : <div className="text-sm text-slate-400">Generating QR...</div>}
        </div>
      </div>
    </div>
  )
}

type RegistrationDetail = {
  registration_number?: string
  first_name?: string
  last_name?: string
  department?: string
  academic_year?: string
  roll_number?: string
  phone?: string
  email?: string
  gender?: string
  status?: string
  created_at?: string
  approved_at?: string | null
  approved_by?: number | null
  rejected_reason?: string | null
}

export default function AdminRegistrationDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState<RegistrationDetail | null>(null)
  const [passData, setPassData] = useState<any | null>(null)
  const [passError, setPassError] = useState<string | null>(null)
  const [passLoading, setPassLoading] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionError, setActionError] = useState('')
  const [confirmApproveOpen, setConfirmApproveOpen] = useState(false)
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  const canReview = useMemo(() => item?.status === 'pending', [item])

  useEffect(() => {
    const load = async () => {
      if (!id) return
      setLoading(true)
      setError('')
      try {
        const response = await api.get<RegistrationDetail>(`/admin/registrations/${id}`)
        setItem(response.data)
        // load pass data if approved
        setPassError(null)
        if (response.data.status === 'approved') {
          setPassLoading(true)
          try {
            const pr = await api.get(`/admin/registrations/${id}/pass`)
            setPassData(pr.data)
          } catch (err: any) {
            setPassData(null)
            const detail = err?.response?.data?.detail || err?.message || 'Failed to fetch pass'
            setPassError(`Failed to load generated pass: ${detail}`)
          } finally {
            setPassLoading(false)
          }
        } else {
          setPassData(null)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load registration')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const handleApprove = async () => {
    if (!id) return
    setActionLoading(true)
    setActionError('')
    try {
      const response = await api.post<RegistrationDetail>(`/admin/registrations/${id}/approve`)
      setItem((current) => current ? { ...current, status: response.data.status, approved_at: response.data.approved_at } : current)
      setConfirmApproveOpen(false)
        // fetch pass info after approve
        setPassError(null)
        setPassLoading(true)
        try {
          const pr = await api.get(`/admin/registrations/${id}/pass`)
          setPassData(pr.data)
        } catch (err: any) {
          setPassData(null)
          const detail = err?.response?.data?.detail || err?.message || 'Failed to fetch pass'
          setPassError(`Failed to load generated pass: ${detail}`)
        } finally {
          setPassLoading(false)
        }
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to approve registration')
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async () => {
    if (!id) return
    if (!rejectionReason.trim()) {
      setActionError('Rejection reason is required.')
      return
    }
    setActionLoading(true)
    setActionError('')
    try {
      const response = await api.post<RegistrationDetail>(`/admin/registrations/${id}/reject`, { reason: rejectionReason.trim() })
      setItem((current) =>
        current
          ? {
              ...current,
              status: response.data.status,
              rejected_reason: response.data.rejected_reason,
              approved_at: null,
              approved_by: null,
            }
          : current,
      )
      setRejectDialogOpen(false)
        setPassData(null)
        setPassError(null)
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to reject registration')
    } finally {
      setActionLoading(false)
    }
  }

  if (error) {
    return <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">{error}</div>
  }

  if (loading || !item) {
    return <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6 text-slate-100">Loading registration...</div>
  }

  const personalFields = [
    ['First Name', item.first_name],
    ['Last Name', item.last_name],
    ['Gender', item.gender],
  ]

  const academicFields = [
    ['Department', item.department],
    ['Academic Year', item.academic_year],
    ['Roll Number', item.roll_number],
  ]

  const contactFields = [
    ['Phone', item.phone],
    ['Email', item.email],
  ]

  const auditFields = [
    ['Registration Number', item.registration_number],
    ['Status', item.status],
    ['Submitted', item.created_at ? new Date(item.created_at).toLocaleString() : '-'],
    ['Approved At', item.approved_at ? new Date(item.approved_at).toLocaleString() : '-'],
    ['Approved By', item.approved_by ? String(item.approved_by) : '-'],
    ['Rejection Reason', item.rejected_reason || '-'],
  ]

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 text-slate-100 shadow-xl shadow-black/20">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Registration Review</p>
            <h1 className="text-3xl font-semibold">{item.first_name} {item.last_name}</h1>
            <p className="mt-2 text-sm text-slate-400">Status: {item.status}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {canReview ? (
              <>
                <Button variant="success" onClick={() => setConfirmApproveOpen(true)} isLoading={actionLoading}>Approve Registration</Button>
                <Button variant="destructive" onClick={() => setRejectDialogOpen(true)} isLoading={actionLoading}>Reject Registration</Button>
              </>
            ) : null}
          </div>
        </div>
      </div>

          {actionError ? <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">{actionError}</div> : null}
          {passError ? <div className="rounded-2xl border border-yellow-500/20 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-100">{passError}</div> : null}

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-slate-100">Personal</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {personalFields.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
                  <p className="mt-2 text-sm text-white">{value || '-'}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-slate-100">Academic</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {academicFields.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
                  <p className="mt-2 text-sm text-white">{value || '-'}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-slate-100">Contact</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {contactFields.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
                  <p className="mt-2 text-sm text-white">{value || '-'}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="space-y-6">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-slate-100">Registration Audit</h2>
            <div className="mt-4 space-y-3">
              {auditFields.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
                  <p className="mt-2 text-sm text-white">{value || '-'}</p>
                </div>
              ))}
            </div>
          </section>
          {item.status === 'approved' && (
            passLoading ? (
              <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
                <h2 className="text-xl font-semibold text-slate-100">Pass</h2>
                <div className="mt-4">Loading pass...</div>
              </section>
            ) : passData ? (
            <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
              <h2 className="text-xl font-semibold text-slate-100">Pass</h2>
              <div className="mt-4 space-y-3">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Pass Number</p>
                  <p className="mt-2 text-sm text-white">{passData.pass_number || '-'}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Pass Status</p>
                  <p className="mt-2 text-sm text-white">{passData.status || '-'}</p>
                </div>
                <div className="mt-4">
                  <PassPreview item={item} pass={passData} qrToken={passData?.qr?.qr_token} />
                </div>
              </div>
            </section>
            ) : null
          )}
        </aside>
      </div>

      <ConfirmDialog
        open={confirmApproveOpen}
        title="Approve this registration?"
        description="Once approved, this registration will be marked as approved. Pass generation and email delivery are separate steps and will not happen yet."
        onConfirm={handleApprove}
        onCancel={() => setConfirmApproveOpen(false)}
      />

      <Modal open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} title="Reject Registration">
        <p className="text-sm text-slate-400">Provide a reason for rejecting this registration. This reason will be stored with the registration.</p>
        <div className="mt-4">
          <Textarea
            label="Rejection Reason"
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            rows={5}
          />
        </div>
        <div className="mt-4 flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
          <Button variant="destructive" onClick={handleReject} isLoading={actionLoading}>Reject Registration</Button>
        </div>
      </Modal>
    </div>
  )
}
