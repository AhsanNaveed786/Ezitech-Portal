from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    Admin,
    Attendance,
    CaseStudy,
    DailyActivity,
    EngineeringCredit,
    EngineeringPerformanceRecord,
    GitHubReport,
    LearningSpeedRecord,
    Mentor,
    MentorFeedback,
    Student,
    Task
)
from backend.schemas import (
    EngineeringScoreGenerateRequest
)


class EngineeringScoreService:

    COMPONENT_WEIGHTS = {
        "attendance": 0.10,
        "github": 0.15,
        "daily_activity": 0.10,
        "tasks": 0.15,
        "case_studies": 0.15,
        "mentor_feedback": 0.10,
        "communication": 0.10,
        "deadline_compliance": 0.05,
        "learning_speed": 0.05,
        "engineering_credits": 0.05
    }

    COMPONENT_LABELS = {
        "attendance": "Attendance",
        "github": "GitHub Performance",
        "daily_activity": "Daily Activity",
        "tasks": "Task Performance",
        "case_studies": "Case Study Performance",
        "mentor_feedback": "Mentor Feedback",
        "communication": "Communication",
        "deadline_compliance": "Deadline Compliance",
        "learning_speed": "Learning Speed",
        "engineering_credits": "Engineering Credits"
    }

    @staticmethod
    def generate_score(
        db: Session,
        request_data: EngineeringScoreGenerateRequest,
        mentor: Mentor | None = None,
        admin: Admin | None = None
    ) -> EngineeringPerformanceRecord:
        student = (
            db.query(Student)
            .filter(
                Student.id == request_data.student_id
            )
            .first()
        )

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student was not found."
            )

        if mentor and student.mentor_id != mentor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only generate engineering scores "
                    "for your assigned students."
                )
            )

        existing_record = (
            db.query(EngineeringPerformanceRecord)
            .filter(
                EngineeringPerformanceRecord.student_id
                == student.id,
                EngineeringPerformanceRecord.period_start
                == request_data.period_start,
                EngineeringPerformanceRecord.period_end
                == request_data.period_end
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An engineering score already exists "
                    "for this student and period."
                )
            )

        attendance = (
            EngineeringScoreService
            ._calculate_attendance_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        github = (
            EngineeringScoreService
            ._calculate_github_score(
                db=db,
                student_id=student.id,
                period_end=request_data.period_end
            )
        )

        activity = (
            EngineeringScoreService
            ._calculate_daily_activity_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        tasks = (
            EngineeringScoreService
            ._calculate_task_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        case_studies = (
            EngineeringScoreService
            ._calculate_case_study_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        feedback = (
            EngineeringScoreService
            ._calculate_feedback_scores(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        deadline = (
            EngineeringScoreService
            ._calculate_deadline_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        learning = (
            EngineeringScoreService
            ._calculate_learning_score(
                db=db,
                student_id=student.id,
                period_end=request_data.period_end
            )
        )

        credits = (
            EngineeringScoreService
            ._calculate_credit_score(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        component_results = {
            "attendance": attendance,
            "github": github,
            "daily_activity": activity,
            "tasks": tasks,
            "case_studies": case_studies,
            "mentor_feedback": {
                "score": feedback["mentor_feedback_score"],
                "has_data": feedback["has_data"],
                "details": feedback["details"]
            },
            "communication": {
                "score": feedback["communication_score"],
                "has_data": feedback["has_data"],
                "details": feedback["details"]
            },
            "deadline_compliance": deadline,
            "learning_speed": learning,
            "engineering_credits": credits
        }

        final_score = 0.0
        available_components = 0

        for component_name, result in component_results.items():
            component_score = float(
                result["score"]
            )

            component_score = (
                EngineeringScoreService
                ._clamp_score(component_score)
            )

            final_score += (
                component_score
                * EngineeringScoreService
                .COMPONENT_WEIGHTS[
                    component_name
                ]
            )

            if result["has_data"]:
                available_components += 1

        final_score = round(
            final_score,
            2
        )

        completeness = round(
            available_components
            / len(component_results)
            * 100,
            2
        )

        if completeness < 40:
            performance_level = (
                "Insufficient Data"
            )

        else:
            performance_level = (
                EngineeringScoreService
                ._get_performance_level(
                    final_score
                )
            )

        component_scores = {
            name: round(
                float(result["score"]),
                2
            )
            for name, result
            in component_results.items()
        }

        strong_areas = (
            EngineeringScoreService
            ._get_strong_areas(
                component_scores
            )
        )

        weak_areas = (
            EngineeringScoreService
            ._get_weak_areas(
                component_scores
            )
        )

        readiness = (
            EngineeringScoreService
            ._calculate_readiness(
                final_score=final_score,
                completeness=completeness,
                component_scores=component_scores,
                tasks=tasks,
                case_studies=case_studies,
                feedback=feedback,
                deadline=deadline
            )
        )

        recommendations = (
            EngineeringScoreService
            ._generate_recommendations(
                final_score=final_score,
                completeness=completeness,
                component_scores=component_scores,
                readiness=readiness
            )
        )

        component_details = {
            component_name: {
                "label": (
                    EngineeringScoreService
                    .COMPONENT_LABELS[
                        component_name
                    ]
                ),
                "score": round(
                    float(result["score"]),
                    2
                ),
                "weight_percentage": round(
                    EngineeringScoreService
                    .COMPONENT_WEIGHTS[
                        component_name
                    ]
                    * 100,
                    2
                ),
                "has_data": result["has_data"],
                "details": result["details"]
            }
            for component_name, result
            in component_results.items()
        }

        record = EngineeringPerformanceRecord(
            student_id=student.id,

            generated_by_mentor_id=(
                mentor.id
                if mentor
                else None
            ),

            generated_by_admin_id=(
                admin.id
                if admin
                else None
            ),

            period_start=request_data.period_start,
            period_end=request_data.period_end,

            attendance_score=(
                attendance["score"]
            ),

            github_score=github["score"],

            daily_activity_score=(
                activity["score"]
            ),

            task_score=tasks["score"],

            case_study_score=(
                case_studies["score"]
            ),

            mentor_feedback_score=(
                feedback["mentor_feedback_score"]
            ),

            communication_score=(
                feedback["communication_score"]
            ),

            deadline_compliance_score=(
                deadline["score"]
            ),

            learning_speed_score=(
                learning["score"]
            ),

            engineering_credit_score=(
                credits["score"]
            ),

            final_engineering_score=final_score,
            performance_level=performance_level,

            placement_readiness=(
                readiness["placement_readiness"]
            ),

            promotion_readiness=(
                readiness["promotion_readiness"]
            ),

            client_project_readiness=(
                readiness[
                    "client_project_readiness"
                ]
            ),

            certificate_eligibility=(
                readiness[
                    "certificate_eligibility"
                ]
            ),

            data_completeness_percentage=(
                completeness
            ),

            strong_areas=strong_areas,
            weak_areas=weak_areas,
            recommendations=recommendations,
            component_details=component_details
        )

        try:
            db.add(record)
            db.commit()
            db.refresh(record)

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An engineering score already exists "
                    "for this student and period."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return record

    @staticmethod
    def get_record_by_id(
        db: Session,
        record_id: int
    ) -> EngineeringPerformanceRecord | None:
        return (
            db.query(EngineeringPerformanceRecord)
            .filter(
                EngineeringPerformanceRecord.id
                == record_id
            )
            .first()
        )

    @staticmethod
    def get_student_history(
        db: Session,
        student_id: int,
        limit: int = 50
    ) -> list[EngineeringPerformanceRecord]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(EngineeringPerformanceRecord)
            .filter(
                EngineeringPerformanceRecord.student_id
                == student_id
            )
            .order_by(
                EngineeringPerformanceRecord
                .period_end
                .desc(),
                EngineeringPerformanceRecord
                .id
                .desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_latest_student_score(
        db: Session,
        student_id: int
    ) -> EngineeringPerformanceRecord | None:
        return (
            db.query(EngineeringPerformanceRecord)
            .filter(
                EngineeringPerformanceRecord.student_id
                == student_id
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

    @staticmethod
    def get_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        latest_subquery = (
            db.query(
                EngineeringPerformanceRecord
                .student_id
                .label("student_id"),

                func.max(
                    EngineeringPerformanceRecord.id
                ).label("latest_record_id")
            )
            .group_by(
                EngineeringPerformanceRecord
                .student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                EngineeringPerformanceRecord,
                Student
            )
            .join(
                latest_subquery,
                EngineeringPerformanceRecord.id
                == latest_subquery.c.latest_record_id
            )
            .join(
                Student,
                Student.id
                == EngineeringPerformanceRecord
                .student_id
            )
            .order_by(
                desc(
                    EngineeringPerformanceRecord
                    .final_engineering_score
                ),
                desc(
                    EngineeringPerformanceRecord
                    .data_completeness_percentage
                )
            )
            .limit(safe_limit)
            .all()
        )

        rankings = []

        for rank, row in enumerate(
            rows,
            start=1
        ):
            record, student = row

            rankings.append({
                "rank": rank,
                "student_id": student.id,
                "student_name": student.name,
                "batch": student.batch,

                "final_engineering_score": (
                    record.final_engineering_score
                ),

                "performance_level": (
                    record.performance_level
                ),

                "placement_readiness": (
                    record.placement_readiness
                ),

                "promotion_readiness": (
                    record.promotion_readiness
                ),

                "client_project_readiness": (
                    record.client_project_readiness
                ),

                "certificate_eligibility": (
                    record.certificate_eligibility
                ),

                "data_completeness_percentage": (
                    record
                    .data_completeness_percentage
                ),

                "period_start": record.period_start,
                "period_end": record.period_end
            })

        return rankings

    @staticmethod
    def get_readiness_students(
        db: Session,
        readiness_type: str
    ) -> list[dict[str, Any]]:
        valid_readiness_types = {
            "placement": "placement_readiness",
            "promotion": "promotion_readiness",
            "client-project": (
                "client_project_readiness"
            ),
            "certificate": (
                "certificate_eligibility"
            )
        }

        field_name = valid_readiness_types.get(
            readiness_type
        )

        if not field_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Readiness type must be placement, "
                    "promotion, client-project or certificate."
                )
            )

        latest_subquery = (
            db.query(
                EngineeringPerformanceRecord
                .student_id
                .label("student_id"),

                func.max(
                    EngineeringPerformanceRecord.id
                ).label("latest_record_id")
            )
            .group_by(
                EngineeringPerformanceRecord
                .student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                EngineeringPerformanceRecord,
                Student
            )
            .join(
                latest_subquery,
                EngineeringPerformanceRecord.id
                == latest_subquery.c.latest_record_id
            )
            .join(
                Student,
                Student.id
                == EngineeringPerformanceRecord
                .student_id
            )
            .filter(
                getattr(
                    EngineeringPerformanceRecord,
                    field_name
                ).is_(True)
            )
            .order_by(
                desc(
                    EngineeringPerformanceRecord
                    .final_engineering_score
                )
            )
            .all()
        )

        return [
            {
                "student_id": student.id,
                "student_name": student.name,
                "batch": student.batch,

                "final_engineering_score": (
                    record.final_engineering_score
                ),

                "performance_level": (
                    record.performance_level
                ),

                "placement_readiness": (
                    record.placement_readiness
                ),

                "promotion_readiness": (
                    record.promotion_readiness
                ),

                "client_project_readiness": (
                    record.client_project_readiness
                ),

                "certificate_eligibility": (
                    record.certificate_eligibility
                ),

                "strong_areas": record.strong_areas,
                "weak_areas": record.weak_areas
            }
            for record, student in rows
        ]

    @staticmethod
    def get_summary(
        db: Session
    ) -> dict[str, Any]:
        latest_subquery = (
            db.query(
                EngineeringPerformanceRecord
                .student_id
                .label("student_id"),

                func.max(
                    EngineeringPerformanceRecord.id
                ).label("latest_record_id")
            )
            .group_by(
                EngineeringPerformanceRecord
                .student_id
            )
            .subquery()
        )

        records = (
            db.query(
                EngineeringPerformanceRecord
            )
            .join(
                latest_subquery,
                EngineeringPerformanceRecord.id
                == latest_subquery.c.latest_record_id
            )
            .all()
        )

        total = len(records)

        def count_level(
            level: str
        ) -> int:
            return sum(
                1
                for record in records
                if record.performance_level == level
            )

        average_score = (
            sum(
                float(
                    record.final_engineering_score
                )
                for record in records
            )
            / total
            if total
            else 0.0
        )

        average_completeness = (
            sum(
                float(
                    record
                    .data_completeness_percentage
                )
                for record in records
            )
            / total
            if total
            else 0.0
        )

        scores = [
            float(record.final_engineering_score)
            for record in records
        ]

        return {
            "total_students_scored": total,

            "excellent_students": count_level(
                "Excellent"
            ),

            "good_students": count_level(
                "Good"
            ),

            "average_students": count_level(
                "Average"
            ),

            "weak_students": count_level(
                "Weak"
            ),

            "insufficient_data_students": (
                count_level(
                    "Insufficient Data"
                )
            ),

            "placement_ready_students": sum(
                1
                for record in records
                if record.placement_readiness
            ),

            "promotion_ready_students": sum(
                1
                for record in records
                if record.promotion_readiness
            ),

            "client_project_ready_students": sum(
                1
                for record in records
                if record.client_project_readiness
            ),

            "certificate_eligible_students": sum(
                1
                for record in records
                if record.certificate_eligibility
            ),

            "average_engineering_score": round(
                average_score,
                2
            ),

            "average_data_completeness": round(
                average_completeness,
                2
            ),

            "highest_engineering_score": round(
                max(scores)
                if scores
                else 0.0,
                2
            ),

            "lowest_engineering_score": round(
                min(scores)
                if scores
                else 0.0,
                2
            )
        }

    @staticmethod
    def _calculate_attendance_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.date >= period_start,
                Attendance.date <= period_end
            )
            .all()
        )

        if not attendance_records:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "records": 0,
                    "present": 0,
                    "late": 0,
                    "absent": 0
                }
            }

        present = 0
        late = 0
        absent = 0
        earned_points = 0.0

        for record in attendance_records:
            record_status = str(
                record.status
            ).lower()

            if record_status == "present":
                present += 1
                earned_points += 1.0

            elif record_status == "late":
                late += 1
                earned_points += 0.75

            else:
                absent += 1

        score = (
            earned_points
            / len(attendance_records)
            * 100
        )

        return {
            "score": round(score, 2),
            "has_data": True,
            "details": {
                "records": len(
                    attendance_records
                ),
                "present": present,
                "late": late,
                "absent": absent
            }
        }

    @staticmethod
    def _calculate_github_score(
        db: Session,
        student_id: int,
        period_end: date
    ) -> dict[str, Any]:
        period_end_datetime = datetime.combine(
            period_end,
            time.max
        ).replace(
            tzinfo=timezone.utc
        )

        report = (
            db.query(GitHubReport)
            .filter(
                GitHubReport.student_id == student_id,
                GitHubReport.generated_at
                <= period_end_datetime
            )
            .order_by(
                GitHubReport.generated_at.desc(),
                GitHubReport.id.desc()
            )
            .first()
        )

        if not report:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "report_id": None
                }
            }

        return {
            "score": round(
                float(
                    report.final_github_score
                    or 0
                ),
                2
            ),
            "has_data": True,
            "details": {
                "report_id": report.id,
                "profile_score": (
                    report.profile_score
                ),
                "activity_score": (
                    report.activity_score
                ),
                "code_quality_score": (
                    report.ai_code_quality_score
                ),
                "repositories_analyzed": (
                    report.repositories_analyzed
                )
            }
        }

    @staticmethod
    def _calculate_daily_activity_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id
                == student_id,
                DailyActivity.activity_date
                >= period_start,
                DailyActivity.activity_date
                <= period_end
            )
            .all()
        )

        if not activities:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "activity_days": 0,
                    "verified_records": 0
                }
            }

        total_period_days = max(
            1,
            (
                period_end - period_start
            ).days + 1
        )

        activity_days = len({
            activity.activity_date
            for activity in activities
        })

        consistency_score = min(
            100.0,
            activity_days
            / total_period_days
            * 100
        )

        verified_records = sum(
            1
            for activity in activities
            if activity.verification_status
            == "Verified"
        )

        verification_score = (
            verified_records
            / len(activities)
            * 100
        )

        completed_records = sum(
            1
            for activity in activities
            if activity.task_status
            == "Completed"
        )

        completion_score = (
            completed_records
            / len(activities)
            * 100
        )

        final_score = (
            consistency_score * 0.50
            + verification_score * 0.30
            + completion_score * 0.20
        )

        return {
            "score": round(final_score, 2),
            "has_data": True,
            "details": {
                "total_records": len(activities),
                "activity_days": activity_days,
                "verified_records": verified_records,
                "completed_records": completed_records,
                "consistency_score": round(
                    consistency_score,
                    2
                )
            }
        }

    @staticmethod
    def _calculate_task_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        tasks = (
            db.query(Task)
            .filter(
                Task.student_id == student_id,
                Task.start_date >= period_start,
                Task.start_date <= period_end
            )
            .all()
        )

        if not tasks:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "total_tasks": 0,
                    "approved_tasks": 0
                }
            }

        approved_tasks = [
            task
            for task in tasks
            if task.status == "Approved"
        ]

        submitted_or_completed = [
            task
            for task in tasks
            if task.status in {
                "Submitted",
                "Approved"
            }
        ]

        completion_rate = (
            len(submitted_or_completed)
            / len(tasks)
            * 100
        )

        task_scores = [
            float(task.completion_score)
            for task in approved_tasks
            if task.completion_score is not None
        ]

        average_review_score = (
            sum(task_scores)
            / len(task_scores)
            if task_scores
            else 0.0
        )

        average_progress = (
            sum(
                float(
                    task.progress_percentage
                    or 0
                )
                for task in tasks
            )
            / len(tasks)
        )

        final_score = (
            completion_rate * 0.40
            + average_review_score * 0.40
            + average_progress * 0.20
        )

        return {
            "score": round(final_score, 2),
            "has_data": True,
            "details": {
                "total_tasks": len(tasks),
                "approved_tasks": len(
                    approved_tasks
                ),
                "completion_rate": round(
                    completion_rate,
                    2
                ),
                "average_review_score": round(
                    average_review_score,
                    2
                ),
                "average_progress": round(
                    average_progress,
                    2
                )
            }
        }

    @staticmethod
    def _calculate_case_study_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.student_id
                == student_id,
                CaseStudy.start_date
                >= period_start,
                CaseStudy.start_date
                <= period_end
            )
            .all()
        )

        if not case_studies:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "total_case_studies": 0,
                    "evaluated_case_studies": 0
                }
            }

        evaluated = [
            case_study
            for case_study in case_studies
            if case_study.final_score is not None
        ]

        approved = [
            case_study
            for case_study in case_studies
            if case_study.status == "Approved"
        ]

        average_score = (
            sum(
                float(
                    case_study.final_score
                )
                for case_study in evaluated
            )
            / len(evaluated)
            if evaluated
            else 0.0
        )

        approval_rate = (
            len(approved)
            / len(case_studies)
            * 100
        )

        average_revisions = (
            sum(
                case_study.revision_count
                for case_study in case_studies
            )
            / len(case_studies)
        )

        revision_efficiency = max(
            0.0,
            100.0
            - average_revisions * 20
        )

        final_score = (
            average_score * 0.60
            + approval_rate * 0.25
            + revision_efficiency * 0.15
        )

        return {
            "score": round(final_score, 2),
            "has_data": True,
            "details": {
                "total_case_studies": len(
                    case_studies
                ),
                "evaluated_case_studies": len(
                    evaluated
                ),
                "approved_case_studies": len(
                    approved
                ),
                "average_score": round(
                    average_score,
                    2
                ),
                "approval_rate": round(
                    approval_rate,
                    2
                ),
                "average_revisions": round(
                    average_revisions,
                    2
                )
            }
        }

    @staticmethod
    def _calculate_feedback_scores(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        feedback_records = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.student_id
                == student_id,
                MentorFeedback.review_date
                >= period_start,
                MentorFeedback.review_date
                <= period_end
            )
            .all()
        )

        if not feedback_records:
            return {
                "mentor_feedback_score": 0.0,
                "communication_score": 0.0,
                "has_data": False,
                "details": {
                    "feedback_records": 0
                }
            }

        mentor_feedback_score = (
            sum(
                float(
                    feedback.overall_feedback_score
                )
                for feedback in feedback_records
            )
            / len(feedback_records)
        )

        communication_score = (
            sum(
                float(
                    feedback.communication_score
                )
                for feedback in feedback_records
            )
            / len(feedback_records)
        )

        leadership_score = (
            sum(
                float(
                    feedback.leadership_score
                )
                for feedback in feedback_records
            )
            / len(feedback_records)
        )

        return {
            "mentor_feedback_score": round(
                mentor_feedback_score,
                2
            ),
            "communication_score": round(
                communication_score,
                2
            ),
            "has_data": True,
            "details": {
                "feedback_records": len(
                    feedback_records
                ),
                "average_leadership_score": round(
                    leadership_score,
                    2
                )
            }
        }

    @staticmethod
    def _calculate_deadline_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        tasks = (
            db.query(Task)
            .filter(
                Task.student_id == student_id,
                Task.start_date >= period_start,
                Task.start_date <= period_end,
                Task.deadline_status.in_([
                    "On Time",
                    "Late",
                    "Overdue"
                ])
            )
            .all()
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.student_id
                == student_id,
                CaseStudy.start_date >= period_start,
                CaseStudy.start_date <= period_end,
                CaseStudy.deadline_status.in_([
                    "On Time",
                    "Late",
                    "Overdue"
                ])
            )
            .all()
        )

        records = [
            *tasks,
            *case_studies
        ]

        if not records:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "deadline_records": 0,
                    "on_time": 0,
                    "late": 0,
                    "overdue": 0
                }
            }

        on_time = sum(
            1
            for record in records
            if record.deadline_status == "On Time"
        )

        late = sum(
            1
            for record in records
            if record.deadline_status == "Late"
        )

        overdue = sum(
            1
            for record in records
            if record.deadline_status == "Overdue"
        )

        earned_points = (
            on_time * 1.0
            + late * 0.50
        )

        score = (
            earned_points
            / len(records)
            * 100
        )

        return {
            "score": round(score, 2),
            "has_data": True,
            "details": {
                "deadline_records": len(records),
                "on_time": on_time,
                "late": late,
                "overdue": overdue
            }
        }

    @staticmethod
    def _calculate_learning_score(
        db: Session,
        student_id: int,
        period_end: date
    ) -> dict[str, Any]:
        record = (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id
                == student_id,
                LearningSpeedRecord.period_end
                <= period_end
            )
            .order_by(
                LearningSpeedRecord.period_end.desc(),
                LearningSpeedRecord.id.desc()
            )
            .first()
        )

        if not record:
            return {
                "score": 0.0,
                "has_data": False,
                "details": {
                    "record_id": None
                }
            }

        return {
            "score": round(
                float(
                    record.learning_speed_score
                    or 0
                ),
                2
            ),
            "has_data": True,
            "details": {
                "record_id": record.id,
                "learning_level": (
                    record.learning_level
                ),
                "growth_percentage": (
                    record.growth_percentage
                ),
                "tasks_completed": (
                    record.tasks_completed
                ),
                "case_studies_completed": (
                    record.case_studies_completed
                )
            }
        }

    @staticmethod
    def _calculate_credit_score(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        start_datetime = datetime.combine(
            period_start,
            time.min
        ).replace(
            tzinfo=timezone.utc
        )

        end_datetime = datetime.combine(
            period_end,
            time.max
        ).replace(
            tzinfo=timezone.utc
        )

        credits = (
            db.query(EngineeringCredit)
            .filter(
                EngineeringCredit.student_id
                == student_id,
                EngineeringCredit.awarded_at
                >= start_datetime,
                EngineeringCredit.awarded_at
                <= end_datetime
            )
            .all()
        )

        if not credits:
            return {
                "score": 50.0,
                "has_data": False,
                "details": {
                    "transactions": 0,
                    "net_credits": 0
                }
            }

        positive_credits = sum(
            credit.credit_value
            for credit in credits
            if credit.credit_value > 0
        )

        penalty_credits = sum(
            credit.credit_value
            for credit in credits
            if credit.credit_value < 0
        )

        net_credits = (
            positive_credits
            + penalty_credits
        )

        score = 50 + (
            net_credits / 4
        )

        score = (
            EngineeringScoreService
            ._clamp_score(score)
        )

        return {
            "score": round(score, 2),
            "has_data": True,
            "details": {
                "transactions": len(credits),
                "positive_credits": positive_credits,
                "penalty_credits": penalty_credits,
                "net_credits": net_credits
            }
        }

    @staticmethod
    def _calculate_readiness(
        final_score: float,
        completeness: float,
        component_scores: dict[str, float],
        tasks: dict[str, Any],
        case_studies: dict[str, Any],
        feedback: dict[str, Any],
        deadline: dict[str, Any]
    ) -> dict[str, bool]:
        placement_readiness = (
            final_score >= 75
            and completeness >= 70
            and component_scores["github"] >= 65
            and component_scores["communication"] >= 65
            and component_scores[
                "deadline_compliance"
            ] >= 60
        )

        promotion_readiness = (
            final_score >= 80
            and completeness >= 70
            and component_scores["tasks"] >= 75
            and component_scores[
                "case_studies"
            ] >= 75
            and component_scores[
                "mentor_feedback"
            ] >= 75
        )

        client_project_readiness = (
            final_score >= 78
            and completeness >= 75
            and component_scores["github"] >= 70
            and component_scores["tasks"] >= 75
            and component_scores[
                "case_studies"
            ] >= 75
            and component_scores[
                "communication"
            ] >= 70
            and component_scores[
                "deadline_compliance"
            ] >= 70
        )

        certificate_eligibility = (
            final_score >= 60
            and completeness >= 60
            and component_scores["attendance"] >= 60
            and component_scores[
                "deadline_compliance"
            ] >= 50
        )

        return {
            "placement_readiness": (
                placement_readiness
            ),
            "promotion_readiness": (
                promotion_readiness
            ),
            "client_project_readiness": (
                client_project_readiness
            ),
            "certificate_eligibility": (
                certificate_eligibility
            )
        }

    @staticmethod
    def _get_strong_areas(
        scores: dict[str, float]
    ) -> list[str]:
        strong_areas = []

        for component_name, score in scores.items():
            if score >= 75:
                strong_areas.append(
                    EngineeringScoreService
                    .COMPONENT_LABELS[
                        component_name
                    ]
                )

        return strong_areas

    @staticmethod
    def _get_weak_areas(
        scores: dict[str, float]
    ) -> list[str]:
        weak_areas = []

        for component_name, score in scores.items():
            if score < 60:
                weak_areas.append(
                    EngineeringScoreService
                    .COMPONENT_LABELS[
                        component_name
                    ]
                )

        return weak_areas

    @staticmethod
    def _generate_recommendations(
        final_score: float,
        completeness: float,
        component_scores: dict[str, float],
        readiness: dict[str, bool]
    ) -> list[str]:
        recommendations = []

        if completeness < 60:
            recommendations.append(
                "Collect more performance data before making a final engineering decision."
            )

        if component_scores["attendance"] < 60:
            recommendations.append(
                "Improve attendance consistency."
            )

        if component_scores["github"] < 60:
            recommendations.append(
                "Increase GitHub contributions and improve repository quality."
            )

        if component_scores["daily_activity"] < 60:
            recommendations.append(
                "Submit consistent and verified daily activity updates."
            )

        if component_scores["tasks"] < 60:
            recommendations.append(
                "Assign additional guided tasks and review task-completion quality."
            )

        if component_scores["case_studies"] < 60:
            recommendations.append(
                "Assign an easier case study with additional mentor guidance."
            )

        elif (
            component_scores["case_studies"] >= 80
            and final_score >= 75
        ):
            recommendations.append(
                "Assign an advanced case study."
            )

        if component_scores["communication"] < 60:
            recommendations.append(
                "Schedule a mentor meeting to improve communication and collaboration."
            )

        if component_scores[
            "deadline_compliance"
        ] < 60:
            recommendations.append(
                "Create a deadline-improvement plan and monitor overdue work."
            )

        if component_scores[
            "learning_speed"
        ] < 60:
            recommendations.append(
                "Provide additional mentoring and a structured learning plan."
            )

        if readiness["client_project_readiness"]:
            recommendations.append(
                "Consider assigning the intern to a supervised client project."
            )

        if readiness["placement_readiness"]:
            recommendations.append(
                "Recommend the intern for interview or job-placement review."
            )

        if readiness["promotion_readiness"]:
            recommendations.append(
                "Consider the intern for promotion or advanced responsibilities."
            )

        if (
            not recommendations
            and final_score >= 60
        ):
            recommendations.append(
                "Continue the current learning plan and monitor monthly growth."
            )

        return recommendations

    @staticmethod
    def _get_performance_level(
        score: float
    ) -> str:
        if score >= 85:
            return "Excellent"

        if score >= 70:
            return "Good"

        if score >= 55:
            return "Average"

        return "Weak"

    @staticmethod
    def _clamp_score(
        score: float
    ) -> float:
        return round(
            max(
                0.0,
                min(
                    float(score),
                    100.0
                )
            ),
            2
        )