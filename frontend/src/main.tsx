import React from 'react'
import { createRoot } from 'react-dom/client'
import AppProviders from './app/AppProviders'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppProviders />
  </React.StrictMode>
)

