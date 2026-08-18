import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, Menu, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function PragyarambhLanding() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [videoError, setVideoError] = useState(false)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const playVideo = async () => {
      try {
        video.muted = true
        await video.play()
      } catch {
        // autoplay may be blocked; ignore
      }
    }

    playVideo()
  }, [])

  return (
    <div className="min-h-screen bg-[#442C1B] text-[#E0D0B6]">
      {/* Navigation */}
      <header className="fixed inset-x-0 top-0 z-50 px-4 py-4 md:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between rounded-full border border-[#CC9E4C]/30 bg-[#6B2717]/60 px-6 py-3 backdrop-blur-xl">
          <div className="flex items-center gap-2">
            <div className="text-sm font-black tracking-[0.2em] text-[#E0D0B6]">PRAGYARAMBH</div>
            <div className="text-xs text-[#8B9EA5]">3.0</div>
          </div>
          <nav className="hidden items-center gap-8 text-sm text-[#E0D0B6] md:flex">
            <a href="#experience" className="transition hover:text-[#CC9E4C]">Experience</a>
            <a href="#register" className="transition hover:text-[#CC9E4C]">Register</a>
          </nav>
          <button
            onClick={() => navigate('/register')}
            className="hidden rounded-full bg-[#CC9E4C] px-4 py-2 text-sm font-semibold text-[#442C1B] backdrop-blur transition hover:bg-[#6B2717] hover:text-[#E0D0B6] md:block"
          >
            Register
          </button>
          <button
            className="md:hidden rounded-lg border border-[#CC9E4C]/30 p-2 text-[#E0D0B6] transition hover:text-[#CC9E4C]"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mx-auto mt-3 max-w-7xl rounded-2xl border border-[#CC9E4C]/30 bg-[#6B2717]/80 p-4 backdrop-blur-xl md:hidden"
          >
            <nav className="flex flex-col gap-4 text-sm text-[#E0D0B6]">
              <a href="#experience" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                Experience
              </a>
              <a href="#register" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                Register
              </a>
              <button
                onClick={() => {
                  navigate('/register')
                  setMenuOpen(false)
                }}
                className="w-full rounded-full bg-[#CC9E4C] px-4 py-2 text-sm font-semibold text-[#442C1B] backdrop-blur transition hover:bg-[#6B2717] hover:text-[#E0D0B6]"
              >
                Register Now
              </button>
            </nav>
          </motion.div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen overflow-hidden pt-24">
        <div className="absolute inset-0">
          <video
            ref={videoRef}
            className="absolute inset-0 h-full w-full object-cover"
            autoPlay
            loop
            playsInline
            muted
            preload="auto"
            onError={() => setVideoError(true)}
          >
            <source src="/video.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-b from-[#6B2717]/50 via-[#442C1B]/60 to-[#442C1B]/80" />
          {videoError && <div className="absolute inset-0 bg-gradient-to-b from-[#6B2717] via-[#442C1B] to-[#442C1B]" />}
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 py-12 text-center sm:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-6 max-w-4xl"
          >
            <div className="inline-flex items-center justify-center gap-3 rounded-full border border-[#CC9E4C]/40 bg-[#CC9E4C]/10 px-4 py-2 backdrop-blur text-xs uppercase tracking-[0.2em] text-[#E0D0B6]">
              <span className="h-2 w-2 rounded-full bg-[#CC9E4C] animate-pulse" />
              Happening Now
            </div>

            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-[-0.02em] leading-[0.95] text-[#E0D0B6]">
              PRAGYARAMBH
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#E0D0B6] via-[#CC9E4C] to-[#6B2717]">
                3.0
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-[#D4C5AC] max-w-2xl mx-auto leading-relaxed">
              Experience a night of cinematic energy, premium vibes, and unforgettable moments. Your campus freshers' celebration, reimagined.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/register')}
                className="rounded-full bg-[#CC9E4C] px-8 py-3 font-semibold text-[#442C1B] shadow-lg shadow-[#CC9E4C]/40 transition hover:shadow-xl hover:shadow-[#CC9E4C]/60 hover:bg-[#6B2717] hover:text-[#E0D0B6]"
              >
                Register Now
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  const elem = document.getElementById('experience')
                  elem?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="rounded-full border border-[#CC9E4C]/50 bg-[#CC9E4C]/5 px-8 py-3 font-semibold text-[#E0D0B6] backdrop-blur transition hover:bg-[#CC9E4C]/15 hover:text-[#CC9E4C]"
              >
                Explore Experience
              </motion.button>
            </div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="absolute bottom-8 flex flex-col items-center gap-2"
          >
            <span className="text-sm text-[#8B9EA5]">Scroll to discover</span>
            <ChevronDown size={20} className="text-[#8B9EA5]" />
          </motion.div>
        </div>
      </section>

      {/* Experience Section */}
      <section id="experience" className="relative z-10 bg-[#442C1B] px-4 py-20 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C]/80">The Event</p>
            <h2 className="mt-4 text-4xl sm:text-5xl font-black tracking-tight text-[#E0D0B6]">
              Premium • Cinematic • Unforgettable
            </h2>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                title: 'Live Music & DJ',
                description: 'High-energy performances and premium sound that sets the mood for the entire night.',
              },
              {
                title: 'Immersive Visuals',
                description: 'Cinematic lighting, projection mapping, and visual elements designed to captivate.',
              },
              {
                title: 'Curated Experience',
                description: 'Every detail is crafted for freshers to feel welcome, connected, and part of something special.',
              },
              {
                title: 'Food & Vibes',
                description: 'Premium food stalls, chill zones, and spaces to connect with your campus community.',
              },
              {
                title: 'Photo Moments',
                description: 'Instagrammable setups and professional coverage to capture your memories.',
              },
              {
                title: 'Zero Registration Fee',
                description: 'Entry is free for all First Year students. Paid tiers for Second and Third Year.',
              },
            ].map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="group rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/30 p-6 backdrop-blur transition hover:bg-[#6B2717]/50 hover:border-[#CC9E4C]/40"
              >
                <h3 className="text-lg font-semibold text-[#E0D0B6] group-hover:text-[#CC9E4C] transition">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-[#D4C5AC]">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Info Section */}
      <section className="relative z-10 bg-gradient-to-b from-[#442C1B] to-[#6B2717] px-4 py-20 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C]/80">Important</p>
            <h2 className="mt-4 text-4xl sm:text-5xl font-black tracking-tight text-[#E0D0B6]">
              What You Need to Know
            </h2>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/40 p-8 backdrop-blur"
            >
              <h3 className="text-xl font-semibold text-[#E0D0B6] mb-4">Registration Details</h3>
              <ul className="space-y-3 text-[#D4C5AC] text-sm">
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold mt-0.5">•</span>
                  <span><strong className="text-[#E0D0B6]">First Year:</strong> Free registration for all freshers</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold mt-0.5">•</span>
                  <span><strong className="text-[#E0D0B6]">Second Year:</strong> ₹250 registration fee (UPI or Cash)</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold mt-0.5">•</span>
                  <span><strong className="text-[#E0D0B6]">Third Year:</strong> ₹250 registration fee (UPI or Cash)</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold mt-0.5">•</span>
                  <span>Payment proof required only for UPI mode</span>
                </li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="rounded-2xl border border-[#CC9E4C]/20 bg-[#6B2717]/40 p-8 backdrop-blur"
            >
              <h3 className="text-xl font-semibold text-[#E0D0B6] mb-4">Next Steps</h3>
              <ol className="space-y-3 text-[#D4C5AC] text-sm">
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold min-w-fit">1.</span>
                  <span>Complete your registration form with accurate details</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold min-w-fit">2.</span>
                  <span>If paying by UPI, scan the QR code and upload your payment proof</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold min-w-fit">3.</span>
                  <span>Submit your registration and await confirmation</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#CC9E4C] font-bold min-w-fit">4.</span>
                  <span>Receive your pass via email and enjoy the event</span>
                </li>
              </ol>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Register CTA */}
      <section id="register" className="relative z-10 bg-[#442C1B] px-4 py-20 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-3xl border border-[#CC9E4C]/30 bg-gradient-to-br from-[#6B2717]/40 to-[#6B2717]/20 p-12 text-center backdrop-blur"
          >
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-[#E0D0B6] mb-4">
              Ready to join?
            </h2>
            <p className="text-lg text-[#D4C5AC] mb-8 max-w-2xl mx-auto">
              Secure your spot now and be part of a night that will define your college memories.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/register')}
              className="rounded-full bg-[#CC9E4C] px-10 py-4 text-lg font-semibold text-[#442C1B] shadow-lg shadow-[#CC9E4C]/40 transition hover:shadow-xl hover:shadow-[#CC9E4C]/60 hover:bg-[#6B2717] hover:text-[#E0D0B6]"
            >
              Register Now
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#CC9E4C]/20 bg-[#442C1B] px-4 py-12 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col items-center justify-between gap-6 text-center md:flex-row md:text-left">
            <div>
              <p className="text-sm font-semibold text-[#E0D0B6]">PRAGYARAMBH 3.0</p>
              <p className="mt-1 text-xs text-[#8B9EA5]">The Premium Freshers' Experience</p>
            </div>
            <p className="text-xs text-[#8B9EA5]">
              © 2026 Pragyarambh. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
