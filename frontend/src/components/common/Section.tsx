import React from 'react'

export const Section: React.FC<React.HTMLAttributes<HTMLElement>> = ({ children, className, ...props }) => (
  <section className={`py-6 ${className ?? ''}`} {...props}>{children}</section>
)

export default Section
