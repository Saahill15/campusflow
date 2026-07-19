import React from 'react'
import { cn } from '../../../lib/cn'

export const Card = ({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('rounded-lg border bg-card text-card-foreground', className)} {...props}>
    {children}
  </div>
)

export const CardHeader = ({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-4 border-b', className)} {...props}>{children}</div>
)

export const CardTitle = ({ children, className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn('text-sm font-semibold', className)} {...props}>{children}</h3>
)

export const CardDescription = ({ children, className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={cn('text-sm text-muted-foreground', className)} {...props}>{children}</p>
)

export const CardContent = ({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-4', className)} {...props}>{children}</div>
)

export const CardFooter = ({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('p-4 border-t', className)} {...props}>{children}</div>
)

export default Card
