from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from utils.dependencies import get_current_student, get_current_mentor

from backend.schemas import AttendanceCheckIn
from backend.models import Mentor, Student 
from backend.services.attendance import (
    check_in,
    check_out,
    attendance_history,
    mentor_student_attendance,
    today_attendance,
    mentor_today_attendance,
    mentor_all_attendance
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

@router.post("/check-in")
def student_check_in(
    attendance: AttendanceCheckIn,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return check_in(
        student_id=current_student.id,
        mentor_id=attendance.mentor_id,
        db=db
    )

@router.post("/check-out")
def student_check_out(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return check_out(
        student_id=current_student.id,
        db=db
    )

@router.get("/history")
def student_attendance_history(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return attendance_history(
        student_id=current_student.id,
        db=db
    )

@router.get("/today")
def student_today_attendance(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):

    return today_attendance(
        student_id=current_student.id,
        db=db
    )

@router.get("/mentor/today")
def mentor_today(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return mentor_today_attendance(
        mentor_id=current_mentor.id,
        db=db
    )

@router.get("/mentor/all")
def mentor_all(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return mentor_all_attendance(
        mentor_id=current_mentor.id,
        db=db
    )

@router.get("/mentor/all")
def mentor_all(
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return mentor_all_attendance(
        mentor_id=current_mentor.id,
        db=db
    )

@router.get("/mentor/student/{student_id}")
def mentor_student_history(
    student_id: int,
    current_mentor: Mentor = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):

    return mentor_student_attendance(
        mentor_id=current_mentor.id,
        student_id=student_id,
        db=db
    )