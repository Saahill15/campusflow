import React from 'react'
import PageContainer from '../components/PageContainer'

export default function Unauthorized() {
  return (
    <PageContainer>
      <div className="text-center py-20">
        <h2 className="text-2xl font-semibold">Unauthorized</h2>
        <p className="mt-2 text-slate-600">You do not have access to this page.</p>
      </div>
    </PageContainer>
  )
}
