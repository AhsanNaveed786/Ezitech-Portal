from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.schemas import (
    MentorSummaryReportResponse
)

from backend.schemas import (
    TeamPerformanceReportResponse
)

from backend.services.ai import (
    get_team_performance_report
)


from backend.services.ai import (
    get_mentor_summary_report
)

from backend.schemas import AdminRecommendationListResponse

from backend.services.ai import get_admin_ai_recommendations
from backend.schemas import (
    MonthlyGrowthReportResponse
)

from backend.services.ai import (
    get_monthly_growth_report
)
from backend.database import get_db
from backend.models import Mentor

from backend.schemas import WeeklyEngineeringReportResponse

from backend.services.ai import (
    get_weekly_engineering_report
)

from backend.schemas import (
    MentorDashboardResponse,
    MentorTeamAnalytics,
    MentorRecommendation,
    StudentPerformanceSummary,
    StudentEngineeringGrowth
)

from backend.services.ai import (
    get_complete_mentor_ai_dashboard,
    get_mentor_top_performers,
    get_mentor_weak_performers,
    get_mentor_team_analytics,
    get_mentor_ai_recommendations,
    get_student_engineering_growth
)

from utils.dependencies import get_current_mentor


from backend.models import Student
from backend.schemas import (
    AIChatRequest,
    AIChatResponse,
    AIDashboardResponse,
    AIRoadmapResponse
)
from backend.services.ai import (
    ai_chat,
    ai_dashboard_summary,
    ai_learning_roadmap
)
from utils.dependencies import get_current_student
from backend.models import Admin
from backend.schemas import AdminTopInternListResponse
from backend.services.ai import get_admin_top_interns
from utils.dependencies import get_current_admin

router = APIRouter(

    prefix="/ai",

    tags=["AI"]

)


@router.post(
    "/chat",
    response_model=AIChatResponse
)
def chat_with_ai(

    request: AIChatRequest,

    current_student: Student = Depends(get_current_student),

    db: Session = Depends(get_db)

):

    return ai_chat(
        message=request.message,
        student=current_student,
        db=db
    )

@router.get(
    "/dashboard",
    response_model=AIDashboardResponse
)
def dashboard_ai(

    current_student: Student = Depends(get_current_student),

    db: Session = Depends(get_db)

):

    return ai_dashboard_summary(
        student=current_student,
        db=db
    )

@router.get(
    "/dashboard",
    response_model=AIDashboardResponse
)
def ai_dashboard(

    current_student: Student = Depends(get_current_student),

    db: Session = Depends(get_db)

):

    return ai_dashboard_summary(
        student=current_student,
        db=db
    )

@router.get(
    "/roadmap",
    response_model=AIRoadmapResponse
)
def student_ai_roadmap(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return ai_learning_roadmap(
        student=current_student,
        db=db
    )

@router.get(
    "/mentor/dashboard",
    response_model=MentorDashboardResponse
)
def mentor_ai_dashboard(
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_complete_mentor_ai_dashboard(
        mentor=current_mentor,
        db=db
    )

@router.get(
    "/mentor/top-performers",
    response_model=list[StudentPerformanceSummary]
)
def mentor_top_performers(
    limit: int = Query(
        default=5,
        ge=1,
        le=20
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_mentor_top_performers(
        mentor=current_mentor,
        db=db,
        limit=limit
    )


@router.get(
    "/mentor/weak-performers",
    response_model=list[StudentPerformanceSummary]
)
def mentor_weak_performers(
    limit: int = Query(
        default=5,
        ge=1,
        le=20
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_mentor_weak_performers(
        mentor=current_mentor,
        db=db,
        limit=limit
    )

@router.get(
    "/mentor/team-analytics",
    response_model=MentorTeamAnalytics
)
def mentor_team_analytics(
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_mentor_team_analytics(
        mentor=current_mentor,
        db=db
    )

@router.get(
    "/mentor/recommendations",
    response_model=list[MentorRecommendation]
)
def mentor_recommendations(
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_mentor_ai_recommendations(
        mentor=current_mentor,
        db=db
    )

@router.get(
    "/mentor/engineering-growth/{student_id}",
    response_model=StudentEngineeringGrowth
)
def student_engineering_growth(
    student_id: int,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return get_student_engineering_growth(
        mentor=current_mentor,
        student_id=student_id,
        db=db
    )


@router.get(
    "/admin/top-interns",
    response_model=AdminTopInternListResponse
)
def admin_top_interns(
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return get_admin_top_interns(
        db=db,
        limit=limit
    )


@router.get(
    "/admin/recommendations",
    response_model=AdminRecommendationListResponse
)
def admin_ai_recommendations(
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return get_admin_ai_recommendations(
        db=db,
        limit=limit
    )


@router.get(
    "/reports/weekly-engineering",
    response_model=WeeklyEngineeringReportResponse
)
def weekly_engineering_report(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return get_weekly_engineering_report(
        db=db
    )


@router.get(
    "/reports/monthly-growth",
    response_model=MonthlyGrowthReportResponse
)
def monthly_growth_report(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return get_monthly_growth_report(
        db=db
    )


@router.get(
    "/reports/mentor-summary",
    response_model=MentorSummaryReportResponse
)
def mentor_summary_report(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return get_mentor_summary_report(
        db=db
    )


@router.get(
    "/reports/team-performance",
    response_model=TeamPerformanceReportResponse
)
def team_performance_report(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return get_team_performance_report(
        db=db
    )