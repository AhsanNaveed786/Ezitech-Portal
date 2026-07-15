import ScoreRing from './ScoreRing'
import RecommendationBadge from './RecommendationBadge'

const statusDot = {
  active: 'bg-signal-up',
  watch: 'bg-signal-warn',
  at_risk: 'bg-signal-down',
}

export default function InternTable({ data, title = 'Intern Performance', dense = false }) {
  return (
    <div className="glass-panel rounded-2xl shadow-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <h3 className="font-display text-sm font-semibold text-ink">{title}</h3>
        <span className="text-xs text-ink-faint">{data.length} interns</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-line text-[11px] uppercase tracking-wider text-ink-faint">
              <th className="px-5 py-3 font-medium">Intern</th>
              <th className="px-5 py-3 font-medium">Technology</th>
              <th className="px-5 py-3 font-medium">Score</th>
              <th className="px-5 py-3 font-medium">Deadline</th>
              <th className="px-5 py-3 font-medium">Credits</th>
              <th className="px-5 py-3 font-medium">AI Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {data.map((intern) => (
              <tr key={intern.id} className="border-b border-line/60 last:border-0 hover:bg-base-700/30 transition-colors">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 shrink-0 rounded-full ${statusDot[intern.status]}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-ink truncate">{intern.name}</p>
                      <p className="eef-id text-[11px] text-ink-faint">{intern.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3.5 text-sm text-ink-muted">{intern.technology}</td>
                <td className="px-5 py-3.5">
                  <ScoreRing value={intern.engineeringScore} size={dense ? 40 : 44} stroke={5} />
                </td>
                <td className="px-5 py-3.5 text-sm text-ink-muted">{intern.deadlineCompliance}%</td>
                <td className="px-5 py-3.5 font-mono text-sm text-ink-muted">{intern.engineeringCredits}</td>
                <td className="px-5 py-3.5">
                  <RecommendationBadge type={intern.recommendation} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
