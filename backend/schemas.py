from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Any
from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl
)

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


class ProductivityPeriodData(BaseModel):
    period_start: str
    period_end: str
    average_attendance: float
    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int
    project_approval_percentage: float
    average_engineering_score: float


class ProductivityTrendsResponse(BaseModel):
    previous_period: ProductivityPeriodData
    current_period: ProductivityPeriodData

    attendance_change: float
    project_submission_change: int
    approved_project_change: int
    engineering_score_change: float

    attendance_trend: str
    project_trend: str
    approval_trend: str
    engineering_trend: str

    overall_productivity_status: str
    ai_summary: str
    recommendations: list[str]

class InternshipHealthMetrics(BaseModel):
    total_interns: int
    active_interns: int
    inactive_interns: int

    average_engineering_score: float
    average_attendance: float

    total_projects: int
    approved_projects: int
    pending_projects: int
    rejected_projects: int

    project_approval_percentage: float
    students_requiring_attention: int
    placement_ready_interns: int


class InternshipHealthResponse(BaseModel):
    health_score: float
    health_status: str

    metrics: InternshipHealthMetrics

    ai_summary: str
    recommendations: list[str]


class BatchPerformanceItem(BaseModel):
    batch: str

    total_students: int

    average_engineering_score: float

    average_attendance: float

    total_projects: int

    approved_projects: int

    pending_projects: int

    rejected_projects: int

    project_approval_percentage: float

    placement_ready_students: int

    performance_status: str


class BatchComparisonResponse(BaseModel):

    total_batches: int

    strongest_batch: str | None

    weakest_batch: str | None

    highest_attendance_batch: str | None

    highest_project_batch: str | None

    highest_placement_batch: str | None

    batches: list[BatchPerformanceItem]

    ai_summary: str

    recommendations: list[str]



class PlacementReadinessStudent(BaseModel):
    student_id: int
    student_name: str

    engineering_score: int

    attendance_percentage: float

    approved_projects: int

    placement_status: str

    recommended_action: str


class PlacementSummary(BaseModel):
    job_ready: int
    interview_ready: int
    client_ready: int
    needs_improvement: int


class PlacementReadinessResponse(BaseModel):
    summary: PlacementSummary

    students: list[
        PlacementReadinessStudent
    ]

    ai_summary: str

    recommendations: list[str]


class AdminInsightItem(BaseModel):
    title: str
    description: str
    category: str
    priority: str


class AdminInsightsResponse(BaseModel):
    total_insights: int
    overall_status: str
    insights: list[AdminInsightItem]
    executive_summary: str
    recommended_actions: list[str]

class IntelligenceQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=500
    )

class IntelligenceQueryResponse(BaseModel):
    question: str
    intent: str
    answer: str
    confidence_score: float
    data: Any | None = None
    routing_method: str | None = None


class GitHubReportRequest(BaseModel):
    repository_limit: int = Field(
        default=5,
        ge=1,
        le=10
    )

    ai_repository_limit: int = Field(
        default=2,
        ge=1,
        le=5
    )

    commit_limit: int = Field(
        default=30,
        ge=1,
        le=100
    )

    max_files_per_repository: int = Field(
        default=8,
        ge=1,
        le=20
    )


class GitHubReportResponse(BaseModel):
    student_id: int
    student_name: str
    github_username: str
    saved_report_id: int
    report: dict[str, Any]

class GitHubSavedReportResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    student_id: int
    github_username: str

    profile_score: float
    activity_score: float
    repository_quality_score: float
    documentation_score: float
    testing_score: float
    ai_code_quality_score: float
    final_github_score: float

    performance_level: str
    assessment_status: str

    repositories_analyzed: int
    repositories_with_ai_review: int

    best_repository_name: str | None = None

    generated_at: datetime


class GitHubSavedReportDetailResponse(
    GitHubSavedReportResponse
):
    report_json: dict[str, Any]


class GitHubReportHistoryResponse(BaseModel):
    student_id: int
    student_name: str
    github_username: str
    total_reports: int
    reports: list[GitHubSavedReportResponse]


class GitHubRankingItem(BaseModel):
    rank: int
    report_id: int
    student_id: int
    student_name: str
    github_username: str

    final_github_score: float
    ai_code_quality_score: float
    activity_score: float

    performance_level: str
    best_repository_name: str | None = None
    generated_at: datetime


class GitHubRankingResponse(BaseModel):
    total_students: int
    rankings: list[GitHubRankingItem]


class GitHubReportRequest(BaseModel):
    repository_limit: int = Field(
        default=5,
        ge=1,
        le=10
    )

    ai_repository_limit: int = Field(
        default=2,
        ge=1,
        le=5
    )

    commit_limit: int = Field(
        default=30,
        ge=1,
        le=100
    )

    max_files_per_repository: int = Field(
        default=8,
        ge=1,
        le=20
    )


class GitHubReportResponse(BaseModel):
    student_id: int
    student_name: str
    github_username: str
    saved_report_id: int
    report: dict[str, Any]


class GitHubSavedReportResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    student_id: int
    github_username: str

    profile_score: float
    activity_score: float
    repository_quality_score: float
    documentation_score: float
    testing_score: float
    ai_code_quality_score: float
    final_github_score: float

    performance_level: str
    assessment_status: str

    repositories_analyzed: int
    repositories_with_ai_review: int

    best_repository_name: str | None = None
    generated_at: datetime


class GitHubSavedReportDetailResponse(
    GitHubSavedReportResponse
):
    report_json: dict[str, Any]


class GitHubReportHistoryResponse(BaseModel):
    student_id: int
    student_name: str
    github_username: str
    total_reports: int
    reports: list[GitHubSavedReportResponse]


class GitHubRankingItem(BaseModel):
    rank: int
    report_id: int
    student_id: int
    student_name: str
    github_username: str

    final_github_score: float
    ai_code_quality_score: float
    activity_score: float

    performance_level: str
    best_repository_name: str | None = None
    generated_at: datetime


class GitHubRankingResponse(BaseModel):
    total_students: int
    rankings: list[GitHubRankingItem]


class DailyActivityCreate(BaseModel):
    activity_date: date = Field(
        default_factory=date.today
    )

    task_title: str = Field(
        ...,
        min_length=3,
        max_length=200
    )

    work_summary: str = Field(
        ...,
        min_length=10,
        max_length=2000
    )

    hours_worked: float = Field(
        ...,
        ge=0,
        le=24
    )

    task_status: Literal[
        "Not Started",
        "In Progress",
        "Completed",
        "Blocked"
    ] = "In Progress"

    repository_url: str | None = Field(
        default=None,
        max_length=500
    )

    commit_url: str | None = Field(
        default=None,
        max_length=500
    )

    blockers: str | None = Field(
        default=None,
        max_length=1000
    )

    learning_outcome: str | None = Field(
        default=None,
        max_length=1500
    )


class DailyActivityUpdate(BaseModel):
    task_title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200
    )

    work_summary: str | None = Field(
        default=None,
        min_length=10,
        max_length=2000
    )

    hours_worked: float | None = Field(
        default=None,
        ge=0,
        le=24
    )

    task_status: Literal[
        "Not Started",
        "In Progress",
        "Completed",
        "Blocked"
    ] | None = None

    repository_url: str | None = Field(
        default=None,
        max_length=500
    )

    commit_url: str | None = Field(
        default=None,
        max_length=500
    )

    blockers: str | None = Field(
        default=None,
        max_length=1000
    )

    learning_outcome: str | None = Field(
        default=None,
        max_length=1500
    )


class DailyActivityVerificationRequest(BaseModel):
    verification_status: Literal[
        "Verified",
        "Rejected"
    ]

    mentor_feedback: str | None = Field(
        default=None,
        max_length=1500
    )


class DailyActivityResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    student_id: int
    activity_date: date

    task_title: str
    work_summary: str
    hours_worked: float
    task_status: str

    repository_url: str | None = None
    commit_url: str | None = None
    blockers: str | None = None
    learning_outcome: str | None = None

    submitted_at: datetime
    updated_at: datetime

    verification_status: str
    mentor_id: int | None = None
    mentor_feedback: str | None = None
    is_verified: bool
    verified_at: datetime | None = None


class DailyActivityListResponse(BaseModel):
    total_records: int
    activities: list[DailyActivityResponse]


class InactiveStudentItem(BaseModel):
    student_id: int
    student_name: str
    email: str
    batch: str | None = None
    mentor_id: int | None = None

    last_activity_date: date | None = None
    days_inactive: int | None = None
    activity_status: str


class InactiveStudentsResponse(BaseModel):
    inactivity_threshold_days: int
    total_students: int
    inactive_students_count: int
    inactive_students: list[InactiveStudentItem]


class DailyActivitySummaryResponse(BaseModel):
    period_days: int

    total_students: int
    students_with_activity: int
    students_without_activity: int

    total_activity_records: int
    verified_records: int
    pending_records: int
    rejected_records: int

    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int

    total_hours_worked: float
    average_hours_per_record: float
    activity_submission_rate: float


class TaskCreate(BaseModel):
    student_id: int = Field(
        ...,
        ge=1
    )

    title: str = Field(
        ...,
        min_length=3,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000
    )

    difficulty_level: Literal[
        "Easy",
        "Medium",
        "Advanced"
    ] = "Medium"

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ] = "Medium"

    start_date: date
    due_date: date

    @model_validator(mode="after")
    def validate_task_dates(self):
        if self.due_date < self.start_date:
            raise ValueError(
                "Due date cannot be earlier than start date."
            )

        return self


class TaskProgressUpdate(BaseModel):
    progress_percentage: float = Field(
        ...,
        ge=0,
        le=100
    )

    status: Literal[
        "In Progress",
        "Blocked"
    ]

    blockers: str | None = Field(
        default=None,
        max_length=2000
    )


class TaskSubmissionRequest(BaseModel):
    github_repository_url: str = Field(
        ...,
        min_length=10,
        max_length=500
    )

    github_commit_url: str | None = Field(
        default=None,
        max_length=500
    )

    submission_notes: str = Field(
        ...,
        min_length=10,
        max_length=3000
    )


class TaskReviewRequest(BaseModel):
    decision: Literal[
        "Approved",
        "Rejected"
    ]

    completion_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    mentor_feedback: str = Field(
        ...,
        min_length=5,
        max_length=3000
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    description: str

    student_id: int
    assigned_by_mentor_id: int | None = None

    difficulty_level: str
    priority: str
    status: str

    progress_percentage: float

    assigned_at: datetime
    start_date: date
    due_date: date

    started_at: datetime | None = None
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    reviewed_at: datetime | None = None

    github_repository_url: str | None = None
    github_commit_url: str | None = None
    submission_notes: str | None = None

    blockers: str | None = None
    mentor_feedback: str | None = None
    completion_score: float | None = None

    deadline_status: str
    days_late: int


class TaskListResponse(BaseModel):
    total_records: int
    tasks: list[TaskResponse]


class OverdueTaskItem(BaseModel):
    task_id: int
    title: str

    student_id: int
    student_name: str
    mentor_id: int | None = None

    due_date: date
    status: str
    progress_percentage: float

    days_overdue: int
    difficulty_level: str
    priority: str


class OverdueTasksResponse(BaseModel):
    total_overdue_tasks: int
    overdue_tasks: list[OverdueTaskItem]


class TaskSummaryResponse(BaseModel):
    period_days: int
    total_tasks: int

    assigned_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    submitted_tasks: int
    approved_tasks: int
    rejected_tasks: int
    overdue_tasks: int

    on_time_completions: int
    late_completions: int

    average_completion_score: float
    average_progress_percentage: float

    task_completion_rate: float
    deadline_compliance_rate: float

class CaseStudyCreate(BaseModel):
    student_id: int = Field(
        ...,
        ge=1
    )

    title: str = Field(
        ...,
        min_length=3,
        max_length=250
    )

    description: str = Field(
        ...,
        min_length=20,
        max_length=10000
    )

    objectives: str = Field(
        ...,
        min_length=10,
        max_length=5000
    )

    requirements: str | None = Field(
        default=None,
        max_length=10000
    )

    technology: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    difficulty_level: Literal[
        "Easy",
        "Medium",
        "Advanced"
    ] = "Medium"

    start_date: date
    due_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.due_date < self.start_date:
            raise ValueError(
                "Due date cannot be earlier than start date."
            )

        return self


class CaseStudyProgressUpdate(BaseModel):
    progress_percentage: float = Field(
        ...,
        ge=0,
        le=100
    )

    student_blockers: str | None = Field(
        default=None,
        max_length=3000
    )

    learning_outcome: str | None = Field(
        default=None,
        max_length=3000
    )


class CaseStudySubmissionRequest(BaseModel):
    github_repository_url: str = Field(
        ...,
        min_length=10,
        max_length=500
    )

    live_demo_url: str | None = Field(
        default=None,
        max_length=500
    )

    documentation_url: str | None = Field(
        default=None,
        max_length=500
    )

    submission_notes: str = Field(
        ...,
        min_length=10,
        max_length=5000
    )

    learning_outcome: str | None = Field(
        default=None,
        max_length=3000
    )


class CaseStudyEvaluationRequest(BaseModel):
    decision: Literal[
        "Approved",
        "Revision Required",
        "Failed"
    ]

    technical_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    code_quality_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    documentation_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    problem_solving_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    presentation_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    mentor_feedback: str = Field(
        ...,
        min_length=5,
        max_length=5000
    )

    strengths: str | None = Field(
        default=None,
        max_length=3000
    )

    weak_areas: str | None = Field(
        default=None,
        max_length=3000
    )

    revision_instructions: str | None = Field(
        default=None,
        max_length=5000
    )

    @model_validator(mode="after")
    def validate_revision_instructions(self):
        if (
            self.decision == "Revision Required"
            and not self.revision_instructions
        ):
            raise ValueError(
                "Revision instructions are required "
                "when revision is requested."
            )

        return self


class CaseStudyResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    description: str
    objectives: str
    requirements: str | None = None

    technology: str
    category: str
    difficulty_level: str

    student_id: int
    assigned_by_mentor_id: int | None = None

    status: str
    progress_percentage: float

    assigned_at: datetime
    start_date: date
    due_date: date

    started_at: datetime | None = None
    submitted_at: datetime | None = None
    evaluated_at: datetime | None = None
    completed_at: datetime | None = None

    github_repository_url: str | None = None
    live_demo_url: str | None = None
    documentation_url: str | None = None

    submission_notes: str | None = None
    student_blockers: str | None = None
    learning_outcome: str | None = None

    technical_score: float | None = None
    code_quality_score: float | None = None
    documentation_score: float | None = None
    problem_solving_score: float | None = None
    presentation_score: float | None = None

    final_score: float | None = None
    performance_level: str | None = None

    mentor_feedback: str | None = None
    strengths: str | None = None
    weak_areas: str | None = None
    revision_instructions: str | None = None

    revision_count: int

    deadline_status: str
    days_late: int


class CaseStudyListResponse(BaseModel):
    total_records: int
    case_studies: list[CaseStudyResponse]


class CaseStudyRankingItem(BaseModel):
    rank: int
    case_study_id: int

    student_id: int
    student_name: str

    title: str
    technology: str
    difficulty_level: str

    final_score: float
    performance_level: str

    deadline_status: str
    revision_count: int


class CaseStudyRankingResponse(BaseModel):
    total_students: int
    rankings: list[CaseStudyRankingItem]


class CaseStudySummaryResponse(BaseModel):
    period_days: int

    total_case_studies: int
    assigned_case_studies: int
    in_progress_case_studies: int
    submitted_case_studies: int
    revision_required_case_studies: int
    approved_case_studies: int
    failed_case_studies: int
    overdue_case_studies: int

    easy_case_studies: int
    medium_case_studies: int
    advanced_case_studies: int

    on_time_submissions: int
    late_submissions: int

    average_final_score: float
    approval_rate: float
    failure_rate: float
    deadline_compliance_rate: float


class CaseStudyRecommendationItem(BaseModel):
    student_id: int
    student_name: str

    completed_case_studies: int
    average_score: float
    average_revision_count: float

    current_recommended_level: str
    recommendation: str
    reason: str


class CaseStudyRecommendationsResponse(BaseModel):
    total_students: int
    recommendations: list[
        CaseStudyRecommendationItem
    ]

class MentorFeedbackCreate(BaseModel):
    student_id: int = Field(
        ...,
        ge=1
    )

    review_date: date = Field(
        default_factory=date.today
    )

    review_period: Literal[
        "Weekly",
        "Monthly",
        "Final"
    ] = "Weekly"

    technical_skill_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    problem_solving_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    consistency_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    learning_attitude_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    leadership_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    communication_clarity_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    responsiveness_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    professionalism_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    collaboration_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    meeting_participation_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    strengths: str | None = Field(
        default=None,
        max_length=3000
    )

    weak_areas: str | None = Field(
        default=None,
        max_length=3000
    )

    improvement_plan: str | None = Field(
        default=None,
        max_length=4000
    )

    general_feedback: str = Field(
        ...,
        min_length=5,
        max_length=5000
    )


class MentorFeedbackUpdate(BaseModel):
    technical_skill_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    problem_solving_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    consistency_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    learning_attitude_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    leadership_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    communication_clarity_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    responsiveness_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    professionalism_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    collaboration_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    meeting_participation_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    strengths: str | None = Field(
        default=None,
        max_length=3000
    )

    weak_areas: str | None = Field(
        default=None,
        max_length=3000
    )

    improvement_plan: str | None = Field(
        default=None,
        max_length=4000
    )

    general_feedback: str | None = Field(
        default=None,
        min_length=5,
        max_length=5000
    )


class MentorFeedbackResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    student_id: int
    mentor_id: int

    review_date: date
    review_period: str

    technical_skill_score: float
    problem_solving_score: float
    consistency_score: float
    learning_attitude_score: float
    leadership_score: float

    communication_clarity_score: float
    responsiveness_score: float
    professionalism_score: float
    collaboration_score: float
    meeting_participation_score: float

    communication_score: float
    overall_feedback_score: float

    performance_level: str
    communication_level: str

    strengths: str | None = None
    weak_areas: str | None = None
    improvement_plan: str | None = None
    general_feedback: str

    leadership_potential: str
    requires_mentor_meeting: bool

    created_at: datetime
    updated_at: datetime


class MentorFeedbackListResponse(BaseModel):
    total_records: int
    feedback_records: list[
        MentorFeedbackResponse
    ]


class CommunicationRankingItem(BaseModel):
    rank: int
    student_id: int
    student_name: str
    mentor_id: int

    communication_score: float
    communication_level: str

    leadership_score: float
    leadership_potential: str

    overall_feedback_score: float
    review_date: date


class CommunicationRankingResponse(BaseModel):
    total_students: int
    rankings: list[
        CommunicationRankingItem
    ]


class WeakCommunicationItem(BaseModel):
    student_id: int
    student_name: str
    mentor_id: int

    communication_score: float
    communication_level: str

    weak_areas: str | None = None
    improvement_plan: str | None = None

    requires_mentor_meeting: bool
    review_date: date


class WeakCommunicationResponse(BaseModel):
    score_threshold: float
    total_students: int
    students: list[
        WeakCommunicationItem
    ]


class LeadershipPotentialItem(BaseModel):
    student_id: int
    student_name: str
    mentor_id: int

    leadership_score: float
    leadership_potential: str

    communication_score: float
    overall_feedback_score: float

    review_date: date


class LeadershipPotentialResponse(BaseModel):
    total_students: int
    students: list[
        LeadershipPotentialItem
    ]


class MentorFeedbackSummaryResponse(BaseModel):
    period_days: int

    total_feedback_records: int
    students_reviewed: int
    mentors_participated: int

    excellent_performers: int
    good_performers: int
    average_performers: int
    weak_performers: int

    strong_communicators: int
    weak_communicators: int

    high_leadership_potential: int
    mentor_meetings_required: int

    average_technical_score: float
    average_communication_score: float
    average_leadership_score: float
    average_overall_feedback_score: float