import React from 'react'
import PageContainer from '../components/PageContainer'

export default function AdminDashboard() {
  return (
    <PageContainer title="Admin Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded shadow">Statistics (placeholder)</div>
        <div className="bg-white p-4 rounded shadow">Recent Registrations (placeholder)</div>
      </div>
    </PageContainer>
  )
}
