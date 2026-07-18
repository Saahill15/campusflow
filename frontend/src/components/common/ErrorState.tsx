import React from 'react'

export const ErrorState: React.FC<{ title?: string; description?: string }> = ({ title = 'Something went wrong', description }) => (
  <div className="flex flex-col items-center justify-center py-12">
    <div className="text-center">
      <h3 className="text-lg font-semibold text-red-600">{title}</h3>
      {description ? <p className="mt-2 text-sm text-muted-foreground">{description}</p> : null}
    </div>
  </div>
)

export default ErrorState
