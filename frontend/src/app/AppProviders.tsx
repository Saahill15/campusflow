import React from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '../lib/queryClient'
import ThemeProvider from '../providers/ThemeProvider'
import ToastProvider from '../providers/ToastProvider'
import { AuthProvider } from '../context/AuthContext'
import Router from '../routes/router'

const AppProviders: React.FC = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <Router />
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  </ThemeProvider>
)

export default AppProviders
