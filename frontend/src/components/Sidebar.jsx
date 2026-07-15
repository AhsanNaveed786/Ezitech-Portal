import { NavLink } from 'react-router-dom'
import { LayoutGrid, ShieldCheck, GraduationCap, Cpu, ChevronRight } from 'lucide-react'

const navItems = [
  { to: '/mentor', label: 'Mentor Dashboard', icon: LayoutGrid, desc: 'Team & recommendations' },
  { to: '/admin', label: 'Admin Dashboard', icon: ShieldCheck, desc: 'Internship-wide health' },
  { to: '/student', label: 'Student Dashboard', icon: GraduationCap, desc: 'Your engineering growth' },
]

export default function Sidebar() {
  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 shrink-0 flex-col border-r border-line bg-base-900/60 backdrop-blur-xl">
      <div className="flex items-center gap-2.5 px-6 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-cyan shadow-glow">
          <Cpu size={18} className="text-base-950" strokeWidth={2.5} />
        </div>
        <div>
          <p className="font-display text-sm font-bold leading-none text-ink">AI-MIEDP</p>
          <p className="mt-1 text-[10px] font-medium uppercase tracking-wider text-ink-faint">Ezitech · EEF</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        <p className="px-3 pb-2 pt-2 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">Workspaces</p>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-3 py-3 transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-brand-800/60 to-brand-900/20 border border-brand-700/40 shadow-glow'
                  : 'border border-transparent hover:bg-base-700/50'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${isActive ? 'bg-brand-500 text-white' : 'bg-base-700 text-ink-muted group-hover:text-ink'}`}>
                  <item.icon size={16} strokeWidth={2} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className={`text-sm font-medium truncate ${isActive ? 'text-ink' : 'text-ink-muted group-hover:text-ink'}`}>{item.label}</p>
                  <p className="text-[11px] text-ink-faint truncate">{item.desc}</p>
                </div>
                <ChevronRight size={14} className={`shrink-0 transition-opacity ${isActive ? 'opacity-70 text-brand-300' : 'opacity-0 group-hover:opacity-40'}`} />
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="m-3 rounded-xl border border-line bg-base-800/60 p-4">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-brand-300">AI Engine</p>
        <p className="mt-1.5 text-xs leading-relaxed text-ink-muted">
          Recommendations refresh continuously from attendance, GitHub, reviews & case-study signals.
        </p>
        <div className="mt-3 flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-signal-up opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-signal-up"></span>
          </span>
          <span className="text-[11px] font-medium text-ink-muted">Engine live</span>
        </div>
      </div>
    </aside>
  )
}
