import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PublicLayout from '../layouts/PublicLayout'
import StudentLayout from '../layouts/StudentLayout'
import AdminLayout from '../layouts/AdminLayout'
import Landing from '../pages/Landing'
import PragyarambhLanding from '../pages/pragyarambh/PragyarambhLanding'
import Login from '../pages/Login'
import StudentDashboard from '../pages/StudentDashboard'
import AdminDashboard from '../pages/AdminDashboard'
import CommitteeDashboard from '../pages/CommitteeDashboard'
import Scanner from '../pages/Scanner'
import NotFound from '../pages/NotFound'
import Unauthorized from '../pages/Unauthorized'
import PublicRoute from './PublicRoute'
import RoleRoute from './RoleRoute'

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/pragyarambh" element={<PragyarambhLanding />} />

        <Route path="/" element={<PublicLayout />}>
          <Route index element={<Landing />} />
          <Route path="login" element={<PublicRoute><Login /></PublicRoute>} />
        </Route>

        <Route path="/student" element={<RoleRoute roles={["student"]}><StudentLayout /></RoleRoute>}>
          <Route path="dashboard" element={<StudentDashboard />} />
        </Route>

        <Route path="/admin" element={<RoleRoute roles={["admin"]}><AdminLayout /></RoleRoute>}>
          <Route path="dashboard" element={<AdminDashboard />} />
        </Route>

        <Route path="/committee" element={<RoleRoute roles={["committee"]}><AdminLayout /></RoleRoute>}>
          <Route path="dashboard" element={<CommitteeDashboard />} />
        </Route>

        <Route path="/scanner" element={<RoleRoute roles={["committee","scanner"]}><Scanner /></RoleRoute>} />

        <Route path="/unauthorized" element={<Unauthorized />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

