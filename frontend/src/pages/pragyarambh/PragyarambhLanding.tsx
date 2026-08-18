import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, Menu, Volume2, VolumeX, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function PragyarambhLanding() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [videoError, setVideoError] = useState(false)
  const [isMuted, setIsMuted] = useState(true)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    document.title = 'Pragyarambh 3.0'

    return () => {
      document.title = 'Pragyarambh 3.0'
    }
  }, [])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    video.muted = isMuted
    video.volume = isMuted ? 0 : 1

    const playVideo = async () => {
      try {
        await video.play()
      } catch {
        // autoplay may be blocked; ignore
      }
    }

    playVideo()
  }, [isMuted])

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#1A120D] text-[#E0D0B6]">
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
            <a href="#faq" className="transition duration-300 hover:text-[#CC9E4C]">FAQ</a>
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
              <a href="#faq" className="transition hover:text-[#CC9E4C]" onClick={() => setMenuOpen(false)}>
                FAQ
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
          <div className="absolute inset-0 bg-gradient-to-b from-[#1A120D]/70 via-[#1A120D]/80 to-[#1A120D]/90" />
          <div className="absolute inset-0 bg-radial-gradient(circle at top-right, [#CC9E4C]/5, transparent 50%)" />
          {videoError && <div className="absolute inset-0 bg-[#1A120D]" />}
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex min-h-screen flex-col items-center justify-center overflow-hidden px-3 py-20 text-center sm:px-4 md:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="w-full max-w-5xl space-y-5 px-1 sm:space-y-8 sm:px-0"
          >
            {/* Eyebrow text */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-[0.62rem] uppercase tracking-[0.24em] text-[#CC9E4C] font-black sm:text-[0.7rem]"
            >
              Retro Roots. Fresh Energy.
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, delay: 0.2 }}
              className="mx-auto w-full max-w-[min(100%,32rem)] whitespace-nowrap text-[clamp(2.3rem,5vw,8rem)] font-black leading-[0.82] tracking-[-0.06em] text-[#E0D0B6] sm:max-w-[min(100%,38rem)]"
            >
              <span className="block">PRAGYARAMBH</span>
              <span className="mt-1 block text-[clamp(2.1rem,3.5vw,6rem)] text-[#CC9E4C] leading-[0.8]">3.0</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mx-auto max-w-[min(100%,40rem)] text-sm leading-relaxed text-[#D4C5AC] sm:text-base md:text-lg"
            >
              Where retro nostalgia meets a new generation.
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.35 }}
              className="mx-auto max-w-[min(100%,46rem)] text-xs leading-relaxed text-[#D4C5AC] sm:text-sm md:text-base"
            >
              Retro Fusion brings together the sounds, style and spirit of the past with the energy of a new generation — creating a freshers experience that feels familiar, yet completely new.
            </motion.p>

            {/* CTA Section */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex w-full flex-col items-stretch justify-center gap-3 pt-6 sm:flex-row sm:items-center sm:gap-6 sm:pt-8"
            >
              <button
                onClick={() => navigate('/register')}
                className="w-full max-w-[18rem] self-center px-6 py-3 text-[0.65rem] font-black tracking-[0.15em] text-[#442C1B] bg-[#CC9E4C] hover:bg-[#E0D0B6] transition duration-300 uppercase shadow-2xl shadow-[#CC9E4C]/20 sm:w-auto sm:max-w-none sm:px-10 md:px-12"
              >
                Register Now
              </button>
              <button
                onClick={() => {
                  const elem = document.getElementById('about')
                  elem?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="w-full max-w-[18rem] self-center border border-[#CC9E4C]/50 px-6 py-3 text-[0.65rem] font-black tracking-[0.15em] text-[#E0D0B6] transition duration-300 hover:border-[#CC9E4C] hover:text-[#CC9E4C] uppercase sm:w-auto sm:max-w-none sm:px-10 md:px-12"
              >
                Discover More
              </button>
            </motion.div>
          </motion.div>

          <button
            type="button"
            aria-label={isMuted ? 'Unmute background video' : 'Mute background video'}
            onClick={() => setIsMuted((prev) => !prev)}
            className="absolute bottom-5 right-4 z-20 flex h-10 w-10 items-center justify-center rounded-full border border-[#CC9E4C]/50 bg-[#1A120D]/65 text-[#E0D0B6] shadow-lg shadow-[#1A120D]/40 backdrop-blur-sm transition hover:border-[#CC9E4C] hover:text-[#CC9E4C] md:bottom-8 md:right-8"
          >
            {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>

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
      <section id="about" className="relative bg-[#1A120D] px-4 py-20 sm:px-8 md:py-32">
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
                  Three Departments.
                  <br />
                  One Freshers Era.
                  <br />
                  Zero Boring Introductions.
                </h2>
              </div>
              <p className="text-base text-[#D4C5AC] leading-relaxed font-light max-w-lg">
                Cybersecurity and Digital Forensics, Data Science and Data Analysis, and Artificial Intelligence and Machine Learning — three departments, one freshers experience, and plenty of new people to pretend you already know.
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
                { number: '3', label: 'Departments', detail: 'Cybersecurity and Digital Forensics • Data Science and Data Analysis • Artificial Intelligence and Machine Learning' },
                { number: '1', label: 'Shared Beginning', detail: 'New faces, new connections' },
                { number: 'Freshers', label: 'Edition', detail: 'Made for the newest members of our campus' },
                { number: 'Retro', label: 'Fusion', detail: 'A blend of nostalgia and modern energy' },
              ].map((item, idx) => (
                <div key={idx} className="space-y-2 border border-[#CC9E4C]/10 bg-[#201611]/60 p-4 rounded-lg">
                  <div className="text-3xl sm:text-4xl font-black text-[#CC9E4C]">{item.number}</div>
                  <p className="text-xs uppercase tracking-[0.08em] text-[#8B9EA5] font-semibold">{item.label}</p>
                  <p className="text-xs text-[#D4C5AC] font-light leading-relaxed">{item.detail}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Experience Section */}
      <section id="experience" className="relative bg-[#201611] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 md:mb-24"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black mb-3">Retro Fusion</p>
            <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
              Where retro nostalgia meets a new generation.
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
                <h3 className="text-2xl sm:text-3xl font-bold text-[#E0D0B6]">Music, Nostalgia & Creative Energy</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  Retro Fusion brings together the sounds, style and spirit of the past with the energy of a new generation — creating a freshers experience that feels familiar, yet completely new.
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
                <h3 className="text-xl sm:text-2xl font-bold text-[#E0D0B6]">Campus Connections</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  Meet new people, share the excitement and build fresh memories together as the newest faces on campus come together through music, creativity and joy.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.15 }}
                className="space-y-4"
              >
                <h3 className="text-xl sm:text-2xl font-bold text-[#E0D0B6]">Creativity in Motion</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">
                  From music and style to expression and energy, Pragyarambh celebrates the creativity and spirit of a new beginning for students across the three participating departments.
                </p>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Pragyarambh 2.0 Highlights */}
      <section className="relative bg-[#201611] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="rounded-2xl border border-[#CC9E4C]/15 bg-[#1A120D]/80 p-8 text-center shadow-[0_0_30px_rgba(204,158,76,0.08)] md:p-12"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black mb-4">Pragyarambh 2.0</p>
            <h2 className="text-4xl sm:text-5xl font-black leading-tight text-[#E0D0B6] tracking-[-0.02em]">
              A Glimpse of Pragyarambh 2.0
            </h2>
            <p className="mx-auto mt-6 max-w-2xl text-base text-[#D4C5AC] font-light leading-relaxed">
              Before we begin the next chapter, take a look back at the moments that made Pragyarambh 2.0 special.
            </p>
            <a
              href="https://drive.google.com/drive/folders/1fRLdUS_gzmn_UrNLKnJbVIHnKxjI4BTN?usp=sharing"
              target="_blank"
              rel="noreferrer"
              className="mt-8 inline-flex items-center justify-center px-8 py-3 text-xs font-black tracking-[0.15em] text-[#442C1B] bg-[#CC9E4C] transition hover:bg-[#E0D0B6] uppercase"
            >
              View Pragyarambh 2.0 Highlights
            </a>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="relative bg-[#1A120D] px-4 py-20 sm:px-8 md:py-32">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 md:mb-24"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-[#CC9E4C] font-black mb-3">FAQ</p>
            <h2 className="text-5xl sm:text-6xl font-black leading-[1.1] text-[#E0D0B6] tracking-[-0.02em]">
              Everything you need to know
            </h2>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2">
            {[
              {
                question: 'What is Pragyarambh 3.0?',
                answer: 'Pragyarambh 3.0 is the freshers celebration for Cybersecurity and Digital Forensics, Data Science and Data Analysis, and Artificial Intelligence and Machine Learning.'
              },
              {
                question: 'What is this year\'s theme?',
                answer: 'Retro Fusion — bringing together retro nostalgia with the energy and style of a new generation.'
              },
              {
                question: 'Who can attend?',
                answer: 'The event is intended for eligible freshers from the participating departments.'
              },
              {
                question: 'How do I register?',
                answer: 'Complete the registration form through the Register Now button. Follow the instructions provided during registration.'
              },
              {
                question: 'How will I receive my pass?',
                answer: 'Your pass will be sent to the email address provided during registration. Keep that email accessible after registering. No Pass, No Entry.'
              },
              {
                question: 'Is registration required?',
                answer: 'Yes. Students should complete their registration before attending.'
              },
              {
                question: 'What are the payment options?',
                answer: 'For students for whom payment applies, the registration page provides UPI and cash options. UPI users will be shown the QR code and payment-proof upload option.'
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: idx * 0.05 }}
                className="space-y-3 border border-[#CC9E4C]/10 bg-[#201611]/60 p-6 rounded-lg"
              >
                <h3 className="text-lg font-bold text-[#E0D0B6]">{item.question}</h3>
                <p className="text-[#D4C5AC] leading-relaxed font-light">{item.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative bg-[#1C1412] px-4 py-20 sm:px-8 md:py-32 overflow-hidden">
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
              Your First Chapter Starts Here.
            </h2>
            <p className="text-base text-[#D4C5AC] font-light max-w-2xl mx-auto leading-relaxed">
              Start your campus journey with a freshers celebration built around music, connection and a new beginning.
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
      <footer className="bg-[#120D0A] border-t border-[#CC9E4C]/20 px-4 py-16 sm:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 md:grid-cols-3 mb-12">
            <div className="space-y-2">
              <p className="text-xs font-black tracking-[0.3em] text-[#E0D0B6] uppercase">Pragyarambh</p>
              <p className="text-xs text-[#8B9EA5] font-light">Retro Roots. Fresh Energy.</p>
            </div>
            <div className="space-y-3 text-xs text-[#8B9EA5]">
              <p className="font-semibold text-[#E0D0B6] uppercase tracking-[0.08em]">Quick Links</p>
              <ul className="space-y-1 font-light">
                <li><a href="#about" className="hover:text-[#CC9E4C] transition">About</a></li>
                <li><a href="#experience" className="hover:text-[#CC9E4C] transition">Experience</a></li>
                <li><a href="#faq" className="hover:text-[#CC9E4C] transition">FAQ</a></li>
              </ul>
            </div>
            <div className="space-y-3 text-xs text-[#8B9EA5]">
              <p className="font-semibold text-[#E0D0B6] uppercase tracking-[0.08em]">Support</p>
              <ul className="space-y-1 font-light">
                <li><a href="/register" className="hover:text-[#CC9E4C] transition">Register</a></li>
                <li><a href="#faq" className="hover:text-[#CC9E4C] transition">FAQs</a></li>
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
