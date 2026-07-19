import React from 'react'
import { cn } from '../../../lib/cn'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  helper?: string
  error?: string | boolean
  icon?: React.ReactNode
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, helper, error, icon, ...props }, ref) => {
  return (
    <div>
      <div className={cn('relative flex items-center', className)}>
        {icon ? <span className="absolute left-3 text-muted-foreground">{icon}</span> : null}
        <input
          ref={ref}
          className={cn(
            'w-full rounded-md border px-3 py-2 bg-transparent text-sm focus:ring-0',
            icon ? 'pl-10' : 'pl-3',
            error ? 'border-red-500' : 'border-neutral-200'
          )}
          aria-invalid={!!error}
          {...props}
        />
      </div>
      {helper ? <p className="mt-1 text-xs text-muted-foreground">{helper}</p> : null}
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
    </div>
  )
})
Input.displayName = 'Input'

export default Input
