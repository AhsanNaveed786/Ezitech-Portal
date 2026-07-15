export default function ScoreRing({ value, size = 84, stroke = 7, label, sub }) {
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  const tone =
    value >= 85 ? '#34D399' :
    value >= 65 ? '#4F8EFF' :
    value >= 50 ? '#FBBF24' : '#F87171'

  return (
    <div className="flex items-center gap-3">
      <div className="relative shrink-0" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="rgba(120,160,255,0.12)" strokeWidth={stroke}
          />
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={tone} strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16,1,0.3,1)' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-sm font-semibold text-ink">{value}</span>
        </div>
      </div>
      {label && (
        <div className="min-w-0">
          <div className="text-sm font-medium text-ink truncate">{label}</div>
          {sub && <div className="text-xs text-ink-muted truncate">{sub}</div>}
        </div>
      )}
    </div>
  )
}
