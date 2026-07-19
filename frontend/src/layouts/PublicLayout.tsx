import React from 'react'
import { Outlet } from 'react-router-dom'
import PageContainer from '../components/PageContainer'

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <header className="border-b border-gray-200 bg-white dark:bg-slate-800 p-4">CampusFlow</header>
      <main className="p-6">
        <PageContainer>
          <Outlet />
        </PageContainer>
      </main>
      <footer className="p-6 text-sm text-slate-500">© Pragyarambh</footer>
    </div>
  )
}

