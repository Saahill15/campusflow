import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import api from '../../lib/api'
import { Button, ConfirmDialog, Modal, Textarea } from '../../components/ui'

type RegistrationDetail = {
  id?: string
  user_id?: number | null
  registration_number?: string | null
  first_name?: string | null
  last_name?: string | null
  department?: string | null
  academic_year?: string | null
  roll_number?: string | null
  phone?: string | null
  email?: string | null
  gender?: string | null
  emergency_contact?: string | null
  sims_id?: string | null
  local_station?: string | null
  status?: string
  created_at?: string
  approved_at?: string | null
  approved_by?: number | null
  rejected_reason?: string | null
  payment_status?: string | null
  payment_mode?: string | null
  payment_amount?: number | null
  payment_reference?: string | null
  payment_proof?: string | null
  checked_in?: boolean | null
  checked_in_at?: string | null
  notes?: string | null
}

type PassData = {
  id: string
  pass_number?: string | null
  status?: string | null
  issued_at?: string | null
  qr?: { qr_token?: string | null } | null
}

const statusStyles: Record<string, string> = {
  pending: 'border-amber-300/20 bg-amber-400/10 text-amber-200',
  approved: 'border-emerald-300/20 bg-emerald-400/10 text-emerald-200',
  rejected: 'border-rose-300/20 bg-rose-400/10 text-rose-200',
}

const formatValue = (value?: string | number | null) => value === null || value === undefined || value === '' ? '-' : String(value)
const formatDate = (value?: string | null) => value ? new Date(value).toLocaleString() : '-'
const humanize = (value?: string | null) => value ? value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) : '-'

function StatusBadge({ value, fallback = '-' }: { value?: string | null; fallback?: string }) {
  return <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${statusStyles[value || ''] || 'border-white/10 bg-white/5 text-slate-300'}`}>{value ? humanize(value) : fallback}</span>
}

function InfoGrid({ fields }: { fields: Array<[string, string | number | null | undefined]> }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {fields.map(([label, value]) => (
        <div key={label} className="min-w-0 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</p>
          <p className="mt-2 break-words text-sm text-white">{formatValue(value)}</p>
        </div>
      ))}
    </div>
  )
}

function PassPreview({ item, pass, qrToken }: { item: RegistrationDetail; pass: PassData; qrToken?: string | null }) {
  const [dataUrl, setDataUrl] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    setDataUrl(null)
    if (!qrToken) return () => { mounted = false }

    const generatePreview = async () => {
      try {
        // @ts-ignore - qrcode is a JavaScript dependency without repository types
        const QRCodeLib = await import('qrcode')
        const url = await QRCodeLib.toDataURL(qrToken, { width: 320, margin: 1 })
        if (mounted) setDataUrl(url)
      } catch {
        if (mounted) setDataUrl(null)
      }
    }
    void generatePreview()
    return () => { mounted = false }
  }, [qrToken])

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 space-y-2">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Pragyarambh 3.0 Pass</p>
          <p className="break-words text-lg font-semibold text-white">{formatValue(pass.pass_number)}</p>
          <p className="text-sm text-slate-400">{formatValue(item.first_name)} {formatValue(item.last_name)}</p>
          <p className="text-sm text-slate-400">Generated: {formatDate(pass.issued_at)}</p>
        </div>
        <div className="flex min-h-[180px] w-full max-w-[220px] items-center justify-center rounded-xl bg-white p-3 sm:w-[220px]">
          {dataUrl ? <img src={dataUrl} alt="Pass QR code" className="h-auto w-full max-w-[190px]" /> : <span className="text-center text-xs text-slate-500">{qrToken ? 'Preparing QR preview...' : 'QR unavailable'}</span>}
        </div>
      </div>
      <div className="mt-5 grid gap-3 border-t border-white/10 pt-4 sm:grid-cols-3">
        <div><p className="text-xs text-slate-500">Registration</p><p className="mt-1 break-words text-sm text-white">{formatValue(item.registration_number)}</p></div>
        <div><p className="text-xs text-slate-500">Department</p><p className="mt-1 break-words text-sm text-white">{formatValue(item.department)}</p></div>
        <div><p className="text-xs text-slate-500">Academic Year</p><p className="mt-1 text-sm text-white">{formatValue(item.academic_year)}</p></div>
      </div>
    </div>
  )
}

export default function AdminRegistrationDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState<RegistrationDetail | null>(null)
  const [passData, setPassData] = useState<PassData | null>(null)
  const [passError, setPassError] = useState('')
  const [passLoading, setPassLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [confirmApproveOpen, setConfirmApproveOpen] = useState(false)
  const [confirmResendOpen, setConfirmResendOpen] = useState(false)
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
  const [paymentProofOpen, setPaymentProofOpen] = useState(false)
  const [passPreviewOpen, setPassPreviewOpen] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  const loadPass = async (registrationId: string) => {
    setPassLoading(true)
    setPassError('')
    try {
      const response = await api.get<PassData>(`/admin/registrations/${registrationId}/pass`)
      setPassData(response.data)
    } catch (err: any) {
      setPassData(null)
      if (err?.response?.status !== 404) setPassError(err?.response?.data?.detail || err?.message || 'Unable to load pass information')
    } finally {
      setPassLoading(false)
    }
  }

  const loadRegistration = async () => {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const response = await api.get<RegistrationDetail>(`/admin/registrations/${id}`)
      setItem(response.data)
      await loadPass(id)
    } catch (err: any) {
      setError(err?.response?.status === 404 ? 'Registration not found.' : err?.response?.data?.detail || err?.message || 'Unable to load registration')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadRegistration()
  }, [id])

  const handleApprove = async () => {
    if (!id) return
    setActionLoading(true)
    setActionError('')
    setActionMessage('')
    try {
      await api.post(`/admin/registrations/${id}/approve`)
      setConfirmApproveOpen(false)
      setActionMessage('Registration approved. Pass and QR information refreshed.')
      await loadRegistration()
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || err?.message || 'Unable to approve registration')
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
    setActionMessage('')
    try {
      await api.post(`/admin/registrations/${id}/reject`, { reason: rejectionReason.trim() })
      setRejectDialogOpen(false)
      setRejectionReason('')
      setActionMessage('Registration rejected. Details refreshed.')
      await loadRegistration()
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || err?.message || 'Unable to reject registration')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!id) return
    setActionLoading(true)
    setActionError('')
    try {
      const response = await api.get<Blob>(`/admin/registrations/${id}/pass/download`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = 'Pragyarambh_Pass.png'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      setActionMessage('Pass download started.')
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || err?.message || 'Unable to download pass')
    } finally {
      setActionLoading(false)
    }
  }

  const handleResend = async () => {
    if (!id) return
    setActionLoading(true)
    setActionError('')
    setActionMessage('')
    try {
      const response = await api.post<{ email_sent: boolean; message?: string }>(`/admin/registrations/${id}/resend-approval-email`)
      setConfirmResendOpen(false)
      setActionMessage(response.data.email_sent ? 'Approval email resent with the existing pass attached.' : (response.data.message || 'Email was not sent.'))
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || err?.message || 'Unable to resend approval email')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return <div className="space-y-6 text-slate-100"><div className="h-32 animate-pulse rounded-3xl border border-white/10 bg-slate-900/80" /><div className="grid gap-6 lg:grid-cols-2"><div className="h-80 animate-pulse rounded-3xl border border-white/10 bg-slate-900/80" /><div className="h-80 animate-pulse rounded-3xl border border-white/10 bg-slate-900/80" /></div></div>
  }

  if (error || !item) {
    return <div className="space-y-4"><Link to="/admin/registrations" className="text-sm text-cyan-300 hover:text-cyan-200">← Back to Registrations</Link><div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 p-5 text-sm text-rose-100">{error || 'Registration not found.'}</div><Button variant="secondary" onClick={() => void loadRegistration()}>Retry</Button></div>
  }

  const proof = item.payment_proof || ''
  const proofIsImage = proof.startsWith('data:image/')
  const proofIsOpenable = proofIsImage || proof.startsWith('https://') || proof.startsWith('http://')
  const fullName = [item.first_name, item.last_name].filter(Boolean).join(' ') || 'Unnamed student'

  return (
    <div className="min-w-0 space-y-6 text-slate-100">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <Link to="/admin/registrations" className="text-sm text-cyan-300 hover:text-cyan-200">← Back to Registrations</Link>
          <p className="mt-5 text-xs uppercase tracking-[0.3em] text-cyan-300">Registration Review</p>
          <h1 className="mt-2 break-words text-3xl font-semibold text-white">{fullName}</h1>
          <p className="mt-2 break-words text-sm text-slate-400">Registration #{formatValue(item.registration_number)} · ID {formatValue(item.id || id)}</p>
        </div>
        <StatusBadge value={item.status} />
      </div>

      {actionError ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{actionError}</div> : null}
      {actionMessage ? <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{actionMessage}</div> : null}
      {passError ? <div className="rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">{passError}</div> : null}

      {item.status === 'rejected' ? <section className="rounded-2xl border border-rose-300/25 bg-rose-400/10 p-5"><p className="text-xs uppercase tracking-[0.2em] text-rose-200">Rejection reason</p><p className="mt-2 break-words text-sm leading-6 text-rose-50">{formatValue(item.rejected_reason)}</p></section> : null}

      <div className="grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)]">
        <div className="min-w-0 space-y-6">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Student Details</h2>
            <div className="mt-5"><InfoGrid fields={[
              ['Full Name', fullName],
              ['Gender', item.gender],
              ['Email', item.email],
              ['Contact Number', item.phone],
              ['Emergency Contact', item.emergency_contact || 'Unavailable in current records'],
              ['Department', item.department],
              ['Academic Year', item.academic_year],
              ['Roll Number / SIMS ID', item.roll_number || item.sims_id],
              ['Nearest / Local Station', item.local_station || 'Unavailable in current records'],
            ]} /></div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Payment Information</h2>
            <div className="mt-5"><InfoGrid fields={[
              ['Payment Status', humanize(item.payment_status)],
              ['Payment Mode', item.payment_mode],
              ['Payment Amount', item.payment_amount === null || item.payment_amount === undefined ? null : `₹${item.payment_amount.toFixed(2)}`],
              ['Payment Reference', item.payment_reference],
            ]} /></div>
            <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Payment Proof</p>
              {proof ? <div className="mt-3 flex flex-wrap items-center gap-3"><span className="text-sm text-slate-300">Protected proof available</span>{proofIsImage ? <Button variant="secondary" onClick={() => setPaymentProofOpen(true)}>View Proof</Button> : proofIsOpenable ? <a href={proof} target="_blank" rel="noreferrer" className="rounded-xl border border-white/10 px-3 py-2 text-sm text-cyan-300 hover:bg-white/5">Open Proof</a> : <span className="text-sm text-slate-500">Stored format cannot be previewed safely.</span>}</div> : <p className="mt-2 text-sm text-slate-500">No payment proof supplied.</p>}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Pass</h2>
            {passLoading ? <div className="mt-5 h-48 animate-pulse rounded-2xl bg-white/5" /> : passData ? <div className="mt-5 space-y-4"><div className="grid gap-3 sm:grid-cols-3"><div><p className="text-xs text-slate-500">Pass Number</p><p className="mt-1 break-words text-sm text-white">{formatValue(passData.pass_number)}</p></div><div><p className="text-xs text-slate-500">Pass Status</p><p className="mt-1"><StatusBadge value={passData.status} /></p></div><div><p className="text-xs text-slate-500">Generated At</p><p className="mt-1 text-sm text-white">{formatDate(passData.issued_at)}</p></div></div><div className="flex flex-wrap gap-3"><Button variant="secondary" onClick={() => setPassPreviewOpen(true)}>View Pass</Button><Button variant="secondary" onClick={() => void handleDownload()} isLoading={actionLoading}>Download Pass</Button></div></div> : <div className="mt-5 rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-400">Pass Not Issued</div>}
          </section>
        </div>

        <aside className="min-w-0 space-y-6">
          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Registration</h2>
            <div className="mt-5"><InfoGrid fields={[
              ['Registration Number', item.registration_number],
              ['Registered At', formatDate(item.created_at)],
              ['Current Status', humanize(item.status)],
              ['Registration ID', item.id || id],
              ['Approved At', formatDate(item.approved_at)],
              ['Approved By', item.approved_by],
            ]} /></div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Check-in</h2>
            <div className="mt-5"><InfoGrid fields={[
              ['Status', item.checked_in ? 'Checked In' : 'Not Checked In'],
              ['Checked In At', formatDate(item.checked_in_at)],
            ]} /></div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Admin Actions</h2>
            {item.status === 'pending' ? <div className="mt-5 grid gap-3"><Button variant="success" onClick={() => setConfirmApproveOpen(true)} isLoading={actionLoading}>Approve Registration</Button><Button variant="destructive" onClick={() => setRejectDialogOpen(true)} isLoading={actionLoading}>Reject Registration</Button></div> : item.status === 'approved' ? <div className="mt-5 grid gap-3"><Button variant="secondary" onClick={() => setPassPreviewOpen(true)} disabled={!passData}>View Pass</Button><Button variant="secondary" onClick={() => void handleDownload()} isLoading={actionLoading} disabled={!passData}>Download Pass</Button><Button variant="secondary" onClick={() => setConfirmResendOpen(true)} isLoading={actionLoading} disabled={!passData}>Resend Approval Email</Button></div> : <p className="mt-4 text-sm leading-6 text-slate-400">No status-changing actions are available for this registration.</p>}
            <div className="mt-5 border-t border-white/10 pt-4"><p className="text-xs uppercase tracking-[0.18em] text-slate-500">Email history</p><p className="mt-2 text-sm leading-6 text-slate-400">Delivery history is not stored. Approved registrations can resend the existing pass email above.</p></div>
          </section>
        </aside>
      </div>

      <ConfirmDialog open={confirmApproveOpen} title="Approve this registration?" description="The existing approval flow will update the registration, create or reuse its pass and QR, and handle the approval notification." onConfirm={handleApprove} onCancel={() => setConfirmApproveOpen(false)} />
      <ConfirmDialog open={confirmResendOpen} title="Resend approval email?" description="The existing pass and QR will be reused. No registration, pass, or QR data will be changed." onConfirm={handleResend} onCancel={() => setConfirmResendOpen(false)} />

      <Modal open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} title="Reject Registration">
        <p className="text-sm text-slate-400">Provide a reason for rejecting this registration. The existing rejection workflow will store and notify this reason.</p>
        <div className="mt-4"><Textarea label="Rejection Reason" value={rejectionReason} onChange={(event) => setRejectionReason(event.target.value)} rows={5} /></div>
        <div className="mt-4 flex flex-wrap justify-end gap-3"><Button variant="secondary" onClick={() => setRejectDialogOpen(false)}>Cancel</Button><Button variant="destructive" onClick={() => void handleReject()} isLoading={actionLoading}>Reject Registration</Button></div>
      </Modal>

      <Modal open={paymentProofOpen} onClose={() => setPaymentProofOpen(false)} title="Payment Proof">
        <div className="max-h-[70vh] overflow-auto rounded-xl bg-slate-950 p-2"><img src={proof} alt="Payment proof" className="mx-auto h-auto max-w-full" /></div>
      </Modal>

      <Modal open={passPreviewOpen} onClose={() => setPassPreviewOpen(false)} title="Pass Preview">
        {passData ? <PassPreview item={item} pass={passData} qrToken={passData.qr?.qr_token} /> : null}
      </Modal>
    </div>
  )
}
