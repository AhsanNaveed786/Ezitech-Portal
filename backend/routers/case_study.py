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
    CaseStudy,
    Mentor,
    Student
)
from backend.schemas import (
    CaseStudyCreate,
    CaseStudyEvaluationRequest,
    CaseStudyListResponse,
    CaseStudyProgressUpdate,
    CaseStudyRankingResponse,
    CaseStudyRecommendationsResponse,
    CaseStudyResponse,
    CaseStudySubmissionRequest,
    CaseStudySummaryResponse
)
from backend.services.case_study import (
    CaseStudyService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/case-studies",
    tags=["Case Studies"]
)


@router.post(
    "/mentor/assign",
    response_model=CaseStudyResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_case_study(
    case_study_data: CaseStudyCreate,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return CaseStudyService.assign_case_study(
        db=db,
        mentor=current_mentor,
        case_study_data=case_study_data
    )


@router.get(
    "/mentor/my-case-studies",
    response_model=CaseStudyListResponse
)
def get_mentor_case_studies(
    limit: int = Query(
        default=100,
        ge=1,
        le=200
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    case_studies = (
        CaseStudyService
        .get_mentor_case_studies(
            db=db,
            mentor_id=current_mentor.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            case_studies
        ),
        "case_studies": case_studies
    }


@router.patch(
    "/mentor/{case_study_id}/evaluate",
    response_model=CaseStudyResponse
)
def evaluate_case_study(
    case_study_id: int,
    evaluation_data: CaseStudyEvaluationRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        CaseStudyService
        .evaluate_case_study(
            db=db,
            mentor=current_mentor,
            case_study_id=case_study_id,
            evaluation_data=evaluation_data
        )
    )


@router.get(
    "/student/my-case-studies",
    response_model=CaseStudyListResponse
)
def get_my_case_studies(
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    ),
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    case_studies = (
        CaseStudyService
        .get_student_case_studies(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            case_studies
        ),
        "case_studies": case_studies
    }


@router.patch(
    "/student/{case_study_id}/progress",
    response_model=CaseStudyResponse
)
def update_case_study_progress(
    case_study_id: int,
    progress_data: CaseStudyProgressUpdate,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return (
        CaseStudyService
        .update_progress(
            db=db,
            student=current_student,
            case_study_id=case_study_id,
            progress_data=progress_data
        )
    )


@router.post(
    "/student/{case_study_id}/submit",
    response_model=CaseStudyResponse
)
def submit_case_study(
    case_study_id: int,
    submission_data: CaseStudySubmissionRequest,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return (
        CaseStudyService
        .submit_case_study(
            db=db,
            student=current_student,
            case_study_id=case_study_id,
            submission_data=submission_data
        )
    )


@router.get(
    "/admin/{case_study_id}",
    response_model=CaseStudyResponse
)
def get_case_study_detail(
    case_study_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    case_study = (
        CaseStudyService
        .get_case_study_by_id(
            db=db,
            case_study_id=case_study_id
        )
    )

    if not case_study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study was not found."
        )

    return case_study


@router.get(
    "/admin/student/{student_id}",
    response_model=CaseStudyListResponse
)
def get_student_case_study_history(
    student_id: int,
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student was not found."
        )

    case_studies = (
        CaseStudyService
        .get_student_case_studies(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            case_studies
        ),
        "case_studies": case_studies
    }


@router.get(
    "/admin/rankings/top",
    response_model=CaseStudyRankingResponse
)
def get_case_study_rankings(
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    rankings = (
        CaseStudyService
        .get_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(
            rankings
        ),
        "rankings": rankings
    }


@router.get(
    "/admin/summary/performance",
    response_model=CaseStudySummaryResponse
)
def get_case_study_summary(
    period_days: int = Query(
        default=30,
        ge=1,
        le=365
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return CaseStudyService.get_summary(
        db=db,
        period_days=period_days
    )


@router.get(
    "/admin/recommendations/difficulty",
    response_model=(
        CaseStudyRecommendationsResponse
    )
)
def get_case_study_recommendations(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    recommendations = (
        CaseStudyService
        .get_case_study_recommendations(
            db=db
        )
    )

    return {
        "total_students": len(
            recommendations
        ),
        "recommendations": recommendations
    }