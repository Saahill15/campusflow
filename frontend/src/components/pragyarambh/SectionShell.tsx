import React from 'react'

type SectionShellProps = {
  id?: string
  eyebrow?: string
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
}

export default function SectionShell({ id, eyebrow, title, description, children, className = '' }: SectionShellProps) {
  return (
    <section id={id} className={`mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 lg:px-8 ${className}`.trim()}>
      {(eyebrow || title || description) && (
        <div className="mb-10 max-w-3xl">
          {eyebrow ? <p className="mb-3 text-sm font-semibold uppercase tracking-[0.35em] text-cyan-300">{eyebrow}</p> : null}
          {title ? <h2 className="text-3xl font-semibold tracking-tight text-slate-50 sm:text-4xl">{title}</h2> : null}
          {description ? <p className="mt-4 text-lg leading-8 text-slate-300">{description}</p> : null}
        </div>
      )}
      {children}
    </section>
  )
}
