import React from 'react'
import Sidebar from './Sidebar'
import TopNav from './TopNav'

export default function AppShell({ children }: { children?: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-gray-50 dark:bg-slate-900">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopNav />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
