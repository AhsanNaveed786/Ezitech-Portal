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
    AIRecommendationCompletionRequest,
    AIRecommendationGenerateRequest,
    AIRecommendationGenerationResponse,
    AIRecommendationListResponse,
    AIRecommendationResponse,
    AIRecommendationStatusUpdate,
    AIRecommendationSummaryResponse,
    RecommendationStudentListResponse
)
from backend.services.ai_recommendation import (
    AIRecommendationService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/ai-recommendations",
    tags=["AI Recommendations"]
)


@router.post(
    "/mentor/generate",
    response_model=AIRecommendationGenerationResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_recommendations_by_mentor(
    request_data: AIRecommendationGenerateRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    recommendations = (
        AIRecommendationService
        .generate_recommendations(
            db=db,
            student_id=request_data.student_id,
            engineering_performance_record_id=(
                request_data
                .engineering_performance_record_id
            ),
            mentor=current_mentor
        )
    )

    performance_record_id = (
        recommendations[0]
        .engineering_performance_record_id
        if recommendations
        else (
            request_data
            .engineering_performance_record_id
            or 0
        )
    )

    return {
        "student_id": request_data.student_id,
        "engineering_performance_record_id": (
            performance_record_id
        ),
        "total_generated": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.post(
    "/admin/generate",
    response_model=AIRecommendationGenerationResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_recommendations_by_admin(
    request_data: AIRecommendationGenerateRequest,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    recommendations = (
        AIRecommendationService
        .generate_recommendations(
            db=db,
            student_id=request_data.student_id,
            engineering_performance_record_id=(
                request_data
                .engineering_performance_record_id
            ),
            admin=current_admin
        )
    )

    performance_record_id = (
        recommendations[0]
        .engineering_performance_record_id
        if recommendations
        else (
            request_data
            .engineering_performance_record_id
            or 0
        )
    )

    return {
        "student_id": request_data.student_id,
        "engineering_performance_record_id": (
            performance_record_id
        ),
        "total_generated": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.patch(
    "/mentor/{recommendation_id}/submit",
    response_model=AIRecommendationResponse
)
def submit_recommendation_for_approval(
    recommendation_id: int,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        AIRecommendationService
        .submit_for_approval(
            db=db,
            mentor=current_mentor,
            recommendation_id=recommendation_id
        )
    )


@router.patch(
    "/admin/{recommendation_id}/review",
    response_model=AIRecommendationResponse
)
def review_ai_recommendation(
    recommendation_id: int,
    review_data: AIRecommendationStatusUpdate,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    if review_data.status not in {
        "Approved",
        "Rejected"
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Admin status must be Approved "
                "or Rejected."
            )
        )

    return (
        AIRecommendationService
        .review_recommendation(
            db=db,
            admin=current_admin,
            recommendation_id=recommendation_id,
            new_status=review_data.status,
            review_notes=review_data.review_notes
        )
    )


@router.patch(
    "/mentor/{recommendation_id}/complete",
    response_model=AIRecommendationResponse
)
def complete_ai_recommendation(
    recommendation_id: int,
    completion_data: (
        AIRecommendationCompletionRequest
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return (
        AIRecommendationService
        .complete_recommendation(
            db=db,
            mentor=current_mentor,
            recommendation_id=recommendation_id,
            completion_notes=(
                completion_data.completion_notes
            )
        )
    )


@router.get(
    "/student/me",
    response_model=AIRecommendationListResponse
)
def get_my_ai_recommendations(
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
    recommendations = (
        AIRecommendationService
        .get_student_recommendations(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.get(
    "/mentor/my-recommendations",
    response_model=AIRecommendationListResponse
)
def get_mentor_ai_recommendations(
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
    recommendations = (
        AIRecommendationService
        .get_mentor_recommendations(
            db=db,
            mentor_id=current_mentor.id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.get(
    "/admin/pending",
    response_model=AIRecommendationListResponse
)
def get_pending_ai_recommendations(
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
    recommendations = (
        AIRecommendationService
        .get_pending_recommendations(
            db=db,
            limit=limit
        )
    )

    return {
        "total_records": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.get(
    "/admin/recommendation/{recommendation_id}",
    response_model=AIRecommendationResponse
)
def get_ai_recommendation_detail(
    recommendation_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    recommendation = (
        AIRecommendationService
        .get_recommendation_by_id(
            db=db,
            recommendation_id=recommendation_id
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation was not found."
        )

    return recommendation


@router.get(
    "/admin/student/{student_id}",
    response_model=AIRecommendationListResponse
)
def get_student_ai_recommendations(
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
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student was not found."
        )

    recommendations = (
        AIRecommendationService
        .get_student_recommendations(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    return {
        "total_records": len(
            recommendations
        ),
        "recommendations": recommendations
    }


@router.get(
    "/admin/students-by-type",
    response_model=RecommendationStudentListResponse
)
def get_students_by_recommendation_type(
    recommendation_type: str = Query(...),
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
    students = (
        AIRecommendationService
        .get_students_by_recommendation(
            db=db,
            recommendation_type=(
                recommendation_type
            ),
            limit=limit
        )
    )

    return {
        "recommendation_type": (
            recommendation_type
        ),
        "total_students": len(students),
        "students": students
    }


@router.get(
    "/admin/summary",
    response_model=AIRecommendationSummaryResponse
)
def get_ai_recommendation_summary(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        AIRecommendationService
        .get_summary(
            db=db
        )
    )