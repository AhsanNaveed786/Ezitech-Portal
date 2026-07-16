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