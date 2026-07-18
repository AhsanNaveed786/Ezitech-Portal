from sqlalchemy.orm import Session

from backend.models import Student
from backend.services.ai import (
    calculate_student_engineering_score
)

from backend.intelligence.common import (
    build_intelligence_response,
    calculate_confidence_score
)


def get_top_students(
    question: str,
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    performances = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

    performances.sort(
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    top_students = performances[:limit]

    confidence_score = calculate_confidence_score(
        total_records=len(students),
        matched_records=len(top_students)
    )

    if not top_students:
        answer = "No student performance data is available."

    else:
        best_student = top_students[0]

        answer = (
            f"{best_student['student_name']} is currently "
            f"the top-performing intern with an engineering "
            f"score of {best_student['engineering_score']}."
        )

    return build_intelligence_response(
        question=question,
        intent="top_students",
        answer=answer,
        data=top_students,
        confidence_score=confidence_score
    )


def get_weak_students(
    question: str,
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    weak_students = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        if (
            performance["engineering_score"] < 60
            or performance["attendance_percentage"] < 70
        ):
            weak_students.append(performance)

    weak_students.sort(
        key=lambda item: (
            item["engineering_score"],
            item["attendance_percentage"]
        )
    )

    weak_students = weak_students[:limit]

    confidence_score = calculate_confidence_score(
        total_records=len(students),
        matched_records=len(weak_students)
    )

    if not weak_students:
        answer = (
            "No students currently meet the weak-performance criteria."
        )

    else:
        answer = (
            f"{len(weak_students)} students currently require "
            f"additional performance support."
        )

    return build_intelligence_response(
        question=question,
        intent="weak_students",
        answer=answer,
        data=weak_students,
        confidence_score=confidence_score
    )


def get_job_ready_students(
    question: str,
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    job_ready_students = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        if (
            performance["engineering_score"] >= 85
            and performance["attendance_percentage"] >= 90
            and performance["approved_projects"] >= 4
        ):
            job_ready_students.append({
                **performance,
                "placement_status": "Ready for Job",
                "recommended_action": "Recommend Job Placement"
            })

    job_ready_students.sort(
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    job_ready_students = job_ready_students[:limit]

    confidence_score = calculate_confidence_score(
        total_records=len(students),
        matched_records=len(job_ready_students)
    )

    if not job_ready_students:
        answer = (
            "No interns currently meet the job-readiness criteria."
        )

    else:
        answer = (
            f"{len(job_ready_students)} interns are currently "
            f"ready for job placement."
        )

    return build_intelligence_response(
        question=question,
        intent="job_ready_students",
        answer=answer,
        data=job_ready_students,
        confidence_score=confidence_score
    )


def get_interview_ready_students(
    question: str,
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    interview_ready_students = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        if (
            performance["engineering_score"] >= 75
            and performance["attendance_percentage"] >= 80
            and performance["approved_projects"] >= 3
        ):
            interview_ready_students.append({
                **performance,
                "placement_status": "Ready for Interview",
                "recommended_action": "Recommend Interview"
            })

    interview_ready_students.sort(
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    interview_ready_students = (
        interview_ready_students[:limit]
    )

    confidence_score = calculate_confidence_score(
        total_records=len(students),
        matched_records=len(interview_ready_students)
    )

    if not interview_ready_students:
        answer = (
            "No interns currently meet the interview-readiness criteria."
        )

    else:
        answer = (
            f"{len(interview_ready_students)} interns are "
            f"currently ready for interviews."
        )

    return build_intelligence_response(
        question=question,
        intent="interview_ready_students",
        answer=answer,
        data=interview_ready_students,
        confidence_score=confidence_score
    )


def get_students_needing_mentoring(
    question: str,
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    mentoring_students = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        if (
            performance["engineering_score"] < 60
            or performance["attendance_percentage"] < 70
            or performance["rejected_projects"] > 0
        ):
            mentoring_students.append({
                **performance,
                "recommended_action": "Schedule Mentor Meeting"
            })

    mentoring_students.sort(
        key=lambda item: (
            item["engineering_score"],
            item["attendance_percentage"],
            -item["rejected_projects"]
        )
    )

    mentoring_students = mentoring_students[:limit]

    confidence_score = calculate_confidence_score(
        total_records=len(students),
        matched_records=len(mentoring_students)
    )

    if not mentoring_students:
        answer = (
            "No students currently require additional mentoring."
        )

    else:
        answer = (
            f"{len(mentoring_students)} students currently "
            f"require focused mentor support."
        )

    return build_intelligence_response(
        question=question,
        intent="students_needing_mentoring",
        answer=answer,
        data=mentoring_students,
        confidence_score=confidence_score
    )