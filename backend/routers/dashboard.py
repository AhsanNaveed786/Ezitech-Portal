from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student, Admin, CEO, Mentor
from utils.dependencies import (
    get_current_student,
    get_current_admin,
    get_current_ceo,
    get_current_mentor
)

from backend.services.dashboard import (
    student_dashboard,
    admin_dashboard,
    ceo_dashboard,
    mentor_dashboard
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/student")
def student_dashboard_api(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return student_dashboard(
        student_id=current_student.id,
        db=db
    )

@router.get("/admin")
def admin_dashboard_api(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return admin_dashboard(db)

@router.get("/ceo")
def ceo_dashboard_api(
    current_ceo: CEO = Depends(get_current_ceo),
    db: Session = Depends(get_db)
):

    return ceo_dashboard(db)

@router.get("/mentor")
def mentor_dashboard_api(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return mentor_dashboard(db)