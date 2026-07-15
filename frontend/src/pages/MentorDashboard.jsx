import Topbar from '../components/Topbar'
import StatCard from '../components/StatCard'
import InternTable from '../components/InternTable'
import ScoreRing from '../components/ScoreRing'
import RecommendationBadge from '../components/RecommendationBadge'
import { EngineeringTrendChart } from '../components/Charts'
import { interns, weeklyEngineeringReport } from '../data/mockData'
import { Users, TrendingUp, AlertTriangle, Award } from 'lucide-react'

export default function MentorDashboard({ onMenuClick }) {
  const sorted = [...interns].sort((a, b) => b.engineeringScore - a.engineeringScore)
  const topPerformers = sorted.slice(0, 3)
  const weakPerformers = [...interns].sort((a, b) => a.engineeringScore - b.engineeringScore).slice(0, 3)
  const atRisk = interns.filter((i) => i.status === 'at_risk')

  return (
    <div className="flex-1 min-w-0">
      <Topbar title="Mentor Dashboard" subtitle="Hassan Raza · Artificial Intelligence Track" onMenuClick={onMenuClick} />

      <main className="mx-auto max-w-[1400px] space-y-6 px-5 py-6 md:px-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Team Size" value="8" icon={Users} tone="brand" delta={0} />
          <StatCard label="Avg Engineering Score" value="79" icon={TrendingUp} tone="up" delta={4} />
          <StatCard label="At-Risk Interns" value={atRisk.length} icon={AlertTriangle} tone="down" delta={-2} />
          <StatCard label="Ready for Placement" value="2" icon={Award} tone="up" delta={12} />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="glass-panel rounded-2xl p-5 shadow-card lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-sm font-semibold text-ink">Engineering Growth — Team Average</h3>
              <span className="rounded-full border border-brand-700/40 bg-brand-900/30 px-2.5 py-1 text-[11px] font-medium text-brand-300">Last 6 weeks</span>
            </div>
            <EngineeringTrendChart data={weeklyEngineeringReport} />
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Top Performers</h3>
            <div className="space-y-4">
              {topPerformers.map((intern, i) => (
                <div key={intern.id} className="flex items-center justify-between gap-3">
                  <ScoreRing value={intern.engineeringScore} size={48} stroke={5} label={intern.name} sub={intern.id} />
                  <span className="font-display text-xs font-bold text-ink-faint">#{i + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <InternTable data={sorted} title="AI Recommendations — Your Team" />
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Weak Performers — Needs Attention</h3>
            <div className="space-y-3">
              {weakPerformers.map((intern) => (
                <div key={intern.id} className="rounded-xl border border-line bg-base-800/50 p-3.5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-ink">{intern.name}</p>
                      <p className="eef-id text-[11px] text-ink-faint">{intern.id} · {intern.technology}</p>
                    </div>
                    <ScoreRing value={intern.engineeringScore} size={40} stroke={4} />
                  </div>
                  <div className="mt-3">
                    <RecommendationBadge type={intern.recommendation} />
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
