from pydantic import BaseModel
from datetime import date

class StudentRegistration(BaseModel):
    name: str
    email: str
    password: str
    github_username: str
    phone_number: str
    batch: str
    gender: str

class MentorRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    department: str
    gender: str

class AdminRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    gender: str

class CEORegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    gender: str
    phone_number: str

class StudentLogin(BaseModel):
    email: str
    password: str

class MentorLogin(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

class CEOLogin(BaseModel):
    email: str
    password: str

from datetime import date, datetime


class AttendanceCheckIn(BaseModel):
    mentor_id: int


class AttendanceCheckOut(BaseModel):
    pass


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    mentor_id: int
    date: date
    status: str
    checked_in_time: datetime | None
    checked_out_time: datetime | None

    class Config:
        from_attributes = True

class LeaveApplication(BaseModel):
    reason: str
    leave_date: date

class ProjectSubmission(BaseModel):
    title: str
    description: str
    github_link: str
    tech_stack: str

class ProjectReview(BaseModel):
    remarks: str

# AI Chat

class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str

from pydantic import BaseModel


class AIDashboardResponse(BaseModel):
    engineering_score: int
    skill_growth: str
    weak_areas: list[str]
    recommendations: list[str]
    next_case_study: str

class AIDashboardResponse(BaseModel):
    engineering_score: int
    skill_growth: str
    weak_areas: list[str]
    recommendations: list[str]
    next_case_study: str

class ScoreBreakdown(BaseModel):
    attendance: int
    projects: int
    discipline: int


class AIDashboardResponse(BaseModel):
    engineering_score: int
    score_breakdown: ScoreBreakdown
    skill_growth: str
    weak_areas: list[str]
    recommendations: list[str]
    next_case_study: str

class RoadmapWeek(BaseModel):
    week: int
    topic: str
    goal: str


class AIRoadmapResponse(BaseModel):
    current_level: str
    estimated_completion: str
    roadmap: list[RoadmapWeek]

from typing import List
from pydantic import BaseModel


class StudentPerformanceSummary(BaseModel):
    student_id: int
    student_name: str
    engineering_score: int
    attendance_percentage: float
    total_projects: int
    approved_projects: int
    rejected_projects: int
    performance_level: str


class MentorTeamAnalytics(BaseModel):
    total_students: int
    average_engineering_score: float
    average_attendance: float
    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int
    students_requiring_attention: int


class MentorRecommendation(BaseModel):
    student_id: int
    student_name: str
    recommendation: str
    priority: str


class StudentEngineeringGrowth(BaseModel):
    student_id: int
    student_name: str
    engineering_score: int

    attendance_score: int
    project_score: int
    discipline_score: int

    attendance_percentage: float
    project_completion_percentage: float

    current_level: str
    growth_status: str


class MentorDashboardResponse(BaseModel):
    team_analytics: MentorTeamAnalytics
    top_performers: List[StudentPerformanceSummary]
    weak_performers: List[StudentPerformanceSummary]
    ai_recommendations: List[MentorRecommendation]

from pydantic import BaseModel


class AdminTopInternResponse(BaseModel):
    rank: int
    student_id: int
    student_name: str
    attendance_percentage: float
    total_projects: int
    approved_projects: int
    project_approval_percentage: float
    readiness_score: float


class AdminTopInternListResponse(BaseModel):
    top_interns: list[AdminTopInternResponse]



class AdminRecommendationItem(BaseModel):
    type: str
    reason: str
    priority: str


class AdminInternRecommendation(BaseModel):
    student_id: int
    student_name: str
    readiness_score: float
    attendance_percentage: float
    approved_projects: int
    recommendations: list[AdminRecommendationItem]


class AdminRecommendationListResponse(BaseModel):
    interns: list[AdminInternRecommendation]

class WeeklyPerformerItem(BaseModel):
    student_id: int
    student_name: str
    engineering_score: float
    attendance_percentage: float
    approved_projects: int


class WeeklyEngineeringReportResponse(BaseModel):
    period_start: str
    period_end: str

    total_interns: int
    average_engineering_score: float
    average_attendance: float

    total_projects_submitted: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int

    top_performers: list[WeeklyPerformerItem]
    interns_requiring_attention: list[WeeklyPerformerItem]

    productivity_level: str
    ai_summary: str
    recommendations: list[str]

class MonthlyPeriodPerformance(BaseModel):
    period_start: str
    period_end: str
    average_engineering_score: float
    average_attendance: float
    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int


class MonthlyGrowthReportResponse(BaseModel):
    previous_period: MonthlyPeriodPerformance
    current_period: MonthlyPeriodPerformance

    engineering_score_growth: float
    attendance_growth: float
    project_growth: int
    approved_project_growth: int

    growth_status: str
    ai_summary: str
    recommendations: list[str]


class MentorStudentSummary(BaseModel):
    student_id: int
    student_name: str
    engineering_score: int
    attendance_percentage: float
    approved_projects: int


class MentorSummaryItem(BaseModel):
    mentor_id: int
    mentor_name: str
    department: str | None

    total_assigned_students: int
    average_engineering_score: float
    average_attendance: float

    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int

    students_requiring_attention: int

    top_performer: MentorStudentSummary | None
    weak_performer: MentorStudentSummary | None

    performance_status: str
    ai_summary: str
    recommendations: list[str]


class MentorSummaryReportResponse(BaseModel):
    total_mentors: int
    mentors: list[MentorSummaryItem]


class TeamPerformanceItem(BaseModel):
    team_name: str
    total_students: int

    average_engineering_score: float
    average_attendance: float

    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int

    project_approval_percentage: float
    students_requiring_attention: int

    top_performer: MentorStudentSummary | None
    performance_status: str


class TeamPerformanceReportResponse(BaseModel):
    total_teams: int
    total_students: int

    overall_average_engineering_score: float
    overall_average_attendance: float

    strongest_team: str | None
    weakest_team: str | None

    teams: list[TeamPerformanceItem]

    ai_summary: str
    recommendations: list[str]


class TechnologyPerformanceItem(BaseModel):
    technology: str
    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int
    approval_percentage: float
    performance_status: str


class TechnologyPerformanceReportResponse(BaseModel):
    total_technologies: int
    total_projects_analyzed: int

    strongest_technology: str | None
    weakest_technology: str | None

    technologies: list[TechnologyPerformanceItem]

    ai_summary: str
    recommendations: list[str]