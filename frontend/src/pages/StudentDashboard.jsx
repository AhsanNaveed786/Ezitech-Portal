import Topbar from '../components/Topbar'
import ScoreRing from '../components/ScoreRing'
import RecommendationBadge from '../components/RecommendationBadge'
import { EngineeringTrendChart, SkillRadarChart } from '../components/Charts'
import { interns } from '../data/mockData'
import { Github, CheckCircle2, MessageSquare, Clock, BookOpen } from 'lucide-react'

const me = interns[0] // Zainab Emaan — EEF-014

const skillData = [
  { skill: 'GitHub', value: me.github },
  { skill: 'Tasks', value: me.taskCompletion },
  { skill: 'Reviews', value: me.codeReview },
  { skill: 'Comm.', value: me.communication },
  { skill: 'Case Studies', value: me.caseStudyAvg },
  { skill: 'Deadlines', value: me.deadlineCompliance },
]

const metrics = [
  { label: 'Attendance', value: me.attendance, icon: Clock },
  { label: 'GitHub Contributions', value: me.github, icon: Github },
  { label: 'Task Completion', value: me.taskCompletion, icon: CheckCircle2 },
  { label: 'Communication', value: me.communication, icon: MessageSquare },
]

export default function StudentDashboard({ onMenuClick }) {
  return (
    <div className="flex-1 min-w-0">
      <Topbar title="Student Dashboard" subtitle={`${me.name} · ${me.technology} Track`} onMenuClick={onMenuClick} />

      <main className="mx-auto max-w-[1400px] space-y-6 px-5 py-6 md:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="glass-panel rounded-2xl p-6 shadow-glow-lg lg:col-span-1">
            <p className="text-xs font-medium uppercase tracking-wider text-ink-faint">Your Engineering Score</p>
            <div className="mt-4 flex justify-center">
              <ScoreRing value={me.engineeringScore} size={150} stroke={11} />
            </div>
            <p className="mt-4 text-center text-sm text-ink-muted">
              You're in the <span className="font-semibold text-signal-up">top 8%</span> of the {me.technology} track.
            </p>
            <div className="mt-4 flex justify-center">
              <RecommendationBadge type={me.recommendation} />
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card lg:col-span-2">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Skill Growth</h3>
            <SkillRadarChart data={skillData} height={230} />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((m) => (
            <div key={m.label} className="glass-panel rounded-2xl p-5 shadow-card">
              <div className="flex items-center gap-2">
                <div className="rounded-lg border border-brand-700/40 bg-brand-900/30 p-2 text-brand-300">
                  <m.icon size={15} />
                </div>
                <p className="text-xs font-medium text-ink-muted">{m.label}</p>
              </div>
              <p className="mt-3 font-display text-2xl font-semibold text-ink">{m.value}%</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="glass-panel rounded-2xl p-5 shadow-card lg:col-span-2">
            <h3 className="mb-4 font-display text-sm font-semibold text-ink">Engineering Growth — 6 Weeks</h3>
            <EngineeringTrendChart data={me.weeklyTrend.map((score, i) => ({ week: `W${i + 1}`, score }))} />
          </div>

          <div className="glass-panel rounded-2xl p-5 shadow-card">
            <div className="mb-4 flex items-center gap-2">
              <BookOpen size={15} className="text-cyan" />
              <h3 className="font-display text-sm font-semibold text-ink">Next Suggested Case Study</h3>
            </div>
            <div className="rounded-xl border border-brand-700/40 bg-brand-900/20 p-4">
              <p className="eef-id text-[11px] text-brand-300">CS-AI-108</p>
              <p className="mt-1 text-sm font-medium text-ink">Multi-Agent RAG Pipeline with Guardrails</p>
              <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                Matched to your fast learning speed and strong case-study average. Difficulty: Advanced.
              </p>
            </div>
            <div className="mt-4">
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-ink-faint">Weak Areas</p>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full border border-signal-warn/25 bg-signal-warn/10 px-2.5 py-1 text-xs text-signal-warn">Daily Activity Consistency</span>
                <span className="rounded-full border border-signal-warn/25 bg-signal-warn/10 px-2.5 py-1 text-xs text-signal-warn">Communication Cadence</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
