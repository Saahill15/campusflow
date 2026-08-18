import React from 'react'
import PragyarambhRegistrationCard from '../../components/pragyarambh/PragyarambhRegistrationCard'

export default function RegisterPage() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-[#04030a] text-white">
      <div className="absolute inset-0 bg-black/75" />
      <div className="relative z-20 mx-auto max-w-6xl px-6 py-12 sm:px-8 lg:px-12">
        <div className="space-y-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/90">Pragyarambh 3.0</p>
            <h1 className="mt-3 text-4xl font-black tracking-tight text-white sm:text-5xl">
              Register for Pragyarambh 3.0
            </h1>
            <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-300">
              Complete the registration form below to reserve your spot for the event.
            </p>
          </div>
          <PragyarambhRegistrationCard />
        </div>
      </div>
    </section>
  )
}
