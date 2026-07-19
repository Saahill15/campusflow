import React from 'react'
import { ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react'
import { Button } from '../components/ui'

const upcomingEvents = [
  {
    title: 'Pragyarambh 2026',
    subtitle: 'Freshers Night',
    meta: '19 Aug • Auditorium',
    cta: 'Register Now',
  },
  {
    title: 'TechFest',
    subtitle: 'Hackathon',
    meta: 'Coming Soon',
    cta: 'Notify Me',
  },
]

const features = ['Easy Registration', 'QR Passes', 'Instant Check-in', 'Real-time Entry']

export default function Landing() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8">
      <section className="rounded-[2rem] border border-slate-800 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-8 text-white shadow-2xl shadow-black/20 md:p-12">
        <div className="max-w-3xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-sm text-amber-300">
            <Sparkles size={14} />
            One Platform. Every College Event.
          </div>
          <h1 className="text-4xl font-semibold leading-tight md:text-6xl">CampusFlow</h1>
          <p className="mt-4 max-w-2xl text-lg text-slate-300">
            Manage registrations, approvals, QR passes and event check-ins from one premium experience.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button size="lg" className="bg-amber-500 text-slate-950 hover:bg-amber-400">Get Started</Button>
            <Button size="lg" variant="outline" className="border-slate-700 text-slate-100 hover:bg-slate-800">
              Login
            </Button>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="text-2xl font-semibold text-white">Upcoming Events</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {upcomingEvents.map((event) => (
              <div key={event.title} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                <div className="mb-4 h-24 rounded-xl bg-gradient-to-br from-amber-500/30 to-fuchsia-500/30" />
                <h3 className="text-lg font-semibold text-white">{event.title}</h3>
                <p className="mt-1 text-sm text-slate-400">{event.subtitle}</p>
                <p className="mt-2 text-sm text-slate-500">{event.meta}</p>
                <div className="mt-4">
                  <Button variant="outline" size="sm" className="border-slate-700 text-slate-200 hover:bg-slate-800">
                    {event.cta}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="text-2xl font-semibold text-white">Why CampusFlow?</h2>
          <div className="mt-6 space-y-3">
            {features.map((feature) => (
              <div key={feature} className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-slate-200">
                <CheckCircle2 size={16} className="text-emerald-400" />
                {feature}
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="text-center text-sm text-slate-500">© Pragyarambh</footer>
    </div>
  )
}
