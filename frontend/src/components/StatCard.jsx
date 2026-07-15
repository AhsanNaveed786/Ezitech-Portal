import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

export default function StatCard({ label, value, suffix = '', delta, icon: Icon, tone = 'brand' }) {
  const toneMap = {
    brand: 'text-brand-300 bg-brand-900/40 border-brand-700/40',
    up: 'text-signal-up bg-signal-up/10 border-signal-up/25',
    warn: 'text-signal-warn bg-signal-warn/10 border-signal-warn/25',
    down: 'text-signal-down bg-signal-down/10 border-signal-down/25',
  }

  const deltaPositive = delta > 0
  const deltaZero = delta === 0

  return (
    <div className="glass-panel rounded-2xl p-5 shadow-card animate-rise">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-ink-faint">{label}</p>
          <p className="mt-2 font-display text-3xl font-semibold text-ink">
            {value}<span className="text-lg text-ink-muted">{suffix}</span>
          </p>
        </div>
        {Icon && (
          <div className={`rounded-xl border p-2.5 ${toneMap[tone]}`}>
            <Icon size={18} strokeWidth={2} />
          </div>
        )}
      </div>
      {typeof delta === 'number' && (
        <div className="mt-3 flex items-center gap-1 text-xs font-medium">
          {deltaZero ? (
            <Minus size={13} className="text-ink-faint" />
          ) : deltaPositive ? (
            <ArrowUpRight size={13} className="text-signal-up" />
          ) : (
            <ArrowDownRight size={13} className="text-signal-down" />
          )}
          <span className={deltaZero ? 'text-ink-faint' : deltaPositive ? 'text-signal-up' : 'text-signal-down'}>
            {deltaPositive && !deltaZero ? '+' : ''}{delta}%
          </span>
          <span className="text-ink-faint">vs last week</span>
        </div>
      )}
    </div>
  )
}
