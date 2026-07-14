from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Mentor, Student, Admin
from backend.schemas import (
    ProjectSubmission,
    ProjectReview
)
from utils.dependencies import (
    get_current_student,
    get_current_mentor,
    get_current_admin
)
from backend.services.project import (
    submit_project,
    project_history,
    pending_projects,
    approve_project,
    reject_project,
    my_project_result,
    resubmit_project,
    admin_all_projects
)
router = APIRouter(
    prefix="/project",
    tags=["Project"]
)


@router.post("/submit")
def student_submit_project(
    project: ProjectSubmission,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return submit_project(
        student_id=current_student.id,
        project=project,
        db=db
    )

@router.get("/history")
def student_project_history(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return project_history(
        student_id=current_student.id,
        db=db
    )

@router.get("/mentor/pending")
def mentor_pending_projects(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return pending_projects(db)


@router.put("/mentor/approve/{project_id}")
def mentor_approve_project(
    project_id: int,
    review: ProjectReview,
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return approve_project(
        project_id=project_id,
        mentor_id=current_mentor.id,
        review=review,
        db=db
    )

@router.put("/mentor/reject/{project_id}")
def mentor_reject_project(
    project_id: int,
    review: ProjectReview,
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return reject_project(
        project_id=project_id,
        mentor_id=current_mentor.id,
        review=review,
        db=db
    )

@router.get("/result")
def student_project_result(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return my_project_result(
        student_id=current_student.id,
        db=db
    )

@router.put("/resubmit/{project_id}")
def student_resubmit_project(
    project_id: int,
    project: ProjectSubmission,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return resubmit_project(
        project_id=project_id,
        student_id=current_student.id,
        project=project,
        db=db
    )

@router.get("/admin/all")
def admin_projects(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return admin_all_projects(db)