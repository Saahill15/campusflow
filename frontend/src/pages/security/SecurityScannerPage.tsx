import React, { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import { Navigate } from 'react-router-dom'

import api from '../../lib/api'
import { Button, Select } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'

type Gate = { id: string; name: string }
type ScanResult = {
  status: string
  message: string
  student_name?: string | null
  registration_number?: string | null
  pass_number?: string | null
  department?: string | null
  academic_year?: string | null
  event?: string | null
  checked_in?: boolean
  checked_in_at?: string | null
  entry_log_id?: string | null
}

const resultHeading: Record<string, string> = {
  VALID_PASS: 'VALID PASS',
  ALREADY_CHECKED_IN: 'ALREADY CHECKED IN',
  INVALID_QR: 'INVALID QR',
  PASS_NOT_FOUND: 'PASS NOT FOUND',
  ENTRY_NOT_ALLOWED: 'ENTRY NOT ALLOWED',
  CHECKIN_DISABLED: 'CHECK-IN DISABLED',
  CHECKED_IN: 'CHECK-IN SUCCESSFUL',
}

export default function SecurityScannerPage() {
  const { isInitialized, user, logout } = useAuth()
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const [gates, setGates] = useState<Gate[]>([])
  const [gateId, setGateId] = useState('')
  const [qrToken, setQrToken] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [cameraError, setCameraError] = useState('')
  const [apiError, setApiError] = useState('')
  const [scanning, setScanning] = useState(false)
  const [checkingIn, setCheckingIn] = useState(false)
  const [scannerKey, setScannerKey] = useState(0)
  const processingRef = useRef(false)

  useEffect(() => {
    if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return
    api.get<Gate[]>('/security/gates').then((response) => {
      setGates(response.data)
      if (response.data[0]) setGateId(response.data[0].id)
    }).catch((err: any) => setApiError(err?.response?.data?.detail || 'Unable to load event gates.'))
  }, [user])

  useEffect(() => {
    if (!gateId || result) return
    const scanner = new Html5Qrcode(`security-qr-reader-${scannerKey}`)
    scannerRef.current = scanner
    setCameraError('')
    setScanning(true)
    void scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 220, height: 220 }, aspectRatio: 1 },
      async (decodedText) => {
        if (processingRef.current) return
        processingRef.current = true
        setQrToken(decodedText)
        setScanning(false)
        try { await scanner.stop() } catch { /* Camera may stop during navigation. */ }
        try {
          const response = await api.post<ScanResult>('/security/scan', { qr_token: decodedText, gate_id: gateId })
          setResult(response.data)
        } catch (err: any) {
          setApiError(err?.response?.data?.detail || 'Unable to validate this QR code.')
          processingRef.current = false
        }
      },
      () => undefined,
    ).catch(() => {
      setScanning(false)
      setCameraError('Camera access is required to scan passes. Allow camera access in your browser settings, then try again.')
    })

    return () => {
      if (scannerRef.current === scanner) scannerRef.current = null
      void scanner.stop().catch(() => undefined)
      try { scanner.clear() } catch { /* Camera element may already be removed. */ }
    }
  }, [gateId, result, scannerKey])

  if (!isInitialized) return <div className="min-h-screen bg-slate-950 p-6 text-white">Loading...</div>
  if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return <Navigate to="/security/login" replace />

  const scanAgain = () => {
    setResult(null)
    setQrToken('')
    setApiError('')
    setCameraError('')
    processingRef.current = false
    setScannerKey((key) => key + 1)
  }

  const checkIn = async () => {
    if (!result || !gateId || checkingIn) return
    setCheckingIn(true)
    setApiError('')
    try {
      const response = await api.post<ScanResult>('/security/check-in', { qr_token: qrToken, gate_id: gateId })
      setResult(response.data)
    } catch (err: any) {
      setApiError(err?.response?.data?.detail || 'Unable to complete check-in.')
    } finally {
      setCheckingIn(false)
    }
  }

  return <main className="min-h-screen bg-slate-950 px-4 py-5 text-white sm:px-6"><div className="mx-auto max-w-xl space-y-5"><header className="flex items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 3.0</p><h1 className="mt-2 text-2xl font-semibold">Security Scanner</h1></div><Button variant="ghost" onClick={() => void logout()}>Log out</Button></header><Select label="Entry Gate" value={gateId} onChange={(event) => { setGateId(event.target.value); scanAgain() }} disabled={scanning || checkingIn}><option value="">Select a gate</option>{gates.map((gate) => <option key={gate.id} value={gate.id}>{gate.name}</option>)}</Select>{apiError ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{apiError}</div> : null}{!result ? <section className="rounded-3xl border border-white/10 bg-slate-900/90 p-4"><div id={`security-qr-reader-${scannerKey}`} className="overflow-hidden rounded-2xl bg-black" />{cameraError ? <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">{cameraError}</div> : null}<p className="mt-4 text-center text-sm text-slate-400">{scanning ? 'Point the camera at the student QR code.' : gateId ? 'Starting camera...' : 'Select an entry gate to start scanning.'}</p>{cameraError ? <Button variant="secondary" className="mt-4 w-full" onClick={scanAgain}>Try Camera Again</Button> : null}</section> : <section className={`rounded-3xl border p-6 ${result.status === 'VALID_PASS' ? 'border-emerald-300/30 bg-emerald-400/10' : result.status === 'ALREADY_CHECKED_IN' ? 'border-amber-300/30 bg-amber-400/10' : result.status === 'CHECKED_IN' ? 'border-cyan-300/30 bg-cyan-400/10' : 'border-rose-300/30 bg-rose-400/10'}`}><p className="text-center text-3xl font-black tracking-wide">{resultHeading[result.status] || 'SCAN RESULT'}</p><p className="mt-3 text-center text-sm text-slate-200">{result.message}</p>{result.student_name ? <div className="mt-6 grid gap-3 sm:grid-cols-2"><div><p className="text-xs text-slate-400">Student Name</p><p className="mt-1 text-sm font-semibold">{result.student_name}</p></div><div><p className="text-xs text-slate-400">Registration Number</p><p className="mt-1 text-sm font-semibold">{result.registration_number}</p></div><div><p className="text-xs text-slate-400">Pass Number</p><p className="mt-1 text-sm font-semibold">{result.pass_number}</p></div><div><p className="text-xs text-slate-400">Department</p><p className="mt-1 text-sm font-semibold">{result.department}</p></div><div><p className="text-xs text-slate-400">Academic Year</p><p className="mt-1 text-sm font-semibold">{result.academic_year}</p></div><div><p className="text-xs text-slate-400">Event</p><p className="mt-1 text-sm font-semibold">{result.event}</p></div>{result.checked_in_at ? <div className="sm:col-span-2"><p className="text-xs text-slate-400">Checked In At</p><p className="mt-1 text-sm font-semibold">{new Date(result.checked_in_at).toLocaleString()}</p></div> : null}</div> : null}<div className="mt-6 grid gap-3"><Button variant="success" onClick={() => void checkIn()} isLoading={checkingIn} disabled={result.status !== 'VALID_PASS'}>CHECK IN</Button><Button variant="secondary" onClick={scanAgain} disabled={checkingIn}>SCAN NEXT PASS</Button></div></section>}</div></main>
}
