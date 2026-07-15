// Mock data layer for AI-MIEDP frontend.
// In production this is served by the FastAPI + PostgreSQL backend (see /docs/api-contract.md).

export const technologies = [
  'Laravel', 'MERN Stack', 'Artificial Intelligence', 'Flutter', 'UI/UX', 'DevOps', 'Data Science',
]

export const mentors = [
  { id: 'MNT-01', name: 'Hassan Raza', technology: 'Artificial Intelligence', teamScore: 91, interns: 8 },
  { id: 'MNT-02', name: 'Ayesha Khan', technology: 'MERN Stack', teamScore: 84, interns: 10 },
  { id: 'MNT-03', name: 'Bilal Ahmed', technology: 'Laravel', teamScore: 78, interns: 9 },
  { id: 'MNT-04', name: 'Sana Tariq', technology: 'DevOps', teamScore: 88, interns: 6 },
  { id: 'MNT-05', name: 'Usman Farooq', technology: 'Flutter', teamScore: 73, interns: 7 },
]

export const recommendationTypes = {
  PROMOTE: { label: 'Promote Intern', tone: 'up' },
  ADVANCED: { label: 'Assign Advanced Case Study', tone: 'up' },
  EASIER: { label: 'Assign Easier Case Study', tone: 'warn' },
  MEETING: { label: 'Schedule Mentor Meeting', tone: 'warn' },
  INTERVIEW: { label: 'Recommend Interview', tone: 'up' },
  PLACEMENT: { label: 'Recommend Job Placement', tone: 'up' },
  EXTENSION: { label: 'Recommend Internship Extension', tone: 'idle' },
  CERTIFICATE: { label: 'Recommend Certificate Eligibility', tone: 'up' },
  AT_RISK: { label: 'At-Risk — Needs Support', tone: 'down' },
}

export const interns = [
  {
    id: 'EEF-014', name: 'Zainab Emaan', technology: 'Artificial Intelligence', mentor: 'Hassan Raza',
    engineeringScore: 94, attendance: 97, github: 91, dailyActivity: 88, taskCompletion: 96,
    codeReview: 92, caseStudyAvg: 95, mentorFeedback: 93, communication: 90, engineeringCredits: 410,
    learningSpeed: 'Fast', deadlineCompliance: 98, status: 'active', trend: 'up',
    recommendation: 'PLACEMENT', weeklyTrend: [78, 82, 85, 88, 91, 94],
  },
  {
    id: 'EEF-021', name: 'Ahmed Raza', technology: 'MERN Stack', mentor: 'Ayesha Khan',
    engineeringScore: 88, attendance: 90, github: 85, dailyActivity: 82, taskCompletion: 89,
    codeReview: 86, caseStudyAvg: 90, mentorFeedback: 87, communication: 84, engineeringCredits: 360,
    learningSpeed: 'Fast', deadlineCompliance: 92, status: 'active', trend: 'up',
    recommendation: 'ADVANCED', weeklyTrend: [70, 75, 79, 83, 86, 88],
  },
  {
    id: 'EEF-032', name: 'Hira Sheikh', technology: 'UI/UX', mentor: 'Sana Tariq',
    engineeringScore: 82, attendance: 88, github: 74, dailyActivity: 80, taskCompletion: 85,
    codeReview: 79, caseStudyAvg: 83, mentorFeedback: 85, communication: 91, engineeringCredits: 305,
    learningSpeed: 'Average', deadlineCompliance: 87, status: 'active', trend: 'up',
    recommendation: 'CERTIFICATE', weeklyTrend: [68, 71, 74, 77, 80, 82],
  },
  {
    id: 'EEF-045', name: 'Talha Nadeem', technology: 'Laravel', mentor: 'Bilal Ahmed',
    engineeringScore: 54, attendance: 62, github: 40, dailyActivity: 48, taskCompletion: 58,
    codeReview: 51, caseStudyAvg: 55, mentorFeedback: 60, communication: 57, engineeringCredits: 140,
    learningSpeed: 'Slow', deadlineCompliance: 49, status: 'at_risk', trend: 'down',
    recommendation: 'AT_RISK', weeklyTrend: [70, 66, 61, 58, 56, 54],
  },
  {
    id: 'EEF-052', name: 'Mahnoor Ali', technology: 'Data Science', mentor: 'Hassan Raza',
    engineeringScore: 89, attendance: 93, github: 87, dailyActivity: 85, taskCompletion: 90,
    codeReview: 88, caseStudyAvg: 91, mentorFeedback: 89, communication: 86, engineeringCredits: 375,
    learningSpeed: 'Fast', deadlineCompliance: 94, status: 'active', trend: 'up',
    recommendation: 'INTERVIEW', weeklyTrend: [74, 78, 81, 85, 87, 89],
  },
  {
    id: 'EEF-060', name: 'Fahad Iqbal', technology: 'DevOps', mentor: 'Sana Tariq',
    engineeringScore: 67, attendance: 71, github: 63, dailyActivity: 65, taskCompletion: 69,
    codeReview: 62, caseStudyAvg: 68, mentorFeedback: 70, communication: 66, engineeringCredits: 210,
    learningSpeed: 'Average', deadlineCompliance: 64, status: 'watch', trend: 'flat',
    recommendation: 'MEETING', weeklyTrend: [66, 68, 65, 67, 66, 67],
  },
  {
    id: 'EEF-071', name: 'Areeba Younas', technology: 'Flutter', mentor: 'Usman Farooq',
    engineeringScore: 73, attendance: 80, github: 68, dailyActivity: 72, taskCompletion: 76,
    codeReview: 70, caseStudyAvg: 74, mentorFeedback: 75, communication: 78, engineeringCredits: 250,
    learningSpeed: 'Average', deadlineCompliance: 77, status: 'active', trend: 'flat',
    recommendation: 'EASIER', weeklyTrend: [69, 71, 70, 72, 73, 73],
  },
  {
    id: 'EEF-083', name: 'Danish Malik', technology: 'MERN Stack', mentor: 'Ayesha Khan',
    engineeringScore: 45, attendance: 52, github: 38, dailyActivity: 40, taskCompletion: 47,
    codeReview: 42, caseStudyAvg: 46, mentorFeedback: 50, communication: 44, engineeringCredits: 95,
    learningSpeed: 'Slow', deadlineCompliance: 41, status: 'at_risk', trend: 'down',
    recommendation: 'AT_RISK', weeklyTrend: [58, 54, 50, 48, 46, 45],
  },
]

export const technologyPerformance = [
  { technology: 'Artificial Intelligence', completion: 92, avgScore: 90, interns: 8 },
  { technology: 'MERN Stack', completion: 79, avgScore: 74, interns: 10 },
  { technology: 'Laravel', completion: 68, avgScore: 62, interns: 9 },
  { technology: 'Data Science', completion: 88, avgScore: 86, interns: 6 },
  { technology: 'DevOps', completion: 74, avgScore: 71, interns: 6 },
  { technology: 'Flutter', completion: 76, avgScore: 73, interns: 7 },
  { technology: 'UI/UX', completion: 83, avgScore: 80, interns: 5 },
]

export const weeklyEngineeringReport = [
  { week: 'W1', score: 68, tasks: 120, reviews: 44 },
  { week: 'W2', score: 71, tasks: 134, reviews: 51 },
  { week: 'W3', score: 74, tasks: 141, reviews: 58 },
  { week: 'W4', score: 77, tasks: 150, reviews: 63 },
  { week: 'W5', score: 79, tasks: 158, reviews: 69 },
  { week: 'W6', score: 82, tasks: 165, reviews: 74 },
]

export const batchComparison = [
  { batch: 'Batch 11', avgScore: 71, retention: 88 },
  { batch: 'Batch 12', avgScore: 76, retention: 91 },
  { batch: 'Batch 13', avgScore: 74, retention: 85 },
  { batch: 'Batch 14', avgScore: 81, retention: 94 },
]

export const internshipHealth = {
  totalInterns: 51,
  activeToday: 44,
  avgEngineeringScore: 76,
  placementReady: 9,
  atRisk: 6,
  completionRate: 81,
}

export const aiInsights = [
  { id: 1, text: 'Artificial Intelligence track shows the fastest average learning speed this month, 18% above the internship-wide mean.', tone: 'up' },
  { id: 2, text: 'Laravel batch completion rate dropped 6 points week-over-week — deadline compliance is the primary driver.', tone: 'down' },
  { id: 3, text: '9 interns are within range of Job Placement recommendation once code review scores stabilize above 85.', tone: 'up' },
  { id: 4, text: 'Bilal Ahmed\'s team shows the widest score variance across mentors — may benefit from structured pairing.', tone: 'warn' },
]

export const executiveQueries = [
  'Show me the top 10 interns this month',
  'Which mentor needs more support?',
  'How many interns are ready for hiring?',
  'Which technology is underperforming?',
  'Predict internship completion for the next batch',
]
