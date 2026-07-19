import React from 'react'

export default function ErrorScreen({ message }: { message?: string }) {
  return (
    <div className="min-h-[200px] flex items-center justify-center">
      <div className="text-red-500">{message || 'An error occurred'}</div>
    </div>
  )
}
