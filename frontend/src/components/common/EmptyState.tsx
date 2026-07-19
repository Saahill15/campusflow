import React from 'react'

export const EmptyState: React.FC<{ title?: string; description?: string }> = ({ title = 'Nothing here', description }) => (
  <div className="flex flex-col items-center justify-center py-12">
    <div className="text-center">
      <h3 className="text-lg font-semibold">{title}</h3>
      {description ? <p className="mt-2 text-sm text-muted-foreground">{description}</p> : null}
    </div>
  </div>
)

export default EmptyState
