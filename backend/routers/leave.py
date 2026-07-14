from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student, Mentor
from backend.schemas import LeaveApplication
from utils.dependencies import get_current_mentor, get_current_student
from backend.services.leave import (
    apply_leave,
    my_leave_history,
    pending_leaves,
    approve_leave,
    reject_leave
)


router = APIRouter(
    prefix="/leave",
    tags=["Leave"]
)



@router.post("/apply")
def student_apply_leave(
    leave: LeaveApplication,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return apply_leave(
        student_id=current_student.id,
        leave=leave,
        db=db
    )

@router.get("/history")
def student_leave_history(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return my_leave_history(
        student_id=current_student.id,
        db=db
    )

@router.get("/mentor/pending")
def mentor_pending_leaves(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return pending_leaves(db)

@router.put("/mentor/approve/{leave_id}")
def mentor_approve_leave(
    leave_id: int,
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return approve_leave(
        leave_id=leave_id,
        mentor_id=current_mentor.id,
        db=db
    )

@router.put("/mentor/reject/{leave_id}")
def mentor_reject_leave(
    leave_id: int,
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return reject_leave(
        leave_id=leave_id,
        mentor_id=current_mentor.id,
        db=db
    )