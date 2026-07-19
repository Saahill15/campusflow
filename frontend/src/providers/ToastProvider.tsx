import React from 'react'
import { Toaster } from 'sonner'

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      {children}
      <Toaster position="top-right" />
    </>
  )
}

export default ToastProvider
