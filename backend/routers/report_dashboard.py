from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Admin,
    CEO,
    Mentor,
    Student
)
from backend.schemas import (
    AdminDashboardResponse,
    CEODashboardResponse,
    MentorDashboardResponse,
    PerformanceReportGenerateRequest,
    PerformanceReportListResponse,
    PerformanceReportResponse,
    StudentDashboardResponse
)
from backend.services.report_dashboard import (
    ReportDashboardService
)
from utils.dependencies import (
    get_current_admin,
    get_current_ceo,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/performance",
    tags=["Reports and Dashboards"]
)


@router.post(
    "/reports/admin/generate",
    response_model=PerformanceReportResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_admin_report(
    request_data: PerformanceReportGenerateRequest,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        ReportDashboardService
        .generate_report(
            db=db,
            request_data=request_data,
            generated_by_role="Admin",
            generated_by_user_id=current_admin.id
        )
    )


@router.post(
    "/reports/mentor/generate",
    response_model=PerformanceReportResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_mentor_report(
    request_data: PerformanceReportGenerateRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    allowed_report_types = {
        "Weekly Engineering Report",
        "Monthly Growth Report",
        "Mentor Summary",
        "Team Performance",
        "Productivity Trends"
    }

    if (
        request_data.report_type
        not in allowed_report_types
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Mentors cannot generate this "
                "report type."
            )
        )

    request_data.mentor_id = (
        current_mentor.id
    )

    return (
        ReportDashboardService
        .generate_report(
            db=db,
            request_data=request_data,
            generated_by_role="Mentor",
            generated_by_user_id=(
                current_mentor.id
            )
        )
    )


@router.get(
    "/reports/admin",
    response_model=PerformanceReportListResponse
)
def get_saved_reports(
    report_type: str | None = Query(
        default=None
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    reports = (
        ReportDashboardService
        .get_reports(
            db=db,
            limit=limit,
            report_type=report_type
        )
    )

    return {
        "total_records": len(reports),
        "reports": reports
    }


@router.get(
    "/reports/admin/{report_id}",
    response_model=PerformanceReportResponse
)
def get_saved_report(
    report_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    report = (
        ReportDashboardService
        .get_report_by_id(
            db=db,
            report_id=report_id
        )
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Performance report was not found."
            )
        )

    return report


@router.get(
    "/dashboard/student",
    response_model=StudentDashboardResponse
)
def get_student_dashboard(
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return (
        ReportDashboardService
        .get_student_dashboard(
            db=db,
            student=current_student
        )
    )


@router.get(
    "/dashboard/mentor",
    response_model=MentorDashboardResponse
)
def get_mentor_dashboard(
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        ReportDashboardService
        .get_mentor_dashboard(
            db=db,
            mentor=current_mentor
        )
    )


@router.get(
    "/dashboard/admin",
    response_model=AdminDashboardResponse
)
def get_admin_dashboard(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        ReportDashboardService
        .get_admin_dashboard(
            db=db
        )
    )


@router.get(
    "/dashboard/ceo",
    response_model=CEODashboardResponse
)
def get_ceo_dashboard(
    current_ceo: CEO = Depends(
        get_current_ceo
    ),
    db: Session = Depends(get_db)
):
    return (
        ReportDashboardService
        .get_ceo_dashboard(
            db=db
        )
    )