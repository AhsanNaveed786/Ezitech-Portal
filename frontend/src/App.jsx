import { useState } from 'react'
import { HashRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import MentorDashboard from './pages/MentorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import StudentDashboard from './pages/StudentDashboard'
import { LayoutGrid, ShieldCheck, GraduationCap, Cpu, X } from 'lucide-react'

const mobileNav = [
  { to: '/mentor', label: 'Mentor', icon: LayoutGrid },
  { to: '/admin', label: 'Admin', icon: ShieldCheck },
  { to: '/student', label: 'Student', icon: GraduationCap },
]

function MobileDrawer({ open, onClose }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 md:hidden">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute left-0 top-0 h-full w-72 bg-base-900 border-r border-line p-5">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-cyan">
              <Cpu size={16} className="text-base-950" />
            </div>
            <p className="font-display text-sm font-bold text-ink">AI-MIEDP</p>
          </div>
          <button onClick={onClose} className="text-ink-muted"><X size={18} /></button>
        </div>
        <nav className="space-y-1">
          {mobileNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm ${isActive ? 'bg-brand-800/50 text-ink border border-brand-700/40' : 'text-ink-muted'}`
              }
            >
              <item.icon size={16} />
              {item.label} Dashboard
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  )
}

export default function App() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <HashRouter>
      <div className="flex min-h-screen bg-base-950">
        <Sidebar />
        <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
        <Routes>
          <Route path="/" element={<Navigate to="/mentor" replace />} />
          <Route path="/mentor" element={<MentorDashboard onMenuClick={() => setDrawerOpen(true)} />} />
          <Route path="/admin" element={<AdminDashboard onMenuClick={() => setDrawerOpen(true)} />} />
          <Route path="/student" element={<StudentDashboard onMenuClick={() => setDrawerOpen(true)} />} />
        </Routes>
      </div>
    </HashRouter>
  )
}
