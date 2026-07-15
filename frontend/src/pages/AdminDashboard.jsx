import Topbar from '../components/Topbar'
import StatCard from '../components/StatCard'
import InternTable from '../components/InternTable'
import { TechnologyBarChart, TaskReviewChart } from '../components/Charts'
import {
  interns, technologyPerformance, weeklyEngineeringReport, batchComparison,
  internshipHealth, aiInsights, mentors,
} from '../data/mockData'
import { Activity, Users, GraduationCap, AlertTriangle, TrendingUp, Sparkles } from 'lucide-react'

const insightTone = {
  up: 'border-signal-up/25 bg-signal-up/5 text-signal-up',
  down: 'border-signal-down/25 bg-signal-down/5 text-signal-down',
  warn: 'border-signal-warn/25 bg-signal-warn/5 text-signal-warn',
}

export default function AdminDashboard({ onMenuClick }) {
  const readyForHiring = interns.filter((i) => ['PLACEMENT', 'INTERVIEW'].includes(i.recommendation))

  return (
    <div className="flex-1 min-w-0">
      <Topbar title="Admin Dashboard" subtitle="Internship-wide health & AI insights" onMenuClick={onMenuClick} />

      <main className="mx-auto max-w-[1400px] space-y-6 px-5 py-6 md:px-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Total Interns" value={internshipHealth.totalInterns} icon={Users} tone="brand" delta={3} />
          <StatCard label="Active Today" value={internshipHealth.activeToday} icon={Activity} tone="up" delta={1} />
          <StatCard label="Placement Ready" value={internshipHealth.placementReady} icon={GraduationCap} tone="up" delta={22} />
          <StatCard label="At-Risk Interns" value={internshipHealth.atRisk} icon={AlertTriangle} tone="down" delta={-8} />
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="glass-panel rounded-2xl p-5 shadow-card xl:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-sm font-semibold text-ink">Technology-wise Performance</h3>
              <span className="text-xs text-ink-faint">Completion vs Avg Score</span>
            </div>
            <TechnologyBarChart data={technologyPerformance} />
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <div className="mb-4 flex items-center gap-2">
              <Sparkles size={15} className="text-cyan" />
              <h3 className="font-display text-sm font-semibold text-ink">AI Insights</h3>
            </div>
            <div className="space-y-3">
              {aiInsights.map((insight) => (
                <div key={insight.id} className={`rounded-xl border px-3.5 py-3 text-xs leading-relaxed ${insightTone[insight.tone]}`}>
                  {insight.text}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Batch Comparison</h3>
            <div className="space-y-3">
              {batchComparison.map((batch) => (
                <div key={batch.batch} className="flex items-center gap-3">
                  <span className="w-16 shrink-0 text-xs font-medium text-ink-muted">{batch.batch}</span>
                  <div className="h-2.5 flex-1 rounded-full bg-base-700">
                    <div
                      className="h-2.5 rounded-full bg-gradient-to-r from-brand-500 to-cyan"
                      style={{ width: `${batch.avgScore}%` }}
                    />
                  </div>
                  <span className="w-10 shrink-0 text-right font-mono text-xs text-ink">{batch.avgScore}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Productivity Trends</h3>
            <TaskReviewChart data={weeklyEngineeringReport} height={200} />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <InternTable data={readyForHiring.length ? readyForHiring : interns} title="Placement Readiness" />
          </div>
          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Mentor Team Performance</h3>
            <div className="space-y-3">
              {mentors.map((m) => (
                <div key={m.id} className="flex items-center justify-between rounded-xl border border-line bg-base-800/50 px-3.5 py-3">
                  <div>
                    <p className="text-sm font-medium text-ink">{m.name}</p>
                    <p className="text-[11px] text-ink-faint">{m.technology} · {m.interns} interns</p>
                  </div>
                  <div className="flex items-center gap-1 font-mono text-sm font-semibold text-brand-300">
                    <TrendingUp size={13} />
                    {m.teamScore}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
