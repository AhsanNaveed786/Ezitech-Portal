from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student
from backend.services.dashboard import student_dashboard
from utils.dependencies import get_current_student

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/student")
def dashboard(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return student_dashboard(
        student_id=current_student.id,
        db=db
    )