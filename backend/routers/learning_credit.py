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
    EngineeringCreditCreate,
    EngineeringCreditListResponse,
    EngineeringCreditRankingResponse,
    EngineeringCreditResponse,
    LearningCreditSummaryResponse,
    LearningSpeedGenerateRequest,
    LearningSpeedListResponse,
    LearningSpeedRankingResponse,
    LearningSpeedResponse
)
from backend.services.learning_credits import (
    LearningCreditService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/learning-credits",
    tags=["Learning Speed and Engineering Credits"]
)


@router.post(
    "/mentor/generate-learning-speed",
    response_model=LearningSpeedResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_learning_speed(
    request_data: LearningSpeedGenerateRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        LearningCreditService
        .generate_learning_speed(
            db=db,
            mentor=current_mentor,
            request_data=request_data
        )
    )


@router.post(
    "/mentor/award-credit",
    response_model=EngineeringCreditResponse,
    status_code=status.HTTP_201_CREATED
)
def award_engineering_credit(
    credit_data: EngineeringCreditCreate,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        LearningCreditService
        .award_engineering_credit(
            db=db,
            mentor=current_mentor,
            credit_data=credit_data
        )
    )


@router.get(
    "/student/learning-history",
    response_model=LearningSpeedListResponse
)
def get_my_learning_history(
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
        LearningCreditService
        .get_student_learning_records(
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
    "/student/credits",
    response_model=EngineeringCreditListResponse
)
def get_my_engineering_credits(
    limit: int = Query(
        default=100,
        ge=1,
        le=200
    ),
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    credits = (
        LearningCreditService
        .get_student_credits(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    totals = (
        LearningCreditService
        .get_credit_totals(
            db=db,
            student_id=current_student.id
        )
    )

    return {
        "student_id": current_student.id,
        **totals,
        "credits": credits
    }


@router.get(
    "/admin/student/{student_id}/learning-history",
    response_model=LearningSpeedListResponse
)
def get_student_learning_history(
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
        LearningCreditService
        .get_student_learning_records(
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
    "/admin/student/{student_id}/credits",
    response_model=EngineeringCreditListResponse
)
def get_student_credit_history(
    student_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=200
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

    credits = (
        LearningCreditService
        .get_student_credits(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    totals = (
        LearningCreditService
        .get_credit_totals(
            db=db,
            student_id=student_id
        )
    )

    return {
        "student_id": student_id,
        **totals,
        "credits": credits
    }


@router.get(
    "/admin/learning-rankings",
    response_model=LearningSpeedRankingResponse
)
def get_learning_speed_rankings(
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
        LearningCreditService
        .get_learning_speed_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(rankings),
        "rankings": rankings
    }


@router.get(
    "/admin/credit-rankings",
    response_model=EngineeringCreditRankingResponse
)
def get_engineering_credit_rankings(
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
        LearningCreditService
        .get_credit_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(rankings),
        "rankings": rankings
    }


@router.get(
    "/admin/summary",
    response_model=LearningCreditSummaryResponse
)
def get_learning_credit_summary(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        LearningCreditService
        .get_summary(
            db=db
        )
    )