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
    Mentor,
    Student
)
from backend.schemas import (
    EngineeringPerformanceSummaryResponse,
    EngineeringRankingResponse,
    EngineeringReadinessResponse,
    EngineeringScoreGenerateRequest,
    EngineeringScoreListResponse,
    EngineeringScoreResponse
)
from backend.services.engineering_score import (
    EngineeringScoreService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/engineering-score",
    tags=["Engineering Performance Score"]
)


@router.post(
    "/mentor/generate",
    response_model=EngineeringScoreResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_engineering_score_by_mentor(
    request_data: EngineeringScoreGenerateRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        EngineeringScoreService
        .generate_score(
            db=db,
            request_data=request_data,
            mentor=current_mentor
        )
    )


@router.post(
    "/admin/generate",
    response_model=EngineeringScoreResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_engineering_score_by_admin(
    request_data: EngineeringScoreGenerateRequest,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        EngineeringScoreService
        .generate_score(
            db=db,
            request_data=request_data,
            admin=current_admin
        )
    )


@router.get(
    "/student/latest",
    response_model=EngineeringScoreResponse
)
def get_my_latest_engineering_score(
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    record = (
        EngineeringScoreService
        .get_latest_student_score(
            db=db,
            student_id=current_student.id
        )
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No engineering score exists "
                "for this student."
            )
        )

    return record


@router.get(
    "/student/history",
    response_model=EngineeringScoreListResponse
)
def get_my_engineering_score_history(
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
    records = (
        EngineeringScoreService
        .get_student_history(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    return {
        "total_records": len(records),
        "records": records
    }


@router.get(
    "/admin/record/{record_id}",
    response_model=EngineeringScoreResponse
)
def get_engineering_score_record(
    record_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    record = (
        EngineeringScoreService
        .get_record_by_id(
            db=db,
            record_id=record_id
        )
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Engineering performance record "
                "was not found."
            )
        )

    return record


@router.get(
    "/admin/student/{student_id}/latest",
    response_model=EngineeringScoreResponse
)
def get_student_latest_engineering_score(
    student_id: int,
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

    record = (
        EngineeringScoreService
        .get_latest_student_score(
            db=db,
            student_id=student_id
        )
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No engineering score exists "
                "for this student."
            )
        )

    return record


@router.get(
    "/admin/student/{student_id}/history",
    response_model=EngineeringScoreListResponse
)
def get_student_engineering_score_history(
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

    records = (
        EngineeringScoreService
        .get_student_history(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    return {
        "total_records": len(records),
        "records": records
    }


@router.get(
    "/admin/rankings",
    response_model=EngineeringRankingResponse
)
def get_engineering_rankings(
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
        EngineeringScoreService
        .get_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(rankings),
        "rankings": rankings
    }


@router.get(
    "/admin/readiness/{readiness_type}",
    response_model=EngineeringReadinessResponse
)
def get_ready_students(
    readiness_type: str,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    students = (
        EngineeringScoreService
        .get_readiness_students(
            db=db,
            readiness_type=readiness_type
        )
    )

    return {
        "readiness_type": readiness_type,
        "total_students": len(students),
        "students": students
    }


@router.get(
    "/admin/summary",
    response_model=(
        EngineeringPerformanceSummaryResponse
    )
)
def get_engineering_performance_summary(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        EngineeringScoreService
        .get_summary(
            db=db
        )
    )