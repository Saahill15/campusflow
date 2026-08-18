import React from 'react'
import { motion } from 'framer-motion'
import { ChevronLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import PragyarambhRegistrationCard from '../../components/pragyarambh/PragyarambhRegistrationCard'

export default function RegisterPage() {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen bg-[#1A120D]">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-radial-gradient(circle at top-right, [#CC9E4C]/4, transparent 50%)" />

      {/* Header */}
      <header className="relative z-50 px-4 py-6 md:px-8">
        <div className="mx-auto max-w-7xl">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-xs font-black tracking-[0.15em] text-[#E0D0B6] hover:text-[#CC9E4C] transition uppercase"
          >
            <ChevronLeft size={16} />
            Back
          </button>
        </div>
      </header>

      {/* Main Content - Two Column Layout */}
      <main className="relative z-10 min-h-screen flex items-center">
        <div className="mx-auto w-full max-w-7xl px-4 py-12 md:px-8">
          <div className="grid gap-12 md:gap-20 lg:grid-cols-[1fr_1.2fr] items-start lg:items-center">
            {/* Left Column - Info */}
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-10 text-[#E0D0B6]"
            >
              <div className="space-y-4">
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">Registration</p>
                  <h1 className="text-5xl sm:text-6xl font-black leading-[1.1] tracking-[-0.02em]">
                    Secure Your <br /> Spot
                  </h1>
                </div>
                <p className="text-base text-[#D4C5AC] leading-relaxed font-light">
                  Complete the form to join Pragyarambh 3.0. Every detail matters for verification.
                </p>
              </div>

              {/* Key Info */}
              <div className="space-y-6 pt-8 border-t border-[#CC9E4C]/20">
                <div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[#8B9EA5] font-semibold mb-3">What You Get</p>
                  <ul className="space-y-3 text-sm">
                    <li className="flex items-start gap-3">
                      <span className="text-[#CC9E4C] font-bold mt-1">✓</span>
                      <span>Your unique registration number</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-[#CC9E4C] font-bold mt-1">✓</span>
                      <span>Digital pass in your inbox</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-[#CC9E4C] font-bold mt-1">✓</span>
                      <span>Event access and updates</span>
                    </li>
                  </ul>
                </div>

              </div>
            </motion.div>

            {/* Right Column - Form */}
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="w-full"
            >
              <PragyarambhRegistrationCard />
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  )
}
