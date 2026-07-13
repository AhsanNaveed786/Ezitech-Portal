from sqlalchemy.orm import Session
from backend.models import Attendance


def student_dashboard(
    student_id: int,
    db: Session
):

    total = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).count()

    present = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "Present"
    ).count()

    absent = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.status == "Absent"
    ).count()

    percentage = 0

    if total > 0:
        percentage = round((present / total) * 100, 2)

    return {
        "total_attendance": total,
        "present_days": present,
        "absent_days": absent,
        "attendance_percentage": percentage
    }