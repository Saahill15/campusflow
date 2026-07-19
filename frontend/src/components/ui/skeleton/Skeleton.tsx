import React from 'react'

export const Skeleton = ({ className = 'h-4 w-full rounded bg-neutral-200/50', ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={`animate-pulse ${className}`} aria-hidden {...props} />
)

export default Skeleton
