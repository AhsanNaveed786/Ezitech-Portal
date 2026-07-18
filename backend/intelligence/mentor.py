from sqlalchemy.orm import Session

from backend.models import Mentor, Student

from backend.services.ai import (
    calculate_student_engineering_score
)

from backend.intelligence.common import (
    build_intelligence_response,
    calculate_confidence_score
)


def calculate_mentor_team_performance(
    mentor: Mentor,
    db: Session
):
    students = (
        db.query(Student)
        .filter(Student.mentor_id == mentor.id)
        .all()
    )

    if not students:
        return {
            "mentor_id": mentor.id,
            "mentor_name": mentor.name,
            "department": mentor.department,
            "total_students": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "project_approval_percentage": 0.0,
            "students_requiring_attention": 0,
            "performance_status": "No Students Assigned"
        }

    performances = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

    total_students = len(performances)

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_students

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_students

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    students_requiring_attention = sum(
        1
        for item in performances
        if (
            item["engineering_score"] < 60
            or item["attendance_percentage"] < 70
            or item["rejected_projects"] > 0
        )
    )

    if average_engineering_score >= 80:
        performance_status = "Excellent"

    elif average_engineering_score >= 65:
        performance_status = "Good"

    elif average_engineering_score >= 50:
        performance_status = "Average"

    else:
        performance_status = "Needs Improvement"

    return {
        "mentor_id": mentor.id,
        "mentor_name": mentor.name,
        "department": mentor.department,
        "total_students": total_students,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "students_requiring_attention":
            students_requiring_attention,

        "performance_status": performance_status
    }


def get_best_mentor(
    question: str,
    db: Session
):
    mentors = db.query(Mentor).all()

    mentor_performances = []

    for mentor in mentors:
        performance = calculate_mentor_team_performance(
            mentor=mentor,
            db=db
        )

        if performance["total_students"] == 0:
            continue

        mentor_performances.append(performance)

    mentor_performances.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"],
            item["approved_projects"]
        ),
        reverse=True
    )

    confidence_score = calculate_confidence_score(
        total_records=len(mentors),
        matched_records=len(mentor_performances)
    )

    if not mentor_performances:
        answer = (
            "No mentor team performance data is currently available."
        )

        best_mentor = None

    else:
        best_mentor = mentor_performances[0]

        answer = (
            f"{best_mentor['mentor_name']} currently has the "
            f"highest-performing team with an average engineering "
            f"score of {best_mentor['average_engineering_score']}."
        )

    return build_intelligence_response(
        question=question,
        intent="best_mentor",
        answer=answer,
        data=best_mentor,
        confidence_score=confidence_score
    )


def get_weakest_mentor(
    question: str,
    db: Session
):
    mentors = db.query(Mentor).all()

    mentor_performances = []

    for mentor in mentors:
        performance = calculate_mentor_team_performance(
            mentor=mentor,
            db=db
        )

        if performance["total_students"] == 0:
            continue

        mentor_performances.append(performance)

    mentor_performances.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        )
    )

    confidence_score = calculate_confidence_score(
        total_records=len(mentors),
        matched_records=len(mentor_performances)
    )

    if not mentor_performances:
        answer = (
            "No mentor team performance data is currently available."
        )

        weakest_mentor = None

    else:
        weakest_mentor = mentor_performances[0]

        answer = (
            f"{weakest_mentor['mentor_name']}'s team currently "
            f"has the lowest average engineering score of "
            f"{weakest_mentor['average_engineering_score']} and "
            f"may require additional support."
        )

    return build_intelligence_response(
        question=question,
        intent="weakest_mentor",
        answer=answer,
        data=weakest_mentor,
        confidence_score=confidence_score
    )


def get_mentor_team_rankings(
    question: str,
    db: Session,
    limit: int = 10
):
    mentors = db.query(Mentor).all()

    mentor_performances = []

    for mentor in mentors:
        performance = calculate_mentor_team_performance(
            mentor=mentor,
            db=db
        )

        if performance["total_students"] == 0:
            continue

        mentor_performances.append(performance)

    mentor_performances.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        ),
        reverse=True
    )

    mentor_performances = mentor_performances[:limit]

    ranked_mentors = []

    for index, mentor in enumerate(
        mentor_performances,
        start=1
    ):
        ranked_mentors.append({
            "rank": index,
            **mentor
        })

    confidence_score = calculate_confidence_score(
        total_records=len(mentors),
        matched_records=len(ranked_mentors)
    )

    if not ranked_mentors:
        answer = (
            "No mentor team rankings are currently available."
        )

    else:
        answer = (
            f"{len(ranked_mentors)} mentor teams were ranked "
            f"using engineering score, attendance and "
            f"project approval performance."
        )

    return build_intelligence_response(
        question=question,
        intent="mentor_team_rankings",
        answer=answer,
        data=ranked_mentors,
        confidence_score=confidence_score
    )


def get_mentors_needing_support(
    question: str,
    db: Session,
    limit: int = 10
):
    mentors = db.query(Mentor).all()

    mentors_needing_support = []

    for mentor in mentors:
        performance = calculate_mentor_team_performance(
            mentor=mentor,
            db=db
        )

        if performance["total_students"] == 0:
            continue

        if (
            performance["average_engineering_score"] < 60
            or performance["average_attendance"] < 70
            or performance["students_requiring_attention"] > 0
        ):
            mentors_needing_support.append({
                **performance,
                "recommended_action": (
                    "Review mentor workload and schedule "
                    "team performance support."
                )
            })

    mentors_needing_support.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["average_attendance"],
            -item["students_requiring_attention"]
        )
    )

    mentors_needing_support = (
        mentors_needing_support[:limit]
    )

    confidence_score = calculate_confidence_score(
        total_records=len(mentors),
        matched_records=len(mentors_needing_support)
    )

    if not mentors_needing_support:
        answer = (
            "No mentor teams currently meet the support criteria."
        )

    else:
        answer = (
            f"{len(mentors_needing_support)} mentor teams "
            f"currently require additional support."
        )

    return build_intelligence_response(
        question=question,
        intent="mentors_needing_support",
        answer=answer,
        data=mentors_needing_support,
        confidence_score=confidence_score
    )