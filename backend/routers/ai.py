from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
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