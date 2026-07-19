import React from 'react'

export const Heading: React.FC<React.HTMLAttributes<HTMLHeadingElement> & { level?: 1 | 2 | 3 | 4 }> = ({ level = 1, children, className, ...props }) => {
  if (level === 1) return <h1 className={`text-2xl font-semibold ${className ?? ''}`} {...props}>{children}</h1>
  if (level === 2) return <h2 className={`text-xl font-semibold ${className ?? ''}`} {...props}>{children}</h2>
  if (level === 3) return <h3 className={`text-lg font-semibold ${className ?? ''}`} {...props}>{children}</h3>
  return <h4 className={`text-base font-semibold ${className ?? ''}`} {...props}>{children}</h4>
}

export default Heading
