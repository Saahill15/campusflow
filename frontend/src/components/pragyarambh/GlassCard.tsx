import React from 'react'

type GlassCardProps = {
  children: React.ReactNode
  className?: string
}

export default function GlassCard({ children, className = '' }: GlassCardProps) {
  return (
    <div className={`rounded-[1.75rem] border border-white/10 bg-white/5 p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.03),0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl ${className}`.trim()}>
      {children}
    </div>
  )
}
