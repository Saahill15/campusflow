import React, { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, ChevronDown, Compass, Music4, Sparkles } from 'lucide-react'

const particles = [
  { left: '8%', top: '18%', size: 8, delay: 0 },
  { left: '18%', top: '76%', size: 10, delay: 0.6 },
  { left: '82%', top: '24%', size: 6, delay: 0.3 },
  { left: '86%', top: '72%', size: 12, delay: 1.1 },
]

export default function PragyarambhLanding() {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })
  const [glow, setGlow] = useState({ x: 50, y: 50 })
  const [musicOn, setMusicOn] = useState(false)

  useEffect(() => {
    const target = new Date('2026-08-19T18:00:00')
    const tick = () => {
      const diff = target.getTime() - Date.now()
      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
        return
      }
      setTimeLeft({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((diff / (1000 * 60)) % 60),
        seconds: Math.floor((diff / 1000) % 60),
      })
    }
    tick()
    const interval = window.setInterval(tick, 1000)
    return () => window.clearInterval(interval)
  }, [])

  const stats = useMemo(() => [
    { label: 'Days', value: timeLeft.days },
    { label: 'Hours', value: timeLeft.hours },
    { label: 'Minutes', value: timeLeft.minutes },
    { label: 'Seconds', value: timeLeft.seconds },
  ], [timeLeft])

  return (
    <div className="min-h-screen bg-[#080314] text-slate-50">
      <div className="relative min-h-[100svh] overflow-hidden">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(124,58,237,0.24),_transparent_30%),radial-gradient(circle_at_80%_20%,_rgba(255,45,170,0.18),_transparent_25%),radial-gradient(circle_at_bottom_right,_rgba(51,209,255,0.16),_transparent_28%)]" />
          <motion.div animate={{ x: [0, 16, -10, 0], y: [0, -20, 18, 0] }} transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }} className="absolute left-1/2 top-1/4 h-72 w-72 -translate-x-1/2 rounded-full bg-fuchsia-500/20 blur-[120px]" />
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 50, repeat: Infinity, ease: 'linear' }} className="absolute inset-0 opacity-40 bg-[conic-gradient(from_0deg,_rgba(255,255,255,0.12),_rgba(51,209,255,0.18),_rgba(255,45,170,0.18),_rgba(255,255,255,0.12))]" />
          {particles.map((particle) => (
            <motion.span
              key={`${particle.left}-${particle.top}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: [0.2, 0.8, 0.2], y: [0, -12, 0] }}
              transition={{ duration: 4.5 + particle.delay, repeat: Infinity, delay: particle.delay }}
              className="absolute rounded-full bg-white/70"
              style={{ left: particle.left, top: particle.top, width: particle.size, height: particle.size }}
            />
          ))}
        </div>

        <div
          className="relative z-10 flex min-h-[100svh] flex-col px-4 py-6 sm:px-6 lg:px-8"
          onMouseMove={(event) => {
            const rect = event.currentTarget.getBoundingClientRect()
            setGlow({ x: ((event.clientX - rect.left) / rect.width) * 100, y: ((event.clientY - rect.top) / rect.height) * 100 })
          }}
        >
          <div className="absolute inset-0 pointer-events-none" style={{ background: `radial-gradient(circle at ${glow.x}% ${glow.y}%, rgba(255,255,255,0.12), transparent 28%)` }} />

          <header className="mx-auto flex w-full max-w-7xl items-center justify-between">
            <a href="#home" className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.35em] text-slate-100">
              <span className="rounded-full border border-cyan-400/40 bg-cyan-400/10 p-1.5"><Compass size={14} className="text-cyan-300" /></span>
              Pragyarambh
            </a>
            <button
              onClick={() => setMusicOn((value) => !value)}
              className="rounded-full border border-white/10 bg-white/10 p-2.5 text-slate-100 backdrop-blur-xl transition hover:bg-white/15"
              aria-label="Toggle music"
            >
              <Music4 size={18} className={musicOn ? 'text-cyan-300' : 'text-slate-200'} />
            </button>
          </header>

          <main id="home" className="flex flex-1 items-center justify-center">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }} className="mx-auto flex w-full max-w-5xl flex-col items-center text-center">
              <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1, duration: 0.6 }} className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-200 backdrop-blur">
                <Sparkles size={14} className="text-amber-300" />
                RETRO FUSION
              </motion.div>

              <motion.h1 initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16, duration: 0.8 }} className="max-w-4xl text-5xl font-black uppercase tracking-[0.28em] text-white sm:text-7xl lg:text-8xl">
                PRAGYARAMBH
                <span className="mt-4 block text-[0.45em] font-semibold tracking-[0.2em] text-cyan-300">2026</span>
              </motion.h1>

              <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.24, duration: 0.8 }} className="mt-6 max-w-2xl text-xl leading-8 text-slate-300 sm:text-2xl">
                Your college story starts with one night that feels bigger than your first lecture.
              </motion.p>

              <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.8 }} className="mt-4 max-w-2xl text-base leading-8 text-slate-400 sm:text-lg">
                We know you&apos;re nervous. Everyone is. They&apos;re just better at pretending. This is the part where the campus actually becomes exciting.
              </motion.p>

              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.36, duration: 0.8 }} className="mt-8 grid w-full max-w-3xl gap-3 sm:grid-cols-4">
                {stats.map((item) => (
                  <div key={item.label} className="rounded-[1.2rem] border border-white/10 bg-white/10 p-4 backdrop-blur-xl">
                    <div className="text-3xl font-semibold text-white">{item.value}</div>
                    <div className="mt-1 text-sm uppercase tracking-[0.25em] text-slate-300">{item.label}</div>
                  </div>
                ))}
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.44, duration: 0.8 }} className="mt-10 flex flex-wrap items-center justify-center gap-4">
                <a href="#" className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-fuchsia-500 to-violet-600 px-7 py-3 font-semibold text-white shadow-[0_20px_60px_rgba(124,58,237,0.35)] transition hover:scale-[1.02]">
                  Count Me In <ArrowRight size={18} />
                </a>
                <a href="#" className="rounded-full border border-white/10 bg-white/5 px-7 py-3 font-semibold text-slate-100 backdrop-blur transition hover:bg-white/10">
                  What&apos;s Waiting?
                </a>
              </motion.div>

              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5, duration: 0.8 }} className="mt-12 flex flex-col items-center text-sm text-slate-300">
                <span>Scroll to feel the pulse</span>
                <ChevronDown className="mt-2 animate-bounce" size={18} />
              </motion.div>
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}
