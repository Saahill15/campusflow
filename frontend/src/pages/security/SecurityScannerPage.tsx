import React, { useEffect, useRef, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import { Navigate, useNavigate } from 'react-router-dom'

import api from '../../lib/api'
import { Button } from '../../components/ui'
import { useAuth } from '../../context/AuthContext'

type CameraState = 'INITIALIZING' | 'CAMERA_READY' | 'PERMISSION_DENIED' | 'CAMERA_UNAVAILABLE' | 'ERROR' | 'SCANNING' | 'RESULT'
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

const cameraMessage = (state: CameraState) => ({
  INITIALIZING: 'Preparing camera...',
  CAMERA_READY: 'Camera ready.',
  SCANNING: "Point the camera at the student's QR pass.",
  PERMISSION_DENIED: 'Camera access is required to scan passes.',
  CAMERA_UNAVAILABLE: 'No usable camera is available on this device.',
  ERROR: 'Camera could not be started.',
  RESULT: 'Camera paused while you review the pass.',
}[state])

export default function SecurityScannerPage() {
  const navigate = useNavigate()
  const { isInitialized, user, logout } = useAuth()
  const scannerRef = useRef<Html5Qrcode | null>(null)
  const startingRef = useRef(false)
  const processingRef = useRef(false)
  const [cameraState, setCameraState] = useState<CameraState>('INITIALIZING')
  const [cameraError, setCameraError] = useState('')
  const [qrToken, setQrToken] = useState('')
  const [result, setResult] = useState<ScanResult | null>(null)
  const [apiError, setApiError] = useState('')
  const [checkingIn, setCheckingIn] = useState(false)

  const stopScanner = async () => {
    const scanner = scannerRef.current
    scannerRef.current = null
    if (!scanner) return
    try { await scanner.stop() } catch { /* The camera may already be stopped. */ }
    try { scanner.clear() } catch { /* The container may already be gone. */ }
  }

  const classifyCameraError = (error: unknown) => {
    const name = error instanceof Error ? error.name : ''
    const message = error instanceof Error ? error.message.toLowerCase() : ''
    if (name === 'NotAllowedError' || message.includes('permission') || message.includes('denied')) {
      setCameraState('PERMISSION_DENIED')
      setCameraError(window.isSecureContext ? 'Camera access is required to scan passes.' : 'Camera access requires HTTPS on this device.')
      return
    }
    if (name === 'NotFoundError' || name === 'OverconstrainedError' || message.includes('camera')) {
      setCameraState('CAMERA_UNAVAILABLE')
      setCameraError('No usable camera is available on this device.')
      return
    }
    setCameraState('ERROR')
    setCameraError(window.isSecureContext ? 'Camera could not be started.' : 'Camera access requires HTTPS on this device.')
  }

  const startCamera = async () => {
    if (startingRef.current || result || !user) return
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraState('CAMERA_UNAVAILABLE')
      setCameraError('Camera access requires HTTPS and a supported browser.')
      return
    }
    startingRef.current = true
    setCameraState('INITIALIZING')
    setCameraError('')
    setApiError('')
    await stopScanner()
    const scanner = new Html5Qrcode('security-qr-reader')
    scannerRef.current = scanner
    const onDecode = async (decodedText: string) => {
      if (processingRef.current) return
      processingRef.current = true
      setCameraState('RESULT')
      setQrToken(decodedText)
      await stopScanner()
      try {
        const response = await api.post<ScanResult>('/security/scan', { qr_token: decodedText })
        setResult(response.data)
      } catch (err: any) {
        setApiError(err?.response?.data?.detail || 'Unable to validate this QR code.')
        processingRef.current = false
        await startCamera()
      }
    }
    try {
      try {
        await scanner.start(
          { facingMode: { exact: 'environment' } },
          { fps: 10, qrbox: { width: 220, height: 220 }, aspectRatio: 1 },
          onDecode,
          () => undefined,
        )
      } catch (preferredError) {
        const cameras = await Html5Qrcode.getCameras()
        if (!cameras.length) throw preferredError
        await scanner.start(
          cameras[0].id,
          { fps: 10, qrbox: { width: 220, height: 220 }, aspectRatio: 1 },
          onDecode,
          () => undefined,
        )
      }
      setCameraState('SCANNING')
    } catch (error) {
      await stopScanner()
      classifyCameraError(error)
    } finally {
      startingRef.current = false
    }
  }

  useEffect(() => {
    if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return
    void startCamera()
    return () => { void stopScanner() }
  }, [user])

  if (!isInitialized) return <div className="min-h-screen bg-slate-950 p-6 text-white">Loading...</div>
  if (!user || (user.role !== 'security_volunteer' && user.role !== 'admin')) return <Navigate to="/security/login" replace />

  const scanAgain = async () => {
    await stopScanner()
    setResult(null)
    setQrToken('')
    setApiError('')
    setCameraError('')
    processingRef.current = false
    void startCamera()
  }

  const checkIn = async () => {
    if (!result || checkingIn) return
    setCheckingIn(true)
    setApiError('')
    try {
      const response = await api.post<ScanResult>('/security/check-in', { qr_token: qrToken })
      setResult(response.data)
    } catch (err: any) {
      setApiError(err?.response?.data?.detail || 'Unable to complete check-in.')
    } finally {
      setCheckingIn(false)
    }
  }

  return <main className="min-h-screen overflow-x-hidden bg-slate-950 px-4 py-5 text-white sm:px-6"><div className="mx-auto max-w-xl space-y-5"><header className="flex items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Pragyarambh 2026</p><h1 className="mt-2 text-2xl font-semibold">Scan Pass</h1></div><Button variant="ghost" onClick={() => void logout()}>Log out</Button></header>{apiError ? <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">{apiError}</div> : null}{!result ? <section className="rounded-3xl border border-white/10 bg-slate-900/90 p-4"><div id="security-qr-reader" className="aspect-square w-full overflow-hidden rounded-2xl bg-black" />{cameraError ? <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">{cameraError}</div> : null}<p className="mt-4 text-center text-sm text-slate-300">{cameraMessage(cameraState)}</p>{cameraState !== 'SCANNING' ? <Button variant="secondary" className="mt-4 min-h-11 w-full" onClick={() => void startCamera()} disabled={cameraState === 'INITIALIZING'}>{cameraState === 'INITIALIZING' ? 'Preparing camera...' : 'Try Again'}</Button> : null}</section> : <section className={`rounded-3xl border p-6 ${result.status === 'VALID_PASS' ? 'border-emerald-300/30 bg-emerald-400/10' : result.status === 'ALREADY_CHECKED_IN' ? 'border-amber-300/30 bg-amber-400/10' : result.status === 'CHECKED_IN' ? 'border-cyan-300/30 bg-cyan-400/10' : 'border-rose-300/30 bg-rose-400/10'}`}><p className="text-center text-3xl font-black tracking-wide">{resultHeading[result.status] || 'SCAN RESULT'}</p><p className="mt-3 text-center text-sm text-slate-200">{result.message}</p>{result.student_name ? <div className="mt-6 grid gap-3 sm:grid-cols-2"><div><p className="text-xs text-slate-400">Student Name</p><p className="mt-1 text-sm font-semibold">{result.student_name}</p></div><div><p className="text-xs text-slate-400">Registration Number</p><p className="mt-1 text-sm font-semibold">{result.registration_number}</p></div><div><p className="text-xs text-slate-400">Pass Number</p><p className="mt-1 text-sm font-semibold">{result.pass_number}</p></div><div><p className="text-xs text-slate-400">Department</p><p className="mt-1 text-sm font-semibold">{result.department}</p></div><div><p className="text-xs text-slate-400">Academic Year</p><p className="mt-1 text-sm font-semibold">{result.academic_year}</p></div></div> : null}<div className="mt-6 grid gap-3"><Button variant="success" className="min-h-11" onClick={() => void checkIn()} isLoading={checkingIn} disabled={result.status !== 'VALID_PASS'}>CHECK IN</Button><Button variant="secondary" className="min-h-11" onClick={() => void scanAgain()} disabled={checkingIn}>SCAN NEXT PASS</Button><Button variant="ghost" className="min-h-11" onClick={() => navigate('/security/dashboard')} disabled={checkingIn}>Dashboard</Button></div></section>}</div></main>
}
