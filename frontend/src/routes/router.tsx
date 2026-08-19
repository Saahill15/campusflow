import React from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import AdminShell from '../components/admin/AdminShell'
import PragyarambhLanding from '../pages/pragyarambh/PragyarambhLanding'
import RegisterPage from '../pages/pragyarambh/RegisterPage'
import CheckStatusPage from '../pages/pragyarambh/CheckStatusPage'
import AdminLoginPage from '../pages/admin/AdminLoginPage'
import AdminHomePage from '../pages/admin/AdminHomePage'
import AdminRegistrationsPage from '../pages/admin/AdminRegistrationsPage'
import AdminRegistrationDetailPage from '../pages/admin/AdminRegistrationDetailPage'
import AdminSettingsPage from '../pages/admin/AdminSettingsPage'
import AdminSecurityVolunteersPage from '../pages/admin/AdminSecurityVolunteersPage'
import AdminCheckinOverviewPage from '../pages/admin/AdminCheckinOverviewPage'
import SecurityLoginPage from '../pages/security/SecurityLoginPage'
import SecurityDashboardPage from '../pages/security/SecurityDashboardPage'
import SecurityScannerPage from '../pages/security/SecurityScannerPage'

function AdminGuard({ children }: { children: React.ReactNode }) {
  const { isInitialized, user } = useAuth()

  if (!isInitialized) return <div className="min-h-screen bg-slate-950 text-white p-6">Loading...</div>
  if (!user || user.role !== 'admin') return <Navigate to="/admin/login" replace />
  return <>{children}</>
}

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PragyarambhLanding />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/check-status" element={<CheckStatusPage />} />
        <Route path="/security/login" element={<SecurityLoginPage />} />
        <Route path="/security/dashboard" element={<SecurityDashboardPage />} />
        <Route path="/security/scanner" element={<SecurityScannerPage />} />
        <Route path="/admin/dashboard" element={<Navigate to="/admin" replace />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route
          path="/admin"
          element={(
            <AdminGuard>
              <AdminShell />
            </AdminGuard>
          )}
        >
          <Route index element={<AdminHomePage />} />
          <Route path="registrations" element={<AdminRegistrationsPage />} />
          <Route path="registrations/:id" element={<AdminRegistrationDetailPage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
          <Route path="security-volunteers" element={<AdminSecurityVolunteersPage />} />
          <Route path="check-in" element={<AdminCheckinOverviewPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

