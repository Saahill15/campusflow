import React from 'react'
import { cn } from '../../../lib/cn'
import { Loader2 } from 'lucide-react'

type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success' | 'icon'
type Size = 'sm' | 'default' | 'lg' | 'icon'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  const { className, children, variant = 'primary', size = 'default', isLoading, disabled, ...rest } = props

  const base = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'
  const variantMap: Record<Variant, string> = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600',
    secondary: 'bg-secondary-600 text-white hover:bg-secondary-700',
    outline: 'border border-neutral-200 bg-transparent dark:border-neutral-700',
    ghost: 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800',
    destructive: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-green-600 text-white hover:bg-green-700',
    icon: 'p-2 bg-transparent hover:bg-neutral-100 rounded-full dark:hover:bg-neutral-800'
  }
  const sizeMap: Record<Size, string> = {
    sm: 'h-8 px-3 text-sm',
    default: 'h-10 px-4 text-sm',
    lg: 'h-12 px-6 text-base',
    icon: 'h-10 w-10 p-0'
  }

  return (
    <button
      ref={ref}
      className={cn(base, variantMap[variant], sizeMap[size], className)}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden /> : null}
      {children}
    </button>
  )
})
Button.displayName = 'Button'

export default Button
