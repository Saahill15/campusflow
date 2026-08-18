import React from 'react'
import { motion } from 'framer-motion'
import { ChevronLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PragyarambhRegistrationCard from '../../components/pragyarambh/PragyarambhRegistrationCard'

export default function RegisterPage() {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-b from-[#442C1B] via-[#6B2717] to-[#442C1B] text-[#E0D0B6]">
      {/* Subtle background effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(204,158,76,0.08),_transparent_40%),radial-gradient(circle_at_bottom_left,_rgba(139,158,165,0.06),_transparent_50%)]" />

      {/* Header */}
      <header className="relative z-20 border-b border-[#CC9E4C]/20 bg-[#6B2717]/60 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-8 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm font-semibold text-[#E0D0B6] transition hover:text-[#CC9E4C]"
          >
            <ChevronLeft size={18} />
            Back to Home
          </button>
          <div className="text-sm font-black tracking-[0.2em] text-[#E0D0B6]">PRAGYARAMBH 3.0</div>
          <div className="w-20" />
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 mx-auto max-w-4xl px-4 py-12 sm:px-8 lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C]/80">Registration</p>
          <h1 className="mt-4 text-4xl sm:text-5xl font-black tracking-tight text-[#E0D0B6]">
            Secure Your Spot
          </h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-[#D4C5AC]">
            Complete your registration to join Pragyarambh 3.0. All fields are required for verification.
          </p>
        </motion.div>

        <PragyarambhRegistrationCard />
      </main>

      {/* Footer Info */}
      <footer className="relative z-10 border-t border-[#CC9E4C]/20 bg-[#6B2717]/40 backdrop-blur mt-12">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-8 text-center text-sm text-[#8B9EA5]">
          <p>Need help? Check the information section on the home page or contact the Pragyarambh team.</p>
        </div>
      </footer>
    </div>
  )
}
