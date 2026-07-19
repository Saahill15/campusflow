import React from 'react'

export default function PageContainer({ children, title }: { children: React.ReactNode, title?: string }) {
  return (
    <div className="max-w-7xl mx-auto">
      {title && <h1 className="text-2xl font-semibold mb-4">{title}</h1>}
      <div className="space-y-4">{children}</div>
    </div>
  )
}
