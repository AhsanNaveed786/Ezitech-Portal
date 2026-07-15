import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts'

const gridColor = 'rgba(120,160,255,0.10)'
const axisColor = '#5C6E92'

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-panel rounded-lg px-3 py-2 shadow-glow">
      <p className="text-[11px] font-medium text-ink-muted">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="font-mono text-xs text-ink">
          <span style={{ color: p.color }}>●</span> {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  )
}

export function EngineeringTrendChart({ data, height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4F8EFF" stopOpacity={0.45} />
            <stop offset="100%" stopColor="#4F8EFF" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={gridColor} vertical={false} />
        <XAxis dataKey="week" stroke={axisColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis stroke={axisColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip content={<ChartTooltip />} />
        <Area type="monotone" dataKey="score" name="Engineering Score" stroke="#4F8EFF" strokeWidth={2.5} fill="url(#scoreGrad)" />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function TaskReviewChart({ data, height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid stroke={gridColor} vertical={false} />
        <XAxis dataKey="week" stroke={axisColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis stroke={axisColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip content={<ChartTooltip />} />
        <Line type="monotone" dataKey="tasks" name="Tasks Completed" stroke="#22D3EE" strokeWidth={2.5} dot={false} />
        <Line type="monotone" dataKey="reviews" name="Code Reviews" stroke="#34D399" strokeWidth={2.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function TechnologyBarChart({ data, height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} barGap={6}>
        <CartesianGrid stroke={gridColor} vertical={false} />
        <XAxis dataKey="technology" stroke={axisColor} tick={{ fontSize: 10 }} axisLine={false} tickLine={false} interval={0} angle={-15} textAnchor="end" height={50} />
        <YAxis stroke={axisColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip content={<ChartTooltip />} />
        <Bar dataKey="completion" name="Completion %" fill="#4F8EFF" radius={[6, 6, 0, 0]} />
        <Bar dataKey="avgScore" name="Avg Score" fill="#22D3EE" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function SkillRadarChart({ data, height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={data}>
        <PolarGrid stroke={gridColor} />
        <PolarAngleAxis dataKey="skill" tick={{ fill: axisColor, fontSize: 11 }} />
        <Radar name="You" dataKey="value" stroke="#4F8EFF" fill="#4F8EFF" fillOpacity={0.35} strokeWidth={2} />
        <Tooltip content={<ChartTooltip />} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
