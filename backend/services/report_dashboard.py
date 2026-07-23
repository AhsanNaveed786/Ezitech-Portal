from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models import (
    AIRecommendation,
    Attendance,
    CaseStudy,
    DailyActivity,
    EngineeringCredit,
    EngineeringPerformanceRecord,
    GitHubReport,
    LearningSpeedRecord,
    Mentor,
    MentorFeedback,
    PerformanceReport,
    Student,
    Task
)
from backend.schemas import (
    PerformanceReportGenerateRequest
)


class ReportDashboardService:

    @staticmethod
    def generate_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest,
        generated_by_role: str,
        generated_by_user_id: int | None = None
    ) -> PerformanceReport:
        report_builders = {
            "Weekly Engineering Report": (
                ReportDashboardService
                .build_weekly_engineering_report
            ),
            "Monthly Growth Report": (
                ReportDashboardService
                .build_monthly_growth_report
            ),
            "Mentor Summary": (
                ReportDashboardService
                .build_mentor_summary_report
            ),
            "Team Performance": (
                ReportDashboardService
                .build_team_performance_report
            ),
            "Technology Performance": (
                ReportDashboardService
                .build_technology_performance_report
            ),
            "Productivity Trends": (
                ReportDashboardService
                .build_productivity_trends_report
            )
        }

        builder = report_builders.get(
            request_data.report_type
        )

        if not builder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported performance report type."
            )

        report_data = builder(
            db=db,
            request_data=request_data
        )

        saved_report = PerformanceReport(
            report_type=request_data.report_type,
            title=report_data["title"],
            period_start=request_data.period_start,
            period_end=request_data.period_end,
            student_id=request_data.student_id,
            mentor_id=request_data.mentor_id,
            batch=request_data.batch,
            generated_by_role=generated_by_role,
            generated_by_user_id=generated_by_user_id,
            summary=report_data["summary"],
            charts=report_data["charts"],
            insights=report_data["insights"],
            supporting_data=report_data[
                "supporting_data"
            ]
        )

        try:
            db.add(saved_report)
            db.commit()
            db.refresh(saved_report)

        except Exception:
            db.rollback()
            raise

        return saved_report

    @staticmethod
    def get_report_by_id(
        db: Session,
        report_id: int
    ) -> PerformanceReport | None:
        return (
            db.query(PerformanceReport)
            .filter(
                PerformanceReport.id == report_id
            )
            .first()
        )

    @staticmethod
    def get_reports(
        db: Session,
        limit: int = 50,
        report_type: str | None = None
    ) -> list[PerformanceReport]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        query = db.query(
            PerformanceReport
        )

        if report_type:
            query = query.filter(
                PerformanceReport.report_type
                == report_type
            )

        return (
            query.order_by(
                PerformanceReport.generated_at.desc(),
                PerformanceReport.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def build_weekly_engineering_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        students = (
            ReportDashboardService
            ._get_filtered_students(
                db=db,
                batch=request_data.batch,
                mentor_id=request_data.mentor_id,
                student_id=request_data.student_id
            )
        )

        student_ids = [
            student.id
            for student in students
        ]

        latest_scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=request_data.period_end
            )
        )

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id.in_(
                    student_ids or [-1]
                ),
                DailyActivity.activity_date
                >= request_data.period_start,
                DailyActivity.activity_date
                <= request_data.period_end
            )
            .all()
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.student_id.in_(
                    student_ids or [-1]
                ),
                Task.start_date
                >= request_data.period_start,
                Task.start_date
                <= request_data.period_end
            )
            .all()
        )

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id.in_(
                    student_ids or [-1]
                ),
                Attendance.date
                >= request_data.period_start,
                Attendance.date
                <= request_data.period_end
            )
            .all()
        )

        scored_students = len(
            latest_scores
        )

        average_engineering_score = (
            sum(
                float(
                    record.final_engineering_score
                )
                for record in latest_scores.values()
            )
            / scored_students
            if scored_students
            else 0.0
        )

        present_records = sum(
            1
            for record in attendance_records
            if str(record.status).lower()
            == "present"
        )

        attendance_rate = (
            present_records
            / len(attendance_records)
            * 100
            if attendance_records
            else 0.0
        )

        completed_tasks = sum(
            1
            for task in tasks
            if task.status == "Approved"
        )

        task_completion_rate = (
            completed_tasks
            / len(tasks)
            * 100
            if tasks
            else 0.0
        )

        active_students = len({
            activity.student_id
            for activity in activities
        })

        top_students = (
            ReportDashboardService
            ._format_top_students(
                students=students,
                score_records=latest_scores,
                limit=5,
                reverse=True
            )
        )

        weak_students = (
            ReportDashboardService
            ._format_top_students(
                students=students,
                score_records=latest_scores,
                limit=5,
                reverse=False
            )
        )

        insights = []

        if attendance_rate < 70:
            insights.append(
                "Weekly attendance is below the expected level."
            )

        if task_completion_rate < 60:
            insights.append(
                "Task completion requires additional mentor attention."
            )

        if active_students < len(students):
            insights.append(
                "Some interns did not submit a daily activity during the selected period."
            )

        if average_engineering_score >= 75:
            insights.append(
                "Overall weekly engineering performance is strong."
            )

        return {
            "title": "Weekly Engineering Report",
            "summary": {
                "total_students": len(students),
                "students_scored": scored_students,
                "average_engineering_score": round(
                    average_engineering_score,
                    2
                ),
                "attendance_rate": round(
                    attendance_rate,
                    2
                ),
                "daily_active_students": (
                    active_students
                ),
                "total_tasks": len(tasks),
                "approved_tasks": completed_tasks,
                "task_completion_rate": round(
                    task_completion_rate,
                    2
                )
            },
            "charts": [
                {
                    "type": "bar",
                    "title": "Top Engineering Scores",
                    "labels": [
                        item["student_name"]
                        for item in top_students
                    ],
                    "values": [
                        item["engineering_score"]
                        for item in top_students
                    ]
                },
                {
                    "type": "doughnut",
                    "title": "Weekly Task Completion",
                    "labels": [
                        "Approved",
                        "Other"
                    ],
                    "values": [
                        completed_tasks,
                        max(
                            0,
                            len(tasks)
                            - completed_tasks
                        )
                    ]
                }
            ],
            "insights": insights,
            "supporting_data": {
                "top_performers": top_students,
                "weak_performers": weak_students
            }
        }

    @staticmethod
    def build_monthly_growth_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        students = (
            ReportDashboardService
            ._get_filtered_students(
                db=db,
                batch=request_data.batch,
                mentor_id=request_data.mentor_id,
                student_id=request_data.student_id
            )
        )

        student_ids = [
            student.id
            for student in students
        ]

        learning_records = (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id.in_(
                    student_ids or [-1]
                ),
                LearningSpeedRecord.period_end
                >= request_data.period_start,
                LearningSpeedRecord.period_end
                <= request_data.period_end
            )
            .all()
        )

        average_learning_speed = (
            sum(
                float(record.learning_speed_score)
                for record in learning_records
            )
            / len(learning_records)
            if learning_records
            else 0.0
        )

        average_growth = (
            sum(
                float(record.growth_percentage)
                for record in learning_records
            )
            / len(learning_records)
            if learning_records
            else 0.0
        )

        improved_students = sum(
            1
            for record in learning_records
            if record.growth_percentage > 0
        )

        declining_students = sum(
            1
            for record in learning_records
            if record.growth_percentage < 0
        )

        growth_items = []

        student_map = {
            student.id: student
            for student in students
        }

        for record in learning_records:
            student = student_map.get(
                record.student_id
            )

            if not student:
                continue

            growth_items.append({
                "student_id": student.id,
                "student_name": student.name,
                "learning_speed_score": (
                    record.learning_speed_score
                ),
                "growth_percentage": (
                    record.growth_percentage
                ),
                "learning_level": (
                    record.learning_level
                )
            })

        growth_items.sort(
            key=lambda item: (
                item["growth_percentage"]
            ),
            reverse=True
        )

        insights = []

        if average_growth > 10:
            insights.append(
                "The selected group demonstrates strong monthly growth."
            )

        elif average_growth < 0:
            insights.append(
                "Average performance declined during the selected month."
            )

        if declining_students:
            insights.append(
                f"{declining_students} intern(s) require growth intervention."
            )

        return {
            "title": "Monthly Growth Report",
            "summary": {
                "total_students": len(students),
                "learning_records": len(
                    learning_records
                ),
                "average_learning_speed_score": round(
                    average_learning_speed,
                    2
                ),
                "average_growth_percentage": round(
                    average_growth,
                    2
                ),
                "improved_students": (
                    improved_students
                ),
                "declining_students": (
                    declining_students
                )
            },
            "charts": [
                {
                    "type": "line",
                    "title": "Student Growth Percentage",
                    "labels": [
                        item["student_name"]
                        for item in growth_items
                    ],
                    "values": [
                        item["growth_percentage"]
                        for item in growth_items
                    ]
                }
            ],
            "insights": insights,
            "supporting_data": {
                "student_growth": growth_items
            }
        }

    @staticmethod
    def build_mentor_summary_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        mentor = (
            db.query(Mentor)
            .filter(
                Mentor.id
                == request_data.mentor_id
            )
            .first()
        )

        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentor was not found."
            )

        students = (
            db.query(Student)
            .filter(
                Student.mentor_id == mentor.id
            )
            .all()
        )

        student_ids = [
            student.id
            for student in students
        ]

        scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=request_data.period_end
            )
        )

        feedback_count = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.mentor_id
                == mentor.id,
                MentorFeedback.review_date
                >= request_data.period_start,
                MentorFeedback.review_date
                <= request_data.period_end
            )
            .count()
        )

        approved_tasks = (
            db.query(Task)
            .filter(
                Task.assigned_by_mentor_id
                == mentor.id,
                Task.status == "Approved",
                Task.start_date
                >= request_data.period_start,
                Task.start_date
                <= request_data.period_end
            )
            .count()
        )

        average_team_score = (
            sum(
                float(record.final_engineering_score)
                for record in scores.values()
            )
            / len(scores)
            if scores
            else 0.0
        )

        top_students = (
            ReportDashboardService
            ._format_top_students(
                students=students,
                score_records=scores,
                limit=5,
                reverse=True
            )
        )

        weak_students = (
            ReportDashboardService
            ._format_top_students(
                students=students,
                score_records=scores,
                limit=5,
                reverse=False
            )
        )

        return {
            "title": f"Mentor Summary — {mentor.name}",
            "summary": {
                "mentor_id": mentor.id,
                "mentor_name": mentor.name,
                "department": getattr(
                    mentor,
                    "department",
                    None
                ),
                "total_students": len(students),
                "students_scored": len(scores),
                "average_team_score": round(
                    average_team_score,
                    2
                ),
                "feedback_records_submitted": (
                    feedback_count
                ),
                "approved_tasks": approved_tasks
            },
            "charts": [
                {
                    "type": "bar",
                    "title": "Mentor Team Scores",
                    "labels": [
                        item["student_name"]
                        for item in top_students
                    ],
                    "values": [
                        item["engineering_score"]
                        for item in top_students
                    ]
                }
            ],
            "insights": [
                (
                    "Mentor team performance is strong."
                    if average_team_score >= 75
                    else
                    "The mentor team requires additional performance support."
                )
            ],
            "supporting_data": {
                "top_performers": top_students,
                "weak_performers": weak_students
            }
        }

    @staticmethod
    def build_team_performance_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        students = (
            ReportDashboardService
            ._get_filtered_students(
                db=db,
                batch=request_data.batch,
                mentor_id=request_data.mentor_id
            )
        )

        student_ids = [
            student.id
            for student in students
        ]

        scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=request_data.period_end
            )
        )

        level_counts = {
            "Excellent": 0,
            "Good": 0,
            "Average": 0,
            "Weak": 0,
            "Insufficient Data": 0
        }

        for record in scores.values():
            level_counts[
                record.performance_level
            ] = (
                level_counts.get(
                    record.performance_level,
                    0
                )
                + 1
            )

        average_score = (
            sum(
                float(record.final_engineering_score)
                for record in scores.values()
            )
            / len(scores)
            if scores
            else 0.0
        )

        return {
            "title": "Team Performance Report",
            "summary": {
                "total_students": len(students),
                "students_scored": len(scores),
                "average_engineering_score": round(
                    average_score,
                    2
                ),
                "performance_distribution": (
                    level_counts
                )
            },
            "charts": [
                {
                    "type": "pie",
                    "title": "Performance Distribution",
                    "labels": list(
                        level_counts.keys()
                    ),
                    "values": list(
                        level_counts.values()
                    )
                }
            ],
            "insights": [
                (
                    "Team engineering performance is above the expected threshold."
                    if average_score >= 70
                    else
                    "Team engineering performance requires improvement."
                )
            ],
            "supporting_data": {
                "top_performers": (
                    ReportDashboardService
                    ._format_top_students(
                        students=students,
                        score_records=scores,
                        limit=10,
                        reverse=True
                    )
                )
            }
        }

    @staticmethod
    def build_technology_performance_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        technology = (
            request_data.technology
            or ""
        ).strip()

        case_studies = (
            db.query(CaseStudy)
            .filter(
                func.lower(
                    CaseStudy.technology
                )
                == technology.lower(),
                CaseStudy.start_date
                >= request_data.period_start,
                CaseStudy.start_date
                <= request_data.period_end
            )
            .all()
        )

        total = len(case_studies)

        approved = sum(
            1
            for item in case_studies
            if item.status == "Approved"
        )

        failed = sum(
            1
            for item in case_studies
            if item.status == "Failed"
        )

        overdue = sum(
            1
            for item in case_studies
            if item.status == "Overdue"
        )

        scores = [
            float(item.final_score)
            for item in case_studies
            if item.final_score is not None
        ]

        average_score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        completion_rate = (
            approved / total * 100
            if total
            else 0.0
        )

        failure_rate = (
            failed / total * 100
            if total
            else 0.0
        )

        return {
            "title": (
                f"Technology Performance — {technology}"
            ),
            "summary": {
                "technology": technology,
                "total_case_studies": total,
                "approved_case_studies": approved,
                "failed_case_studies": failed,
                "overdue_case_studies": overdue,
                "average_score": round(
                    average_score,
                    2
                ),
                "completion_rate": round(
                    completion_rate,
                    2
                ),
                "failure_rate": round(
                    failure_rate,
                    2
                )
            },
            "charts": [
                {
                    "type": "doughnut",
                    "title": (
                        f"{technology} Case-Study Results"
                    ),
                    "labels": [
                        "Approved",
                        "Failed",
                        "Overdue",
                        "Other"
                    ],
                    "values": [
                        approved,
                        failed,
                        overdue,
                        max(
                            0,
                            total
                            - approved
                            - failed
                            - overdue
                        )
                    ]
                }
            ],
            "insights": [
                (
                    f"{technology} is performing well."
                    if average_score >= 70
                    and failure_rate < 30
                    else
                    f"{technology} requires curriculum or mentor review."
                )
            ],
            "supporting_data": {
                "technology": technology
            }
        }

    @staticmethod
    def build_productivity_trends_report(
        db: Session,
        request_data: PerformanceReportGenerateRequest
    ) -> dict[str, Any]:
        students = (
            ReportDashboardService
            ._get_filtered_students(
                db=db,
                batch=request_data.batch,
                mentor_id=request_data.mentor_id,
                student_id=request_data.student_id
            )
        )

        student_ids = [
            student.id
            for student in students
        ]

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id.in_(
                    student_ids or [-1]
                ),
                DailyActivity.activity_date
                >= request_data.period_start,
                DailyActivity.activity_date
                <= request_data.period_end
            )
            .all()
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.student_id.in_(
                    student_ids or [-1]
                ),
                Task.start_date
                >= request_data.period_start,
                Task.start_date
                <= request_data.period_end
            )
            .all()
        )

        daily_data: dict[
            str,
            dict[str, float]
        ] = defaultdict(
            lambda: {
                "activity_records": 0,
                "hours_worked": 0.0,
                "tasks_completed": 0
            }
        )

        current_date = (
            request_data.period_start
        )

        while (
            current_date
            <= request_data.period_end
        ):
            daily_data[
                current_date.isoformat()
            ]
            current_date += timedelta(days=1)

        for activity in activities:
            date_key = (
                activity.activity_date.isoformat()
            )

            daily_data[
                date_key
            ]["activity_records"] += 1

            daily_data[
                date_key
            ]["hours_worked"] += float(
                activity.hours_worked or 0
            )

        for task in tasks:
            if (
                task.status == "Approved"
                and task.completed_at
            ):
                date_key = (
                    task.completed_at.date()
                    .isoformat()
                )

                if date_key in daily_data:
                    daily_data[
                        date_key
                    ]["tasks_completed"] += 1

        trend_items = []

        for date_key in sorted(
            daily_data.keys()
        ):
            values = daily_data[date_key]

            trend_items.append({
                "date": date_key,
                "activity_records": int(
                    values["activity_records"]
                ),
                "hours_worked": round(
                    values["hours_worked"],
                    2
                ),
                "tasks_completed": int(
                    values["tasks_completed"]
                )
            })

        total_hours = sum(
            item["hours_worked"]
            for item in trend_items
        )

        return {
            "title": "Productivity Trends Report",
            "summary": {
                "total_students": len(students),
                "total_activity_records": len(
                    activities
                ),
                "total_hours_worked": round(
                    total_hours,
                    2
                ),
                "approved_tasks": sum(
                    1
                    for task in tasks
                    if task.status == "Approved"
                )
            },
            "charts": [
                {
                    "type": "line",
                    "title": "Daily Hours Worked",
                    "labels": [
                        item["date"]
                        for item in trend_items
                    ],
                    "values": [
                        item["hours_worked"]
                        for item in trend_items
                    ]
                },
                {
                    "type": "line",
                    "title": "Daily Activity Records",
                    "labels": [
                        item["date"]
                        for item in trend_items
                    ],
                    "values": [
                        item["activity_records"]
                        for item in trend_items
                    ]
                }
            ],
            "insights": [
                (
                    "Productivity data is available for the selected period."
                    if activities
                    else
                    "No productivity data was found for the selected period."
                )
            ],
            "supporting_data": {
                "daily_trends": trend_items
            }
        }

    @staticmethod
    def get_student_dashboard(
        db: Session,
        student: Student
    ) -> dict[str, Any]:
        engineering_record = (
            db.query(
                EngineeringPerformanceRecord
            )
            .filter(
                EngineeringPerformanceRecord.student_id
                == student.id
            )
            .order_by(
                EngineeringPerformanceRecord
                .period_end
                .desc(),
                EngineeringPerformanceRecord
                .id
                .desc()
            )
            .first()
        )

        github_report = (
            db.query(GitHubReport)
            .filter(
                GitHubReport.student_id
                == student.id
            )
            .order_by(
                GitHubReport.generated_at.desc(),
                GitHubReport.id.desc()
            )
            .first()
        )

        learning_record = (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id
                == student.id
            )
            .order_by(
                LearningSpeedRecord.period_end.desc(),
                LearningSpeedRecord.id.desc()
            )
            .first()
        )

        feedback = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.student_id
                == student.id
            )
            .order_by(
                MentorFeedback.review_date.desc(),
                MentorFeedback.id.desc()
            )
            .first()
        )

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id
                == student.id
            )
            .all()
        )

        present = sum(
            1
            for record in attendance_records
            if str(record.status).lower()
            == "present"
        )

        attendance_rate = (
            present
            / len(attendance_records)
            * 100
            if attendance_records
            else 0.0
        )

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id
                == student.id
            )
            .order_by(
                DailyActivity.activity_date.desc()
            )
            .limit(7)
            .all()
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.student_id == student.id
            )
            .all()
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.student_id
                == student.id
            )
            .all()
        )

        credits = (
            db.query(EngineeringCredit)
            .filter(
                EngineeringCredit.student_id
                == student.id
            )
            .all()
        )

        recommendations = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.student_id
                == student.id,
                AIRecommendation.status.in_([
                    "Generated",
                    "Pending Approval",
                    "Approved"
                ])
            )
            .order_by(
                AIRecommendation.priority_score.desc()
            )
            .limit(10)
            .all()
        )

        net_credits = sum(
            credit.credit_value
            for credit in credits
        )

        approved_tasks = sum(
            1
            for task in tasks
            if task.status == "Approved"
        )

        approved_case_studies = sum(
            1
            for item in case_studies
            if item.status == "Approved"
        )

        strong_areas = (
            engineering_record.strong_areas
            if engineering_record
            else []
        )

        weak_areas = (
            engineering_record.weak_areas
            if engineering_record
            else []
        )

        next_action = (
            recommendations[0]
            .recommendation_type
            if recommendations
            else
            "Continue the current learning plan"
        )

        return {
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "batch": student.batch,
                "github_username": (
                    student.github_username
                ),
                "mentor_id": student.mentor_id
            },
            "engineering_performance": {
                "score": (
                    engineering_record
                    .final_engineering_score
                    if engineering_record
                    else 0.0
                ),
                "performance_level": (
                    engineering_record
                    .performance_level
                    if engineering_record
                    else "Insufficient Data"
                ),
                "placement_readiness": (
                    engineering_record
                    .placement_readiness
                    if engineering_record
                    else False
                ),
                "promotion_readiness": (
                    engineering_record
                    .promotion_readiness
                    if engineering_record
                    else False
                ),
                "client_project_readiness": (
                    engineering_record
                    .client_project_readiness
                    if engineering_record
                    else False
                )
            },
            "skill_growth": {
                "learning_speed_score": (
                    learning_record
                    .learning_speed_score
                    if learning_record
                    else 0.0
                ),
                "growth_percentage": (
                    learning_record
                    .growth_percentage
                    if learning_record
                    else 0.0
                ),
                "learning_level": (
                    learning_record.learning_level
                    if learning_record
                    else "Insufficient Data"
                )
            },
            "attendance": {
                "total_records": len(
                    attendance_records
                ),
                "present_records": present,
                "attendance_rate": round(
                    attendance_rate,
                    2
                )
            },
            "github": {
                "final_score": (
                    github_report.final_github_score
                    if github_report
                    else 0.0
                ),
                "performance_level": (
                    github_report.performance_level
                    if github_report
                    else None
                ),
                "repositories_analyzed": (
                    github_report
                    .repositories_analyzed
                    if github_report
                    else 0
                )
            },
            "daily_activity": {
                "recent_records": len(activities),
                "verified_records": sum(
                    1
                    for item in activities
                    if item.is_verified
                ),
                "total_hours": round(
                    sum(
                        float(
                            item.hours_worked or 0
                        )
                        for item in activities
                    ),
                    2
                )
            },
            "tasks": {
                "total": len(tasks),
                "approved": approved_tasks,
                "pending": sum(
                    1
                    for task in tasks
                    if task.status not in {
                        "Approved",
                        "Cancelled"
                    }
                )
            },
            "case_studies": {
                "total": len(case_studies),
                "approved": approved_case_studies,
                "average_score": round(
                    (
                        sum(
                            float(
                                item.final_score
                            )
                            for item in case_studies
                            if item.final_score
                            is not None
                        )
                        / len([
                            item
                            for item in case_studies
                            if item.final_score
                            is not None
                        ])
                    )
                    if any(
                        item.final_score
                        is not None
                        for item in case_studies
                    )
                    else 0.0,
                    2
                )
            },
            "mentor_feedback": {
                "overall_score": (
                    feedback.overall_feedback_score
                    if feedback
                    else 0.0
                ),
                "communication_score": (
                    feedback.communication_score
                    if feedback
                    else 0.0
                ),
                "leadership_potential": (
                    feedback.leadership_potential
                    if feedback
                    else None
                ),
                "general_feedback": (
                    feedback.general_feedback
                    if feedback
                    else None
                )
            },
            "engineering_credits": {
                "net_credits": net_credits,
                "transactions": len(credits)
            },
            "ai_recommendations": [
                {
                    "id": item.id,
                    "type": (
                        item.recommendation_type
                    ),
                    "priority": (
                        item.priority_level
                    ),
                    "confidence": (
                        item.confidence_score
                    ),
                    "status": item.status
                }
                for item in recommendations
            ],
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "next_suggested_action": (
                next_action
            )
        }

    @staticmethod
    def get_mentor_dashboard(
        db: Session,
        mentor: Mentor
    ) -> dict[str, Any]:
        students = (
            db.query(Student)
            .filter(
                Student.mentor_id == mentor.id
            )
            .all()
        )

        student_ids = [
            student.id
            for student in students
        ]

        scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=date.today()
            )
        )

        inactive_students = (
            ReportDashboardService
            ._get_inactive_students(
                db=db,
                student_ids=student_ids,
                inactivity_days=3
            )
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.assigned_by_mentor_id
                == mentor.id
            )
            .all()
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.assigned_by_mentor_id
                == mentor.id
            )
            .all()
        )

        recommendations = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.mentor_id
                == mentor.id,
                AIRecommendation.status.in_([
                    "Generated",
                    "Pending Approval",
                    "Approved"
                ])
            )
            .order_by(
                AIRecommendation.priority_score.desc()
            )
            .limit(20)
            .all()
        )

        average_score = (
            sum(
                float(record.final_engineering_score)
                for record in scores.values()
            )
            / len(scores)
            if scores
            else 0.0
        )

        return {
            "mentor": {
                "id": mentor.id,
                "name": mentor.name,
                "email": mentor.email,
                "department": getattr(
                    mentor,
                    "department",
                    None
                )
            },
            "team_overview": {
                "total_students": len(students),
                "students_scored": len(scores),
                "average_engineering_score": round(
                    average_score,
                    2
                ),
                "placement_ready": sum(
                    1
                    for record in scores.values()
                    if record.placement_readiness
                ),
                "client_project_ready": sum(
                    1
                    for record in scores.values()
                    if record.client_project_readiness
                )
            },
            "top_performers": (
                ReportDashboardService
                ._format_top_students(
                    students=students,
                    score_records=scores,
                    limit=5,
                    reverse=True
                )
            ),
            "weak_performers": (
                ReportDashboardService
                ._format_top_students(
                    students=students,
                    score_records=scores,
                    limit=5,
                    reverse=False
                )
            ),
            "inactive_students": (
                inactive_students
            ),
            "pending_tasks": [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "student_id": task.student_id,
                    "status": task.status,
                    "due_date": task.due_date
                }
                for task in tasks
                if task.status not in {
                    "Approved",
                    "Cancelled"
                }
            ][:20],
            "pending_case_studies": [
                {
                    "case_study_id": item.id,
                    "title": item.title,
                    "student_id": item.student_id,
                    "status": item.status,
                    "due_date": item.due_date
                }
                for item in case_studies
                if item.status not in {
                    "Approved",
                    "Failed",
                    "Cancelled"
                }
            ][:20],
            "pending_recommendations": [
                {
                    "id": item.id,
                    "student_id": item.student_id,
                    "type": (
                        item.recommendation_type
                    ),
                    "priority": (
                        item.priority_level
                    ),
                    "status": item.status
                }
                for item in recommendations
            ],
            "team_growth": {
                "average_engineering_score": round(
                    average_score,
                    2
                ),
                "strong_students": sum(
                    1
                    for record in scores.values()
                    if record.final_engineering_score
                    >= 75
                ),
                "students_needing_support": sum(
                    1
                    for record in scores.values()
                    if record.final_engineering_score
                    < 60
                )
            }
        }

    @staticmethod
    def get_admin_dashboard(
        db: Session
    ) -> dict[str, Any]:
        students = db.query(Student).all()

        student_ids = [
            student.id
            for student in students
        ]

        scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=date.today()
            )
        )

        performance_distribution = {
            "Excellent": 0,
            "Good": 0,
            "Average": 0,
            "Weak": 0,
            "Insufficient Data": 0
        }

        for record in scores.values():
            performance_distribution[
                record.performance_level
            ] = (
                performance_distribution.get(
                    record.performance_level,
                    0
                )
                + 1
            )

        average_score = (
            sum(
                float(record.final_engineering_score)
                for record in scores.values()
            )
            / len(scores)
            if scores
            else 0.0
        )

        batch_comparison = (
            ReportDashboardService
            ._get_batch_comparison(
                students=students,
                score_records=scores
            )
        )

        technology_performance = (
            ReportDashboardService
            ._get_all_technology_performance(
                db=db
            )
        )

        mentor_performance = (
            ReportDashboardService
            ._get_mentor_performance(
                db=db,
                students=students,
                score_records=scores
            )
        )

        recommendation_summary = (
            ReportDashboardService
            ._get_recommendation_summary(
                db=db
            )
        )

        inactive_students = (
            ReportDashboardService
            ._get_inactive_students(
                db=db,
                student_ids=student_ids,
                inactivity_days=3
            )
        )

        return {
            "internship_health": {
                "total_students": len(students),
                "students_scored": len(scores),
                "average_engineering_score": round(
                    average_score,
                    2
                ),
                "active_students": max(
                    0,
                    len(students)
                    - len(inactive_students)
                ),
                "inactive_students": len(
                    inactive_students
                ),
                "health_status": (
                    "Healthy"
                    if average_score >= 70
                    else
                    "Needs Attention"
                )
            },
            "performance_distribution": (
                performance_distribution
            ),
            "readiness": {
                "placement_ready": sum(
                    1
                    for record in scores.values()
                    if record.placement_readiness
                ),
                "promotion_ready": sum(
                    1
                    for record in scores.values()
                    if record.promotion_readiness
                ),
                "client_project_ready": sum(
                    1
                    for record in scores.values()
                    if record.client_project_readiness
                ),
                "certificate_eligible": sum(
                    1
                    for record in scores.values()
                    if record.certificate_eligibility
                )
            },
            "batch_comparison": batch_comparison,
            "technology_performance": (
                technology_performance
            ),
            "mentor_performance": (
                mentor_performance
            ),
            "top_performers": (
                ReportDashboardService
                ._format_top_students(
                    students=students,
                    score_records=scores,
                    limit=10,
                    reverse=True
                )
            ),
            "weak_performers": (
                ReportDashboardService
                ._format_top_students(
                    students=students,
                    score_records=scores,
                    limit=10,
                    reverse=False
                )
            ),
            "inactive_students": (
                inactive_students[:20]
            ),
            "recommendation_summary": (
                recommendation_summary
            ),
            "productivity_trends": (
                ReportDashboardService
                ._get_recent_productivity(
                    db=db,
                    days=7
                )
            )
        }

    @staticmethod
    def get_ceo_dashboard(
        db: Session
    ) -> dict[str, Any]:
        admin_dashboard = (
            ReportDashboardService
            .get_admin_dashboard(
                db=db
            )
        )

        students = db.query(Student).all()

        student_ids = [
            student.id
            for student in students
        ]

        scores = (
            ReportDashboardService
            ._get_latest_engineering_records(
                db=db,
                student_ids=student_ids,
                period_end=date.today()
            )
        )

        top_interns = (
            ReportDashboardService
            ._format_top_students(
                students=students,
                score_records=scores,
                limit=10,
                reverse=True
            )
        )

        mentor_performance = (
            admin_dashboard[
                "mentor_performance"
            ]
        )

        mentors_needing_support = [
            item
            for item in mentor_performance
            if item["average_team_score"] < 60
            or item["weak_students"] > 0
        ]

        technology_performance = (
            admin_dashboard[
                "technology_performance"
            ]
        )

        underperforming_technologies = [
            item
            for item in technology_performance
            if item["average_score"] < 60
            or item["failure_rate"] >= 30
        ]

        risks = []

        inactive_count = (
            admin_dashboard[
                "internship_health"
            ]["inactive_students"]
        )

        weak_count = (
            admin_dashboard[
                "performance_distribution"
            ].get("Weak", 0)
        )

        if inactive_count:
            risks.append({
                "risk": "Intern Inactivity",
                "severity": (
                    "High"
                    if inactive_count >= 5
                    else "Medium"
                ),
                "affected_students": (
                    inactive_count
                )
            })

        if weak_count:
            risks.append({
                "risk": "Weak Engineering Performance",
                "severity": (
                    "High"
                    if weak_count >= 5
                    else "Medium"
                ),
                "affected_students": weak_count
            })

        strategic_insights = []

        placement_ready = (
            admin_dashboard[
                "readiness"
            ]["placement_ready"]
        )

        client_ready = (
            admin_dashboard[
                "readiness"
            ]["client_project_ready"]
        )

        strategic_insights.append(
            f"{placement_ready} intern(s) are currently ready for placement review."
        )

        strategic_insights.append(
            f"{client_ready} intern(s) are ready for supervised client projects."
        )

        if underperforming_technologies:
            strategic_insights.append(
                "One or more technologies require curriculum or mentor intervention."
            )

        return {
            "executive_summary": {
                "total_interns": (
                    admin_dashboard[
                        "internship_health"
                    ]["total_students"]
                ),
                "average_engineering_score": (
                    admin_dashboard[
                        "internship_health"
                    ][
                        "average_engineering_score"
                    ]
                ),
                "internship_health_status": (
                    admin_dashboard[
                        "internship_health"
                    ]["health_status"]
                ),
                "total_mentors": (
                    db.query(Mentor).count()
                )
            },
            "hiring_readiness": (
                admin_dashboard["readiness"]
            ),
            "internship_health": (
                admin_dashboard[
                    "internship_health"
                ]
            ),
            "top_interns": top_interns,
            "mentors_needing_support": (
                mentors_needing_support
            ),
            "underperforming_technologies": (
                underperforming_technologies
            ),
            "batch_performance": (
                admin_dashboard[
                    "batch_comparison"
                ]
            ),
            "risks": risks,
            "strategic_insights": (
                strategic_insights
            ),
            "charts": [
                {
                    "type": "bar",
                    "title": "Top 10 Interns",
                    "labels": [
                        item["student_name"]
                        for item in top_interns
                    ],
                    "values": [
                        item["engineering_score"]
                        for item in top_interns
                    ]
                },
                {
                    "type": "doughnut",
                    "title": "Intern Readiness",
                    "labels": [
                        "Placement Ready",
                        "Client Project Ready",
                        "Promotion Ready"
                    ],
                    "values": [
                        admin_dashboard[
                            "readiness"
                        ]["placement_ready"],
                        admin_dashboard[
                            "readiness"
                        ][
                            "client_project_ready"
                        ],
                        admin_dashboard[
                            "readiness"
                        ]["promotion_ready"]
                    ]
                }
            ]
        }

    @staticmethod
    def _get_filtered_students(
        db: Session,
        batch: str | None = None,
        mentor_id: int | None = None,
        student_id: int | None = None
    ) -> list[Student]:
        query = db.query(Student)

        if batch:
            query = query.filter(
                Student.batch == batch
            )

        if mentor_id:
            query = query.filter(
                Student.mentor_id == mentor_id
            )

        if student_id:
            query = query.filter(
                Student.id == student_id
            )

        return query.all()

    @staticmethod
    def _get_latest_engineering_records(
        db: Session,
        student_ids: list[int],
        period_end: date
    ) -> dict[
        int,
        EngineeringPerformanceRecord
    ]:
        if not student_ids:
            return {}

        records = (
            db.query(
                EngineeringPerformanceRecord
            )
            .filter(
                EngineeringPerformanceRecord.student_id
                .in_(student_ids),
                EngineeringPerformanceRecord.period_end
                <= period_end
            )
            .order_by(
                EngineeringPerformanceRecord
                .period_end
                .desc(),
                EngineeringPerformanceRecord
                .id
                .desc()
            )
            .all()
        )

        latest_records = {}

        for record in records:
            if record.student_id not in latest_records:
                latest_records[
                    record.student_id
                ] = record

        return latest_records

    @staticmethod
    def _format_top_students(
        students: list[Student],
        score_records: dict[
            int,
            EngineeringPerformanceRecord
        ],
        limit: int,
        reverse: bool
    ) -> list[dict[str, Any]]:
        student_map = {
            student.id: student
            for student in students
        }

        items = []

        for student_id, record in (
            score_records.items()
        ):
            student = student_map.get(
                student_id
            )

            if not student:
                continue

            items.append({
                "student_id": student.id,
                "student_name": student.name,
                "batch": student.batch,
                "engineering_score": (
                    record.final_engineering_score
                ),
                "performance_level": (
                    record.performance_level
                ),
                "placement_readiness": (
                    record.placement_readiness
                ),
                "client_project_readiness": (
                    record.client_project_readiness
                )
            })

        items.sort(
            key=lambda item: (
                item["engineering_score"]
            ),
            reverse=reverse
        )

        return items[:limit]

    @staticmethod
    def _get_inactive_students(
        db: Session,
        student_ids: list[int],
        inactivity_days: int
    ) -> list[dict[str, Any]]:
        if not student_ids:
            return []

        cutoff_date = (
            date.today()
            - timedelta(
                days=inactivity_days
            )
        )

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id.in_(
                    student_ids
                )
            )
            .order_by(
                DailyActivity.activity_date.desc()
            )
            .all()
        )

        latest_activity = {}

        for activity in activities:
            if (
                activity.student_id
                not in latest_activity
            ):
                latest_activity[
                    activity.student_id
                ] = activity.activity_date

        students = (
            db.query(Student)
            .filter(
                Student.id.in_(
                    student_ids
                )
            )
            .all()
        )

        results = []

        for student in students:
            last_date = latest_activity.get(
                student.id
            )

            if (
                last_date is None
                or last_date <= cutoff_date
            ):
                results.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "batch": student.batch,
                    "last_activity_date": last_date,
                    "days_inactive": (
                        (
                            date.today()
                            - last_date
                        ).days
                        if last_date
                        else None
                    )
                })

        return results

    @staticmethod
    def _get_batch_comparison(
        students: list[Student],
        score_records: dict[
            int,
            EngineeringPerformanceRecord
        ]
    ) -> list[dict[str, Any]]:
        batches = defaultdict(
            lambda: {
                "students": 0,
                "scores": [],
                "placement_ready": 0
            }
        )

        for student in students:
            batch_name = (
                student.batch
                or "Unassigned"
            )

            batches[
                batch_name
            ]["students"] += 1

            record = score_records.get(
                student.id
            )

            if record:
                batches[
                    batch_name
                ]["scores"].append(
                    float(
                        record.final_engineering_score
                    )
                )

                if record.placement_readiness:
                    batches[
                        batch_name
                    ]["placement_ready"] += 1

        results = []

        for batch_name, data in batches.items():
            scores = data["scores"]

            results.append({
                "batch": batch_name,
                "total_students": (
                    data["students"]
                ),
                "students_scored": len(scores),
                "average_score": round(
                    (
                        sum(scores)
                        / len(scores)
                        if scores
                        else 0.0
                    ),
                    2
                ),
                "placement_ready": (
                    data["placement_ready"]
                )
            })

        results.sort(
            key=lambda item: (
                item["average_score"]
            ),
            reverse=True
        )

        return results

    @staticmethod
    def _get_all_technology_performance(
        db: Session
    ) -> list[dict[str, Any]]:
        case_studies = (
            db.query(CaseStudy)
            .all()
        )

        technology_data = defaultdict(
            lambda: {
                "total": 0,
                "scores": [],
                "approved": 0,
                "failed": 0
            }
        )

        for item in case_studies:
            technology = (
                item.technology
                or "Unknown"
            )

            data = technology_data[
                technology
            ]

            data["total"] += 1

            if item.final_score is not None:
                data["scores"].append(
                    float(item.final_score)
                )

            if item.status == "Approved":
                data["approved"] += 1

            if item.status == "Failed":
                data["failed"] += 1

        results = []

        for technology, data in (
            technology_data.items()
        ):
            total = data["total"]
            scores = data["scores"]

            results.append({
                "technology": technology,
                "total_case_studies": total,
                "average_score": round(
                    (
                        sum(scores)
                        / len(scores)
                        if scores
                        else 0.0
                    ),
                    2
                ),
                "completion_rate": round(
                    (
                        data["approved"]
                        / total
                        * 100
                        if total
                        else 0.0
                    ),
                    2
                ),
                "failure_rate": round(
                    (
                        data["failed"]
                        / total
                        * 100
                        if total
                        else 0.0
                    ),
                    2
                )
            })

        results.sort(
            key=lambda item: (
                item["average_score"]
            ),
            reverse=True
        )

        return results

    @staticmethod
    def _get_mentor_performance(
        db: Session,
        students: list[Student],
        score_records: dict[
            int,
            EngineeringPerformanceRecord
        ]
    ) -> list[dict[str, Any]]:
        mentors = db.query(Mentor).all()

        results = []

        for mentor in mentors:
            mentor_students = [
                student
                for student in students
                if student.mentor_id == mentor.id
            ]

            records = [
                score_records[student.id]
                for student in mentor_students
                if student.id in score_records
            ]

            average_score = (
                sum(
                    float(
                        record.final_engineering_score
                    )
                    for record in records
                )
                / len(records)
                if records
                else 0.0
            )

            results.append({
                "mentor_id": mentor.id,
                "mentor_name": mentor.name,
                "department": getattr(
                    mentor,
                    "department",
                    None
                ),
                "total_students": len(
                    mentor_students
                ),
                "students_scored": len(records),
                "average_team_score": round(
                    average_score,
                    2
                ),
                "top_students": sum(
                    1
                    for record in records
                    if record.final_engineering_score
                    >= 75
                ),
                "weak_students": sum(
                    1
                    for record in records
                    if record.final_engineering_score
                    < 60
                )
            })

        results.sort(
            key=lambda item: (
                item["average_team_score"]
            ),
            reverse=True
        )

        return results

    @staticmethod
    def _get_recommendation_summary(
        db: Session
    ) -> dict[str, Any]:
        recommendations = (
            db.query(AIRecommendation)
            .all()
        )

        return {
            "total": len(recommendations),
            "generated": sum(
                1
                for item in recommendations
                if item.status == "Generated"
            ),
            "pending_approval": sum(
                1
                for item in recommendations
                if item.status
                == "Pending Approval"
            ),
            "approved": sum(
                1
                for item in recommendations
                if item.status == "Approved"
            ),
            "completed": sum(
                1
                for item in recommendations
                if item.status == "Completed"
            ),
            "critical": sum(
                1
                for item in recommendations
                if item.priority_level
                == "Critical"
            )
        }

    @staticmethod
    def _get_recent_productivity(
        db: Session,
        days: int
    ) -> list[dict[str, Any]]:
        start_date = (
            date.today()
            - timedelta(
                days=days - 1
            )
        )

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.activity_date
                >= start_date
            )
            .all()
        )

        results = []

        for index in range(days):
            current_date = (
                start_date
                + timedelta(days=index)
            )

            daily_activities = [
                item
                for item in activities
                if item.activity_date
                == current_date
            ]

            results.append({
                "date": current_date,
                "activity_records": len(
                    daily_activities
                ),
                "active_students": len({
                    item.student_id
                    for item in daily_activities
                }),
                "hours_worked": round(
                    sum(
                        float(
                            item.hours_worked
                            or 0
                        )
                        for item
                        in daily_activities
                    ),
                    2
                )
            })

        return results