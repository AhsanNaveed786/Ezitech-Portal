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
    CommunicationRankingResponse,
    LeadershipPotentialResponse,
    MentorFeedbackCreate,
    MentorFeedbackListResponse,
    MentorFeedbackResponse,
    MentorFeedbackSummaryResponse,
    MentorFeedbackUpdate,
    WeakCommunicationResponse
)
from backend.services.mentor_feedback import (
    MentorFeedbackService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/mentor-feedback",
    tags=["Mentor Feedback"]
)


@router.post(
    "/mentor",
    response_model=MentorFeedbackResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_mentor_feedback(
    feedback_data: MentorFeedbackCreate,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        MentorFeedbackService
        .create_feedback(
            db=db,
            mentor=current_mentor,
            feedback_data=feedback_data
        )
    )


@router.put(
    "/mentor/{feedback_id}",
    response_model=MentorFeedbackResponse
)
def update_mentor_feedback(
    feedback_id: int,
    feedback_data: MentorFeedbackUpdate,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        MentorFeedbackService
        .update_feedback(
            db=db,
            mentor=current_mentor,
            feedback_id=feedback_id,
            feedback_data=feedback_data
        )
    )


@router.get(
    "/mentor/my-feedback",
    response_model=MentorFeedbackListResponse
)
def get_my_submitted_feedback(
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
    feedback_records = (
        MentorFeedbackService
        .get_mentor_feedback_records(
            db=db,
            mentor_id=current_mentor.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            feedback_records
        ),
        "feedback_records": feedback_records
    }


@router.get(
    "/student/me",
    response_model=MentorFeedbackListResponse
)
def get_my_feedback(
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
    feedback_records = (
        MentorFeedbackService
        .get_student_feedback(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            feedback_records
        ),
        "feedback_records": feedback_records
    }


@router.get(
    "/admin/{feedback_id}",
    response_model=MentorFeedbackResponse
)
def get_feedback_detail(
    feedback_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    feedback = (
        MentorFeedbackService
        .get_feedback_by_id(
            db=db,
            feedback_id=feedback_id
        )
    )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback record was not found."
        )

    return feedback


@router.get(
    "/admin/student/{student_id}",
    response_model=MentorFeedbackListResponse
)
def get_student_feedback_history(
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

    feedback_records = (
        MentorFeedbackService
        .get_student_feedback(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            feedback_records
        ),
        "feedback_records": feedback_records
    }


@router.get(
    "/admin/communication-rankings",
    response_model=CommunicationRankingResponse
)
def get_communication_rankings(
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
        MentorFeedbackService
        .get_latest_feedback_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(rankings),
        "rankings": rankings
    }


@router.get(
    "/admin/weak-communication",
    response_model=WeakCommunicationResponse
)
def get_weak_communication_students(
    score_threshold: float = Query(
        default=60,
        ge=0,
        le=100
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    students = (
        MentorFeedbackService
        .get_weak_communicators(
            db=db,
            score_threshold=score_threshold
        )
    )

    return {
        "score_threshold": score_threshold,
        "total_students": len(students),
        "students": students
    }


@router.get(
    "/admin/leadership-potential",
    response_model=LeadershipPotentialResponse
)
def get_leadership_potential_students(
    minimum_score: float = Query(
        default=75,
        ge=0,
        le=100
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    students = (
        MentorFeedbackService
        .get_leadership_potential(
            db=db,
            minimum_score=minimum_score
        )
    )

    return {
        "total_students": len(students),
        "students": students
    }


@router.get(
    "/admin/summary",
    response_model=MentorFeedbackSummaryResponse
)
def get_feedback_summary(
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
    return MentorFeedbackService.get_summary(
        db=db,
        period_days=period_days
    )