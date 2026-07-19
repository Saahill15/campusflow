import React from 'react'
import { CalendarDays, Clock3, MapPin, Sparkles, BellRing, CheckCircle2, ChevronRight, TrendingUp } from 'lucide-react'
import { Avatar, Button, Card, CardContent, CardHeader, CardTitle } from '../components/ui'

const quickStats = [
  { label: 'Events Available', value: '12', trend: '+3 this week' },
  { label: 'Registered', value: '6', trend: '2 pending' },
  { label: 'Approved', value: '4', trend: 'Ready for entry' },
  { label: "Today's Events", value: '2', trend: 'Live now' },
]

const upcomingEvents = [
  {
    name: 'Design Sprint Meetup',
    date: '19 Jul 2026',
    time: '6:30 PM',
    venue: 'Innovation Lab',
    status: 'Open for Registration',
  },
  {
    name: 'Campus Hack Night',
    date: '22 Jul 2026',
    time: '8:00 PM',
    venue: 'Tech Hub',
    status: 'Confirmed',
  },
  {
    name: 'Leadership Circle',
    date: '25 Jul 2026',
    time: '4:00 PM',
    venue: 'Main Auditorium',
    status: 'Almost Full',
  },
]

const registrations = [
  { event: 'Startup Showcase', status: 'Approved', date: '14 Jul 2026' },
  { event: 'AI Workshop', status: 'Pending', date: '16 Jul 2026' },
  { event: 'Cultural Fest', status: 'Approved', date: '18 Jul 2026' },
]

const announcements = [
  { title: 'New speaker lineup added', body: 'Three guest mentors joined the upcoming innovation week.' },
  { title: 'Venue update', body: 'The hack night venue now includes open seating and charging docks.' },
  { title: 'Reminder', body: 'Please carry your ID for all on-campus event entry.' },
]

const activity = [
  { title: 'Registered for AI Workshop', time: '2 hours ago' },
  { title: 'Checked in to Design Sprint', time: 'Yesterday' },
  { title: 'Updated profile preferences', time: '2 days ago' },
]

export default function StudentDashboard() {
  const today = new Date().toLocaleDateString('en', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-sm text-amber-300">
              <Sparkles size={14} />
              Welcome back
            </div>
            <h1 className="text-3xl font-semibold text-white">Good evening, Aarav</h1>
            <p className="mt-2 text-sm text-slate-300">Computer Science · 3rd Year</p>
            <p className="mt-4 text-sm text-slate-400">{today}</p>
          </div>
          <div className="flex items-center gap-4 rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3">
            <Avatar initials="AA" size="lg" className="border border-slate-700" />
            <div>
              <p className="font-medium text-white">Aarav Anand</p>
              <p className="text-sm text-slate-400">Student Portal</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {quickStats.map((stat) => (
          <Card key={stat.label} className="border-slate-800 bg-slate-900/80">
            <CardContent className="space-y-2">
              <p className="text-sm text-slate-400">{stat.label}</p>
              <div className="flex items-end justify-between">
                <p className="text-3xl font-semibold text-white">{stat.value}</p>
                <div className="flex items-center gap-1 text-xs text-emerald-400">
                  <TrendingUp size={12} />
                  {stat.trend}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.6fr_0.9fr]">
        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white">Upcoming Events</CardTitle>
              <Button variant="ghost" className="text-slate-300 hover:bg-slate-800">View all</Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {upcomingEvents.map((event) => (
              <div key={event.name} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mb-3 flex h-24 items-end rounded-xl bg-gradient-to-r from-amber-500/30 to-fuchsia-500/30 p-4">
                  <div className="rounded-full bg-slate-950/70 px-3 py-1 text-xs font-medium text-slate-100">
                    {event.status}
                  </div>
                </div>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{event.name}</h3>
                    <div className="mt-2 flex flex-wrap gap-3 text-sm text-slate-400">
                      <span className="flex items-center gap-1"><CalendarDays size={14} />{event.date}</span>
                      <span className="flex items-center gap-1"><Clock3 size={14} />{event.time}</span>
                      <span className="flex items-center gap-1"><MapPin size={14} />{event.venue}</span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="border-slate-700 text-slate-200 hover:bg-slate-800">
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="text-white">Announcements</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
              {announcements.map((item) => (
                <div key={item.title} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-white">
                    <BellRing size={14} className="text-amber-400" />
                    {item.title}
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{item.body}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="text-white">My Registrations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-xl border border-slate-800">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-950/80 text-left text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Event</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {registrations.map((row) => (
                    <tr key={row.event} className="border-t border-slate-800 bg-slate-900/40">
                      <td className="px-4 py-3 text-white">{row.event}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${row.status === 'Approved' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'}`}>
                          {row.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">{row.date}</td>
                      <td className="px-4 py-3">
                        <button className="flex items-center gap-1 text-sm text-slate-300 hover:text-white">
                          View <ChevronRight size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/80">
          <CardHeader>
            <CardTitle className="text-white">Activity Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activity.map((item, index) => (
                <div key={item.title} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-amber-500/15 text-amber-300">
                      <CheckCircle2 size={16} />
                    </div>
                    {index < activity.length - 1 ? <div className="mt-1 h-full w-px bg-slate-800" /> : null}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{item.title}</p>
                    <p className="text-sm text-slate-400">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
