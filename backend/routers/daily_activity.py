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
    DailyActivityCreate,
    DailyActivityListResponse,
    DailyActivityResponse,
    DailyActivitySummaryResponse,
    DailyActivityUpdate,
    DailyActivityVerificationRequest,
    InactiveStudentsResponse
)
from backend.services.daily_activity import (
    DailyActivityService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/daily-activity",
    tags=["Daily Activity"]
)


@router.post(
    "/student",
    response_model=DailyActivityResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_daily_activity(
    activity_data: DailyActivityCreate,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return DailyActivityService.create_activity(
        db=db,
        student=current_student,
        activity_data=activity_data
    )


@router.put(
    "/student/{activity_id}",
    response_model=DailyActivityResponse
)
def update_daily_activity(
    activity_id: int,
    activity_data: DailyActivityUpdate,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return DailyActivityService.update_activity(
        db=db,
        student=current_student,
        activity_id=activity_id,
        activity_data=activity_data
    )


@router.get(
    "/student/me",
    response_model=DailyActivityListResponse
)
def get_my_daily_activities(
    limit: int = Query(
        default=30,
        ge=1,
        le=100
    ),
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    activities = (
        DailyActivityService
        .get_student_activities(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    total_records = (
        DailyActivityService
        .count_student_activities(
            db=db,
            student_id=current_student.id
        )
    )

    return {
        "total_records": total_records,
        "activities": activities
    }


@router.get(
    "/mentor/student/{student_id}",
    response_model=DailyActivityListResponse
)
def get_assigned_student_activities(
    student_id: int,
    limit: int = Query(
        default=30,
        ge=1,
        le=100
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    activities = (
        DailyActivityService
        .get_mentor_student_activities(
            db=db,
            mentor=current_mentor,
            student_id=student_id,
            limit=limit
        )
    )

    return {
        "total_records": len(activities),
        "activities": activities
    }


@router.patch(
    "/mentor/{activity_id}/verify",
    response_model=DailyActivityResponse
)
def verify_student_activity(
    activity_id: int,
    verification_data: (
        DailyActivityVerificationRequest
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return DailyActivityService.verify_activity(
        db=db,
        mentor=current_mentor,
        activity_id=activity_id,
        verification_data=verification_data
    )


@router.get(
    "/admin/student/{student_id}",
    response_model=DailyActivityListResponse
)
def get_student_activity_history(
    student_id: int,
    limit: int = Query(
        default=30,
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
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student was not found."
        )

    activities = (
        DailyActivityService
        .get_student_activities(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    total_records = (
        DailyActivityService
        .count_student_activities(
            db=db,
            student_id=student_id
        )
    )

    return {
        "total_records": total_records,
        "activities": activities
    }


@router.get(
    "/admin/inactive-students",
    response_model=InactiveStudentsResponse
)
def get_inactive_students(
    inactivity_days: int = Query(
        default=3,
        ge=1,
        le=90
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    inactive_students = (
        DailyActivityService
        .get_inactive_students(
            db=db,
            inactivity_days=inactivity_days
        )
    )

    total_students = (
        db.query(Student).count()
    )

    return {
        "inactivity_threshold_days": (
            inactivity_days
        ),
        "total_students": total_students,
        "inactive_students_count": len(
            inactive_students
        ),
        "inactive_students": inactive_students
    }


@router.get(
    "/admin/summary",
    response_model=DailyActivitySummaryResponse
)
def get_daily_activity_summary(
    period_days: int = Query(
        default=7,
        ge=1,
        le=365
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        DailyActivityService
        .get_activity_summary(
            db=db,
            period_days=period_days
        )
    )