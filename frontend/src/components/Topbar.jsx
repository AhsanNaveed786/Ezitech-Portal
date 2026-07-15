import { Search, Bell, Menu } from 'lucide-react'

export default function Topbar({ title, subtitle, onMenuClick }) {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-base-950/70 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-5 py-4 md:px-8">
        <div className="flex items-center gap-3">
          <button onClick={onMenuClick} className="md:hidden rounded-lg border border-line p-2 text-ink-muted">
            <Menu size={18} />
          </button>
          <div>
            <h1 className="font-display text-lg font-semibold text-ink md:text-xl">{title}</h1>
            {subtitle && <p className="text-xs text-ink-muted md:text-sm">{subtitle}</p>}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 rounded-xl border border-line bg-base-800/60 px-3 py-2 w-72">
            <Search size={15} className="text-ink-faint" />
            <input
              placeholder="Search interns, mentors, batches…"
              className="w-full bg-transparent text-sm text-ink placeholder:text-ink-faint focus:outline-none"
            />
            <kbd className="rounded border border-line px-1.5 py-0.5 text-[10px] text-ink-faint">⌘K</kbd>
          </div>
          <button className="relative rounded-xl border border-line bg-base-800/60 p-2.5 text-ink-muted hover:text-ink">
            <Bell size={16} />
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-cyan" />
          </button>
          <div className="flex items-center gap-2 rounded-xl border border-line bg-base-800/60 py-1.5 pl-1.5 pr-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-cyan font-display text-xs font-bold text-base-950">
              ZE
            </div>
            <div className="hidden sm:block">
              <p className="text-xs font-medium leading-tight text-ink">Zainab Emaan</p>
              <p className="text-[10px] leading-tight text-ink-faint">AI Engineer</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
