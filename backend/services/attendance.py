from datetime import date, datetime

from sqlalchemy.orm import Session

from backend.models import Attendance, Mentor, Student


def check_in(
    student_id: int,
    mentor_id: int,
    db: Session
):

    existing_attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == date.today()
    ).first()

    if existing_attendance:
        return {
            "message": "You have already checked in today."
        }

    mentor = db.query(Mentor).filter(
        Mentor.id == mentor_id
    ).first()

    if mentor is None:
        return {
            "message": "Mentor not found."
        }

    new_attendance = Attendance(
        student_id=student_id,
        mentor_id=mentor_id,
        date=date.today(),
        status="Present",
        checked_in_time=datetime.now()
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return {
        "message": "Check-in successful."
    }

def check_out(
    student_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == date.today()
    ).first()

    if attendance is None:
        return {
            "message": "You have not checked in today."
        }

    if attendance.checked_out_time is not None:
        return {
            "message": "You have already checked out."
        }

    attendance.checked_out_time = datetime.now()

    db.commit()
    db.refresh(attendance)

    return {
        "message": "Check-out successful."
    }

def check_out(
    student_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == date.today()
    ).first()

    if attendance is None:
        return {
            "message": "You have not checked in today."
        }

    if attendance.checked_out_time is not None:
        return {
            "message": "You have already checked out."
        }

    attendance.checked_out_time = datetime.now()

    db.commit()
    db.refresh(attendance)

    return {
        "message": "Check-out successful."
    }

def attendance_history(
    student_id: int,
    db: Session
):

    history = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(
        Attendance.date.desc()
    ).all()

    return history

def today_attendance(
    student_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == date.today()
    ).first()

    if attendance is None:
        return {
            "message": "No attendance found for today."
        }

    return attendance

def mentor_today_attendance(
    mentor_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.mentor_id == mentor_id,
        Attendance.date == date.today()
    ).all()

    return attendance

def mentor_all_attendance(
    mentor_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.mentor_id == mentor_id
    ).order_by(
        Attendance.date.desc()
    ).all()

    return attendance


def mentor_all_attendance(
    mentor_id: int,
    db: Session
):

    attendance = (
        db.query(
            Attendance,
            Student.name,
            Student.email,
            Student.batch
        )
        .join(
            Student,
            Attendance.student_id == Student.id
        )
        .filter(
            Attendance.mentor_id == mentor_id
        )
        .order_by(
            Attendance.date.desc()
        )
        .all()
    )

    result = []

    for record, name, email, batch in attendance:

        result.append({
            "student_name": name,
            "student_email": email,
            "batch": batch,
            "date": record.date,
            "status": record.status,
            "checked_in_time": record.checked_in_time,
            "checked_out_time": record.checked_out_time
        })

    return result

def mentor_student_attendance(
    mentor_id: int,
    student_id: int,
    db: Session
):

    attendance = db.query(Attendance).filter(
        Attendance.mentor_id == mentor_id,
        Attendance.student_id == student_id
    ).order_by(
        Attendance.date.desc()
    ).all()

    return attendance