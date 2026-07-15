# AI-MIEDP Frontend
Ezitech AI Mentor Intelligence & Engineering Decision Platform — Frontend (Case Study AI-012)

Built with **React 18 + Vite + Tailwind CSS + Recharts**. Fully responsive, dark "control room" blue theme, with the three dashboards required by the case study: **Mentor**, **Admin**, and **Student**.

## Run it in VS Code

```bash
npm install
npm run dev
```

Then open the printed local URL (usually `http://localhost:5173`).

To build for production:
```bash
npm run build
npm run preview
```

## Project structure

```
src/
  components/       # Reusable UI: Sidebar, Topbar, ScoreRing, StatCard, InternTable, Charts, RecommendationBadge
  pages/            # MentorDashboard.jsx, AdminDashboard.jsx, StudentDashboard.jsx
  data/mockData.js  # Mock intern/mentor/technology data — replace with FastAPI calls
  App.jsx           # Routing shell (HashRouter — safe for any static host)
  index.css         # Design tokens & global styles
tailwind.config.js  # Full color/typography/shadow token system (the "elite blue" theme)
```

## Design system (token summary)

- **Palette:** deep navy base (`#050912`–`#182541`), electric blue primary (`#2F6FED`/`#4F8EFF`), cyan secondary accent (`#22D3EE`), signal colors for status (green/amber/red).
- **Type:** Sora (display/headings), Inter (body/UI), JetBrains Mono (scores, intern IDs, credits — reinforces the "engineering telemetry" feel).
- **Signature element:** the circular **Engineering Score ring**, used consistently across all three dashboards instead of generic progress bars, tying every screen back to the platform's core scoring concept. Intern IDs are styled like ticket/engineering references (`EEF-014`) for the same reason.
- **Motion:** subtle rise-in on cards, live-pulse indicator on the AI engine status, animated ring fill — kept restrained per the brief.

## Wiring to your FastAPI backend

Every page currently imports from `src/data/mockData.js`. To connect the real backend:

1. Create `src/lib/api.js` with `fetch`/`axios` calls to your FastAPI endpoints (e.g. `GET /api/interns`, `GET /api/mentors`, `GET /api/reports/weekly`).
2. Replace the static imports in each page (`MentorDashboard.jsx`, `AdminDashboard.jsx`, `StudentDashboard.jsx`) with `useEffect` + `useState` data fetching, or React Query if you add it.
3. Keep the shape of the mock objects (see `mockData.js`) as your API contract reference — every field maps directly to a functional requirement in the case study (attendance, github, dailyActivity, taskCompletion, codeReview, caseStudyAvg, mentorFeedback, communication, engineeringCredits, learningSpeed, deadlineCompliance).

## Notes for your case study submission

- This covers the **frontend** deliverable only (Mentor/Admin/Student dashboards + AI recommendation display + report visualizations).
- Backend (FastAPI, LangGraph, PostgreSQL, Redis, ChromaDB, Sentence Transformers) is not included — say the word when you're ready to move to that phase and we'll build it to match this data contract exactly.
- The Bonus Challenge (Executive AI Dashboard with natural-language queries) is not yet built here — happy to add it as a fourth workspace when you get to that stage.
