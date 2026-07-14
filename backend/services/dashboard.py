from sqlalchemy.orm import Session

from backend.models import Attendance

from backend.models import (
    Student,
    Mentor,
    Admin,
    CEO,
    Attendance,
    Leave
)

def student_dashboard(
    student_id: int,
    db: Session
):

    total_attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).count()

    present_days = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "Present"
    ).count()

    absent_days = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "Absent"
    ).count()

    attendance_percentage = 0

    if total_attendance > 0:
        attendance_percentage = round(
            (present_days / total_attendance) * 100,
            2
        )

    return {
        "total_attendance": total_attendance,
        "present_days": present_days,
        "absent_days": absent_days,
        "attendance_percentage": attendance_percentage
    }

def admin_dashboard(
    db: Session
):

    total_students = db.query(Student).count()

    total_mentors = db.query(Mentor).count()

    total_attendance = db.query(Attendance).count()

    total_leaves = db.query(Leave).count()

    pending_leaves = db.query(Leave).filter(
        Leave.status == "Pending"
    ).count()

    approved_leaves = db.query(Leave).filter(
        Leave.status == "Approved"
    ).count()

    rejected_leaves = db.query(Leave).filter(
        Leave.status == "Rejected"
    ).count()

    return {
        "total_students": total_students,
        "total_mentors": total_mentors,
        "total_attendance_records": total_attendance,
        "total_leave_requests": total_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves
    }

def ceo_dashboard(
    db: Session
):

    total_students = db.query(Student).count()

    total_mentors = db.query(Mentor).count()

    total_admins = db.query(Admin).count()

    total_ceos = db.query(CEO).count()

    total_attendance = db.query(Attendance).count()

    total_leaves = db.query(Leave).count()

    return {
        "total_students": total_students,
        "total_mentors": total_mentors,
        "total_admins": total_admins,
        "total_ceos": total_ceos,
        "total_attendance_records": total_attendance,
        "total_leave_requests": total_leaves
    }