import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import StudentDashboard from './pages/StudentDashboard'
import CommitteeDashboard from './pages/CommitteeDashboard'
import AdminDashboard from './pages/AdminDashboard'
import Scanner from './pages/Scanner'
import NotFound from './pages/NotFound'
import Unauthorized from './pages/Unauthorized'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="login" element={<Login />} />

        <Route
          path="student/*"
          element={<ProtectedRoute allowedRoles={["student"]}><StudentDashboard /></ProtectedRoute>}
        />

        <Route
          path="committee/*"
          element={<ProtectedRoute allowedRoles={["committee"]}><CommitteeDashboard /></ProtectedRoute>}
        />

        <Route
          path="admin/*"
          element={<ProtectedRoute allowedRoles={["admin"]}><AdminDashboard /></ProtectedRoute>}
        />

        <Route path="scanner" element={<ProtectedRoute allowedRoles={["committee","scanner"]}><Scanner /></ProtectedRoute>} />

        <Route path="unauthorized" element={<Unauthorized />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

