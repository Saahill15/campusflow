import React from 'react'

export const PageContainer: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => (
  <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${className ?? ''}`} {...props}>
    {children}
  </div>
)

export default PageContainer
