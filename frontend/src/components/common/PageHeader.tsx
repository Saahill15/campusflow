import React from 'react'

export const PageHeader: React.FC<{ title?: React.ReactNode; subtitle?: React.ReactNode }> = ({ title, subtitle }) => (
  <header className="mb-6">
    {title ? <h1 className="text-2xl font-semibold">{title}</h1> : null}
    {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
  </header>
)

export default PageHeader
