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
    <div className="min-h-screen bg-[#2A1810] text-[#E0D0B6]">
      {/* Navigation */}
      <header className="fixed inset-x-0 top-0 z-50 px-4 py-6 md:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <button onClick={() => navigate('/')} className="group">
            <div className="flex items-center gap-3">
              <div className="text-xs font-black tracking-[0.25em] text-[#E0D0B6] group-hover:text-[#CC9E4C] transition duration-300">PRAGYARAMBH</div>
              <div className="text-[11px] text-[#CC9E4C] font-bold tracking-widest">3.0</div>
            </div>
          </button>
          <nav className="hidden items-center gap-12 text-xs text-[#E0D0B6] md:flex uppercase tracking-[0.15em] font-medium">
            <a href="#about" className="transition duration-300 hover:text-[#CC9E4C]">About</a>
            <a href="#experience" className="transition duration-300 hover:text-[#CC9E4C]">Experience</a>
            <a href="#details" className="transition duration-300 hover:text-[#CC9E4C]">Details</a>
          </nav>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/register')}
              className="hidden md:block px-6 py-2 text-xs font-black tracking-[0.1em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase"
            >
              Register
            </button>
            <button
              className="md:hidden text-[#E0D0B6] hover:text-[#CC9E4C] transition"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mx-auto mt-6 max-w-7xl bg-[#442C1B]/95 backdrop-blur p-6 md:hidden"
          >
            <nav className="flex flex-col gap-6 text-xs text-[#E0D0B6] uppercase tracking-[0.15em] font-medium">
              <a href="#about" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                About
              </a>
              <a href="#experience" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                Experience
              </a>
              <a href="#details" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                Details
              </a>
              <button
                onClick={() => {
                  navigate('/register')
                  setMenuOpen(false)
                }}
                className="w-full mt-2 px-6 py-3 text-xs font-black tracking-[0.1em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition uppercase"
              >
                Register Now
              </button>
            </nav>
          </motion.div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen overflow-hidden">
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
          {/* Elegant dark overlay with subtle color */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#2A1810]/60 via-[#2A1810]/70 to-[#2A1810]/85" />
          <div className="absolute inset-0 bg-radial-gradient(circle at top-right, [#CC9E4C]/5, transparent 50%)" />
          {videoError && <div className="absolute inset-0 bg-[#2A1810]" />}
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 py-20 text-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="space-y-8 max-w-5xl"
          >
            {/* Eyebrow text */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black"
            >
              The Premium Freshers' Experience
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, delay: 0.2 }}
              className="text-6xl sm:text-7xl md:text-8xl font-black leading-[0.9] tracking-[-0.025em] text-[#E0D0B6]"
            >
              PRAGYARAMBH <br />
              <span className="text-[#CC9E4C]">3.0</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-base sm:text-lg text-[#D4C5AC] max-w-2xl mx-auto leading-relaxed font-light"
            >
              Experience cinematic energy, premium vibes, and unforgettable moments. Your campus celebration, reimagined.
            </motion.p>

            {/* CTA Section */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-8"
            >
              <button
                onClick={() => navigate('/register')}
                className="px-12 py-4 text-xs font-black tracking-[0.15em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase shadow-2xl shadow-[#CC9E4C]/20"
              >
                Register Now
              </button>
              <button
                onClick={() => {
                  const elem = document.getElementById('about')
                  elem?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="px-12 py-4 text-xs font-black tracking-[0.15em] text-[#E0D0B6] border border-[#CC9E4C]/50 hover:border-[#CC9E4C] hover:text-[#CC9E4C] transition duration-300 uppercase"
              >
                Discover More
              </button>
            </motion.div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
            className="absolute bottom-12 flex flex-col items-center gap-3"
          >
            <div className="h-px w-6 bg-gradient-to-r from-transparent via-[#CC9E4C] to-transparent" />
            <ChevronDown size={18} className="text-[#CC9E4C]" />
          </motion.div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="relative bg-[#2A1810] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-12 md:grid-cols-2 md:gap-16 items-center">
            {/* Left: Headline */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <div className="space-y-3">
                <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black">About</p>
                <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
                  Your College Moment,
                  <br />
                  Elevated.
                </h2>
              </div>
              <p className="text-base text-[#D4C5AC] leading-relaxed font-light max-w-lg">
                Pragyarambh isn't just another event. It's a carefully curated night designed to celebrate your arrival at campus. From immersive visuals to premium experiences, every detail is crafted to make you feel the energy, the community, and the magic.
              </p>
            </motion.div>

            {/* Right: Stats */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="grid grid-cols-2 gap-8"
            >
              {[
                { number: '4+', label: 'Hours of Premium Entertainment' },
                { number: '1000+', label: 'Freshers Celebrating Together' },
                { number: '100%', label: 'Unforgettable Moments' },
                { number: '1', label: 'Night You\'ll Never Forget' },
              ].map((item, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="text-3xl sm:text-4xl font-black text-[#CC9E4C]">{item.number}</div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[#8B9EA5] font-semibold">{item.label}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Experience Section */}
      <section id="experience" className="relative bg-[#442C1B] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 md:mb-24"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black mb-3">The Experience</p>
            <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
              Four Dimensions of Celebration
            </h2>
          </motion.div>

          {/* Experience Grid - Editorial Layout */}
          <div className="grid gap-8 md:gap-12">
            {/* Large Feature */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="group md:grid md:grid-cols-3 gap-8 items-center"
            >
              <div className="md:col-span-2 space-y-4">
                <h3 className="text-2xl sm:text-3xl font-bold text-[#E0D0B6]">Live Music & Cinematic Visuals</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  High-energy performances paired with projection mapping and cinematic lighting. A fully immersive audio-visual experience designed to set the mood for the entire night.
                </p>
              </div>
              <div className="h-48 md:h-full bg-gradient-to-br from-[#6B2717]/40 to-[#CC9E4C]/10 border border-[#CC9E4C]/20 flex items-center justify-center">
                <span className="text-[#CC9E4C]/40 text-4xl font-black">♪</span>
              </div>
            </motion.div>

            {/* Two Column Grid */}
            <div className="grid md:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.1 }}
                className="space-y-4"
              >
                <h3 className="text-xl sm:text-2xl font-bold text-[#E0D0B6]">Premium Food & Vibes</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  Curated food stalls, chill zones, and spaces designed for connection. Every corner is crafted to let you relax, celebrate, and build lasting memories.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.15 }}
                className="space-y-4"
              >
                <h3 className="text-xl sm:text-2xl font-bold text-[#E0D0B6]">Capture Your Moment</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  Instagrammable setups and professional photography. Every moment is documented so your memories last forever.
                </p>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Details Section */}
      <section id="details" className="relative bg-[#2A1810] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 md:mb-24"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black mb-3">Details</p>
            <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
              Registration & Entry Info
            </h2>
          </motion.div>

          <div className="grid gap-12 md:grid-cols-2">
            {/* Registration */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <h3 className="text-xl font-bold text-[#E0D0B6] uppercase tracking-[0.05em]">Registration Tiers</h3>
              <div className="space-y-6">
                {[
                  { year: 'First Year', fee: 'Free', desc: 'All freshers welcome' },
                  { year: 'Second Year', fee: '₹250', desc: 'UPI or Cash payment' },
                  { year: 'Third Year', fee: '₹250', desc: 'UPI or Cash payment' },
                ].map((tier, idx) => (
                  <div key={idx} className="pb-6 border-b border-[#CC9E4C]/20 last:border-b-0">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-lg font-semibold text-[#E0D0B6]">{tier.year}</p>
                      <p className="text-2xl font-black text-[#CC9E4C]">{tier.fee}</p>
                    </div>
                    <p className="text-sm text-[#D4C5AC]">{tier.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Next Steps */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <h3 className="text-xl font-bold text-[#E0D0B6] uppercase tracking-[0.05em]">Get Your Pass</h3>
              <ol className="space-y-5">
                {[
                  'Fill your registration details accurately',
                  'Complete payment if required (UPI QR provided)',
                  'Submit and wait for admin approval',
                  'Receive your digital pass via email',
                ].map((step, idx) => (
                  <li key={idx} className="flex gap-4">
                    <span className="text-xl font-black text-[#CC9E4C] flex-shrink-0">{String(idx + 1).padStart(2, '0')}</span>
                    <span className="text-[#D4C5AC] font-light leading-relaxed">{step}</span>
                  </li>
                ))}
              </ol>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative bg-[#442C1B] px-4 py-20 sm:px-8 md:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-radial-gradient(circle at bottom-left, [#CC9E4C]/3, transparent 60%)" />
        <div className="mx-auto max-w-4xl relative z-10 text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="space-y-6"
          >
            <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
              Ready to join the celebration?
            </h2>
            <p className="text-base text-[#D4C5AC] font-light max-w-2xl mx-auto leading-relaxed">
              Secure your spot now. This night will define your college memories. Limited entries, unlimited vibes.
            </p>
          </motion.div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/register')}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="inline-block px-16 py-5 text-sm font-black tracking-[0.15em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase shadow-2xl shadow-[#CC9E4C]/30"
          >
            Secure Your Pass
          </motion.button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1F140A] border-t border-[#CC9E4C]/20 px-4 py-16 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 md:grid-cols-3 mb-12">
            <div className="space-y-2">
              <p className="text-xs font-black tracking-[0.3em] text-[#E0D0B6] uppercase">Pragyarambh</p>
              <p className="text-xs text-[#8B9EA5] font-light">The Premium Freshers' Experience</p>
            </div>
            <div className="space-y-3 text-xs text-[#8B9EA5]">
              <p className="font-semibold text-[#E0D0B6] uppercase tracking-[0.08em]">Quick Links</p>
              <ul className="space-y-1 font-light">
                <li><a href="#about" className="hover:text-[#CC9E4C] transition">About</a></li>
                <li><a href="#experience" className="hover:text-[#CC9E4C] transition">Experience</a></li>
                <li><a href="#details" className="hover:text-[#CC9E4C] transition">Details</a></li>
              </ul>
            </div>
            <div className="space-y-3 text-xs text-[#8B9EA5]">
              <p className="font-semibold text-[#E0D0B6] uppercase tracking-[0.08em]">Support</p>
              <ul className="space-y-1 font-light">
                <li><a href="/register" className="hover:text-[#CC9E4C] transition">Register</a></li>
                <li><a href="#" className="hover:text-[#CC9E4C] transition">FAQs</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-[#CC9E4C]/10 pt-8 text-center text-xs text-[#8B9EA5] font-light">
            <p>© 2026 Pragyarambh 3.0. Curated for the Premium Experience.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
