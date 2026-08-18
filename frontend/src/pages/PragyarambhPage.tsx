import React, { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, Sparkles, Music4, Camera, UtensilsCrossed, Gamepad2, CalendarDays, MapPin, Phone, Globe2, Send, PlayCircle, Menu, X } from 'lucide-react'

const highlights = [
  { title: 'DJ Night', icon: Music4, description: 'Neon-lit sets, live mixing, and midnight energy.' },
  { title: 'Performances', icon: Sparkles, description: 'Dance battles, band sets, and theatrical showcases.' },
  { title: 'Games', icon: Gamepad2, description: 'Arcade zones, team challenges, and surprise quests.' },
  { title: 'Food', icon: UtensilsCrossed, description: 'Curated street-food stalls and signature bites.' },
  { title: 'Photography', icon: Camera, description: 'A cinematic campus experience captured all night.' },
]

const timeline = [
  { time: '4:00 PM', title: 'Campus Gates Open', body: 'Check-in, welcome kits, and first-light vibes.' },
  { time: '6:30 PM', title: 'Opening Ceremony', body: 'Hosts, lights, and the grand reveal.' },
  { time: '8:00 PM', title: 'Main Stage', body: 'Live performances and headline acts.' },
  { time: '10:30 PM', title: 'Afterhours', body: 'DJ set, food stalls, and neon memories.' },
]

const gallery = [
  'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=800&q=80',
]

const faqItems = [
  { question: 'What is Pragyarambh?', answer: 'Pragyarambh is a high-energy annual fest where culture, music, creativity, and campus togetherness come alive.' },
  { question: 'Is entry free?', answer: 'Yes. Entry is complimentary for all registered students and guests.' },
  { question: 'What should I bring?', answer: 'Bring your ID, a charged phone, and your best event energy.' },
  { question: 'Can I bring a friend?', answer: 'Absolutely. Guest passes are available at the registration desk.' },
]

export default function PragyarambhPage() {
  const [openFaq, setOpenFaq] = useState(0)
  const [menuOpen, setMenuOpen] = useState(false)
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })

  useEffect(() => {
    const target = new Date('2026-08-19T18:00:00')
    const tick = () => {
      const diff = target.getTime() - Date.now()
      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
        return
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24)
      const minutes = Math.floor((diff / (1000 * 60)) % 60)
      const seconds = Math.floor((diff / 1000) % 60)
      setTimeLeft({ days, hours, minutes, seconds })
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
    <div className="min-h-screen bg-[#04070d] text-white">
      <header className="fixed inset-x-0 top-0 z-50 px-4 py-4 md:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between rounded-full border border-white/10 bg-black/20 px-4 py-3 backdrop-blur-xl">
          <div className="text-lg font-semibold tracking-[0.35em] text-white">PRAGYARAMBH</div>
          <nav className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
            {['Home', 'About', 'Timeline', 'Gallery', 'FAQ', 'Register'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="transition hover:text-white">{item}</a>
            ))}
          </nav>
          <button className="rounded-full border border-white/15 p-2 text-slate-200 md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
        {menuOpen ? (
          <div className="mx-auto mt-3 max-w-7xl rounded-2xl border border-white/10 bg-black/50 p-4 text-sm text-slate-200 backdrop-blur-xl md:hidden">
            {['Home', 'About', 'Timeline', 'Gallery', 'FAQ', 'Register'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="block py-2" onClick={() => setMenuOpen(false)}>{item}</a>
            ))}
          </div>
        ) : null}
      </header>

      <main id="home">
        <section className="relative flex min-h-screen items-center overflow-hidden px-4 py-24 md:px-8">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.2),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(217,70,239,0.16),_transparent_35%)]" />
          <div className="absolute inset-0 opacity-30">
            <div className="absolute inset-0 animate-[spin_60s_linear_infinite] bg-[conic-gradient(from_0deg,_rgba(255,255,255,0.12),_rgba(251,191,36,0.20),_rgba(168,85,247,0.20),_rgba(255,255,255,0.12))]" />
          </div>
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="relative z-10 mx-auto flex max-w-6xl flex-col items-center text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-200 backdrop-blur">
              <Sparkles size={16} className="text-amber-300" />
              August 19 • Main Campus • 6 PM onwards
            </div>
            <h1 className="max-w-5xl text-5xl font-black uppercase tracking-[0.2em] text-white sm:text-7xl lg:text-8xl">PRAGYARAMBH 3.0</h1>
            <p className="mt-6 text-xl text-slate-300 sm:text-2xl">A Night of Lights, Music, Motion, and Memories</p>
            <div className="mt-10 grid w-full max-w-3xl gap-4 sm:grid-cols-4">
              {stats.map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-xl">
                  <div className="text-3xl font-semibold text-white">{item.value}</div>
                  <div className="mt-1 text-sm text-slate-300">{item.label}</div>
                </div>
              ))}
            </div>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <a href="#register" className="rounded-full bg-amber-400 px-7 py-3 font-semibold text-slate-950 transition hover:scale-[1.02] hover:bg-amber-300">Register Now</a>
              <a href="#about" className="rounded-full border border-white/15 bg-white/5 px-7 py-3 font-semibold text-white backdrop-blur transition hover:bg-white/10">Explore Experience</a>
            </div>
            <div className="mt-12 flex flex-col items-center text-sm text-slate-300">
              <span>Scroll to discover</span>
              <ChevronDown className="mt-2 animate-bounce" size={20} />
            </div>
          </motion.div>
        </section>

        <section id="about" className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
              <p className="text-sm uppercase tracking-[0.3em] text-amber-300">About Pragyarambh</p>
              <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">A cinematic campus celebration crafted for every kind of student.</h2>
              <p className="mt-6 text-lg leading-8 text-slate-300">Pragyarambh is where the campus transforms into a playground of sound, light, and unforgettable energy. From live performances to immersive experiences, every corner of the evening is designed to spark joy and unforgettable connection.</p>
            </motion.div>
            <div className="grid gap-4 sm:grid-cols-2">
              {gallery.slice(0, 2).map((img, index) => (
                <img key={img} src={img} alt="Pragyarambh moment" className={`h-56 w-full rounded-[1.5rem] object-cover ${index === 0 ? 'sm:translate-y-6' : ''}`} />
              ))}
            </div>
          </div>
        </section>

        <section id="timeline" className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="mb-10 text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-amber-300">Event Highlights</p>
            <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">Moments built to feel larger than life</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {highlights.map((item, index) => {
              const Icon = item.icon
              return (
                <motion.div key={item.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.05 }} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-400/15 text-amber-300"><Icon size={20} /></div>
                  <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                  <p className="mt-2 text-sm leading-7 text-slate-300">{item.description}</p>
                </motion.div>
              )
            })}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-8 backdrop-blur-xl">
            <div className="mb-8 text-center">
              <p className="text-sm uppercase tracking-[0.3em] text-amber-300">Schedule Timeline</p>
              <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">The night unfolds in style</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {timeline.map((item, index) => (
                <div key={item.time} className="rounded-[1.25rem] border border-white/10 bg-slate-950/60 p-5">
                  <div className="text-sm text-amber-300">{item.time}</div>
                  <h3 className="mt-3 text-lg font-semibold text-white">{item.title}</h3>
                  <p className="mt-2 text-sm leading-7 text-slate-300">{item.body}</p>
                  {index < timeline.length - 1 ? <div className="mt-4 h-px w-full bg-white/10" /> : null}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="gallery" className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="mb-8 text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-amber-300">Gallery Preview</p>
            <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">A peek at the atmosphere</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {gallery.map((img, index) => (
              <img key={img} src={img} alt="Pragyarambh gallery" className={`w-full rounded-[1.5rem] object-cover ${index === 1 ? 'h-80' : 'h-64'} ${index === 2 ? 'lg:translate-y-8' : ''}`} />
            ))}
          </div>
        </section>

        <section id="faq" className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
            <div className="mb-8 text-center">
              <p className="text-sm uppercase tracking-[0.3em] text-amber-300">FAQ</p>
              <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">Everything you need to know</h2>
            </div>
            <div className="space-y-3">
              {faqItems.map((item, index) => (
                <div key={item.question} className="rounded-2xl border border-white/10 bg-slate-950/60">
                  <button className="flex w-full items-center justify-between px-5 py-4 text-left text-white" onClick={() => setOpenFaq(index === openFaq ? -1 : index)}>
                    <span>{item.question}</span>
                    <span className="text-amber-300">{index === openFaq ? '−' : '+'}</span>
                  </button>
                  {index === openFaq ? <p className="px-5 pb-5 text-sm leading-7 text-slate-300">{item.answer}</p> : null}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="register" className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="rounded-[2rem] border border-amber-400/20 bg-gradient-to-r from-amber-400/15 via-fuchsia-500/10 to-slate-900 p-10 text-center backdrop-blur-xl">
            <h2 className="text-3xl font-semibold text-white sm:text-4xl">Reserve your place at the night of the year</h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-300">Register now and step into a celebration that feels cinematic, electric, and unforgettable.</p>
            <a href="#home" className="mt-8 inline-block rounded-full bg-amber-400 px-7 py-3 font-semibold text-slate-950 transition hover:bg-amber-300">Register Now</a>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 bg-black/20 px-4 py-10 md:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-lg font-semibold tracking-[0.35em] text-white">PRAGYARAMBH</div>
            <div className="mt-2">Main Auditorium • Campus Square</div>
          </div>
          <div className="flex gap-4 text-white">
            <a href="https://instagram.com" aria-label="Instagram"><Globe2 size={18} /></a>
            <a href="https://facebook.com" aria-label="Facebook"><Send size={18} /></a>
            <a href="https://youtube.com" aria-label="YouTube"><PlayCircle size={18} /></a>
          </div>
          <div className="flex items-center gap-2"><Phone size={16} /> +91 98765 43210</div>
        </div>
      </footer>
    </div>
  )
}
