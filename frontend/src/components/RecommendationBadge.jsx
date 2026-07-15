import { recommendationTypes } from '../data/mockData'

const toneStyles = {
  up: 'bg-signal-up/10 text-signal-up border-signal-up/25',
  warn: 'bg-signal-warn/10 text-signal-warn border-signal-warn/25',
  down: 'bg-signal-down/10 text-signal-down border-signal-down/25',
  idle: 'bg-signal-idle/10 text-signal-idle border-signal-idle/25',
}

export default function RecommendationBadge({ type }) {
  const rec = recommendationTypes[type]
  if (!rec) return null
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${toneStyles[rec.tone]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {rec.label}
    </span>
  )
}
