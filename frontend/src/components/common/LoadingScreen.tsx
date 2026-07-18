import React from 'react'
import { Spinner } from '../ui/spinner/Spinner'

export const LoadingScreen: React.FC = () => (
  <div className="fixed inset-0 flex items-center justify-center bg-white/60 dark:bg-black/60">
    <Spinner className="h-10 w-10 text-primary-600" />
  </div>
)

export default LoadingScreen
