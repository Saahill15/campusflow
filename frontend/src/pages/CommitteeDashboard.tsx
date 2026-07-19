import React from 'react'
import PageContainer from '../components/PageContainer'

export default function CommitteeDashboard() {
  return (
    <PageContainer title="Committee Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">Pending Approvals</div>
        <div className="bg-white p-4 rounded shadow">Live Entries</div>
        <div className="bg-white p-4 rounded shadow">Gate Management</div>
      </div>
    </PageContainer>
  )
}
