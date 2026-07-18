import React from 'react'

export const Text: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ children, className, ...props }) => (
  <p className={`${className ?? ''}`} {...props}>{children}</p>
)

export default Text
