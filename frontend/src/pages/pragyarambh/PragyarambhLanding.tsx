import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Compass } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function PragyarambhLanding() {
  const [isMuted, setIsMuted] = useState(true)
  const [videoError, setVideoError] = useState(false)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const playVideo = async () => {
      try {
        video.muted = isMuted
        await video.play()
      } catch {
        // autoplay may be blocked; ignore
      }
    }

    playVideo()
  }, [isMuted])

  return (
    <section className="relative min-h-screen overflow-hidden bg-[#04030a] text-white">
      <div className="absolute inset-0">
        <video
          ref={videoRef}
          className="absolute inset-0 h-full w-full object-cover"
          autoPlay
          loop
          playsInline
          muted={isMuted}
          preload="auto"
          poster="/video.mp4"
          src="/video.mp4"
          onError={() => setVideoError(true)}
        />
        <div className="absolute inset-0 bg-black/65" />
        {videoError && <div className="absolute inset-0 bg-gradient-to-b from-[#030313] via-[#041028] to-[#000]" />}
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.14),_transparent_22%),radial-gradient(circle_at_bottom_right,_rgba(255,255,255,0.08),_transparent_18%)]" />
      </div>

      <div className="relative z-20 mx-auto flex min-h-screen max-w-7xl flex-col gap-8 px-6 py-8 sm:px-8 lg:px-12">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-3xl border border-white/15 bg-white/5 text-cyan-300 shadow-[0_20px_60px_rgba(6,182,212,0.18)]">
              <Compass size={20} />
            </span>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-300/90">Pragyarambh</p>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">Campus Freshers' Night</h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200 shadow-[0_18px_50px_rgba(0,0,0,0.3)]">
            <span className="font-semibold text-white">14 August 2026</span>
            <span className="h-1 w-1 rounded-full bg-slate-300/70" />
            <span>Campus Grounds</span>
            <span className="h-1 w-1 rounded-full bg-slate-300/70" />
            <span>Open to all</span>
          </div>
        </header>

        <div className="grid gap-10 lg:grid-cols-[1.4fr_1fr] lg:items-center">
          <div className="space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, ease: 'easeOut' }}
              className="space-y-6"
            >
              <p className="inline-flex rounded-full border border-cyan-300/40 bg-cyan-300/10 px-4 py-2 text-xs uppercase tracking-[0.3em] text-cyan-200 shadow-[0_20px_45px_rgba(6,182,212,0.12)]">
                Campus event • Limited spots
              </p>
              <h2 className="text-5xl font-black leading-[0.95] tracking-[-0.04em] text-white sm:text-6xl">
                The <span className="text-cyan-300">ultimate</span> welcome night for freshers.
              </h2>
              <p className="max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
                Join Pragyarambh 2026 for music, lights, rhythm and an unforgettable first impression. Everything is crafted to feel premium, polished, and designed for the new campus generation.
              </p>
            </motion.div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { title: 'Live performances', description: 'Dance, DJ sets & campus energy.' },
                { title: 'Food & drinks', description: 'Street-food flavors and chill zones.' },
                { title: 'Meet new friends', description: 'Connect with freshers and seniors.' },
              ].map((feature) => (
                <div key={feature.title} className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-md">
                  <p className="text-sm uppercase tracking-[0.28em] text-cyan-200/80">{feature.title}</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{feature.description}</p>
                </div>
              ))}
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-center">
                <p className="text-3xl font-semibold text-white">14 Aug</p>
                <p className="mt-2 text-sm uppercase tracking-[0.25em] text-slate-400">Date</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-center">
                <p className="text-3xl font-semibold text-white">7 PM</p>
                <p className="mt-2 text-sm uppercase tracking-[0.25em] text-slate-400">Starts</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-center">
                <p className="text-3xl font-semibold text-white">Campus</p>
                <p className="mt-2 text-sm uppercase tracking-[0.25em] text-slate-400">Venue</p>
              </div>
            </div>
          </div>

          <motion.aside
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.9, ease: 'easeOut' }}
            className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/40 backdrop-blur-xl"
          >
            <div className="flex flex-col gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.32em] text-cyan-200/90">Registration</p>
                <h3 className="mt-3 text-2xl font-bold text-white">Register for Pragyarambh 2026</h3>
              </div>

              <p className="text-sm leading-6 text-slate-300">
                One dedicated registration page contains the full event form. Tap below to complete your details in a clean, focused experience.
              </p>

              <div className="grid gap-4 rounded-3xl border border-white/10 bg-black/20 p-5 text-sm text-slate-200">
                <p className="font-semibold text-white">Only one registration page</p>
                <p>All required details are collected on /register, including your name, department, roll number, phone, email and gender.</p>
                <p className="text-cyan-200">No duplicate form on the landing page.</p>
              </div>

              <button
                type="button"
                onClick={() => navigate('/register')}
                className="mt-6 rounded-3xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-4 text-lg font-semibold text-white transition hover:scale-[1.01] focus:outline-none focus:ring-2 focus:ring-cyan-300"
              >
                REGISTER NOW
              </button>

              <button
                type="button"
                onClick={() => setIsMuted((prev) => !prev)}
                className="mt-4 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
              >
                {isMuted ? 'Audio Off' : 'Audio On'}
              </button>
            </div>
          </motion.aside>
        </div>
      </div>
    </section>
  )
}
