import React from 'react'
import { cn } from '../../../lib/cn'

type Variant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'outline'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: Variant
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(({ className, variant = 'primary', children, ...props }, ref) => {
  const map: Record<Variant, string> = {
    primary: 'bg-primary-600 text-white',
    secondary: 'bg-secondary-600 text-white',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    outline: 'border border-neutral-200 bg-transparent'
  }
  return (
    <span ref={ref} className={cn('inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', map[variant], className)} {...props}>
      {children}
    </span>
  )
})
Badge.displayName = 'Badge'

export default Badge
