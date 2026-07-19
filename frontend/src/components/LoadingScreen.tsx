import React from 'react'

export default function LoadingScreen() {
  return (
    <div className="min-h-[200px] flex items-center justify-center">
      <div className="animate-pulse text-slate-400">Loading…</div>
    </div>
  )
}
