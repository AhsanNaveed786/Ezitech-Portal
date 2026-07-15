from sqlalchemy.orm import Session
from datetime import date
from backend.models import Leave, Student
from backend.schemas import LeaveApplication


def apply_leave(
    student_id: int,
    leave: LeaveApplication,
    db: Session
):

    
    if leave.leave_date < date.today():
        return {
            "message": "You cannot apply leave for a past date."
        }

    existing_leave = db.query(Leave).filter(
        Leave.student_id == student_id,
        Leave.leave_date == leave.leave_date
    ).first()

    if existing_leave:
        return {
            "message": "Leave already applied for this date."
        }

    new_leave = Leave(
        student_id=student_id,
        reason=leave.reason,
        leave_date=leave.leave_date
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return {
        "message": "Leave applied successfully."
    }

def my_leave_history(
    student_id: int,
    db: Session
):

    leaves = db.query(Leave).filter(
        Leave.student_id == student_id
    ).order_by(
        Leave.leave_date.desc()
    ).all()

    return leaves

def pending_leaves(
    db: Session
):

    leaves = (
        db.query(
            Leave,
            Student.name,
            Student.email,
            Student.batch
        )
        .join(
            Student,
            Leave.student_id == Student.id
        )
        .filter(
            Leave.status == "Pending"
        )
        .order_by(
            Leave.applied_at.desc()
        )
        .all()
    )

    result = []

    for leave, name, email, batch in leaves:

        result.append({
            "leave_id": leave.id,
            "student_name": name,
            "student_email": email,
            "batch": batch,
            "reason": leave.reason,
            "leave_date": leave.leave_date,
            "status": leave.status,
            "applied_at": leave.applied_at
        })

    return result

def approve_leave(
    leave_id: int,
    mentor_id: int,
    db: Session
):

    leave = db.query(Leave).filter(
        Leave.id == leave_id
    ).first()

    if leave is None:
        return {
            "message": "Leave not found."
        }

    if leave.status != "Pending":
        return {
            "message": "Leave already processed."
        }

    leave.status = "Approved"
    leave.mentor_id = mentor_id

    db.commit()
    db.refresh(leave)

    return {
        "message": "Leave approved successfully."
    }

def reject_leave(
    leave_id: int,
    mentor_id: int,
    db: Session
):

    leave = db.query(Leave).filter(
        Leave.id == leave_id
    ).first()

    if leave is None:
        return {
            "message": "Leave not found."
        }

    if leave.status != "Pending":
        return {
            "message": "Leave already processed."
        }

    leave.status = "Rejected"
    leave.mentor_id = mentor_id

    db.commit()
    db.refresh(leave)

    return {
        "message": "Leave rejected successfully."
    }