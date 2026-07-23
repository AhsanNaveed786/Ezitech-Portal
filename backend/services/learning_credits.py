from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    CaseStudy,
    DailyActivity,
    EngineeringCredit,
    LearningSpeedRecord,
    Mentor,
    Student,
    Task
)
from backend.schemas import (
    EngineeringCreditCreate,
    LearningSpeedGenerateRequest
)


class LearningCreditService:

    @staticmethod
    def generate_learning_speed(
        db: Session,
        mentor: Mentor,
        request_data: LearningSpeedGenerateRequest
    ) -> LearningSpeedRecord:
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

        if student.mentor_id != mentor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only generate learning-speed "
                    "analysis for your assigned students."
                )
            )

        existing_record = (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id
                == student.id,
                LearningSpeedRecord.period_start
                == request_data.period_start,
                LearningSpeedRecord.period_end
                == request_data.period_end
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Learning-speed analysis already "
                    "exists for this period."
                )
            )

        task_metrics = (
            LearningCreditService
            ._calculate_task_metrics(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        case_study_metrics = (
            LearningCreditService
            ._calculate_case_study_metrics(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        activity_metrics = (
            LearningCreditService
            ._calculate_activity_metrics(
                db=db,
                student_id=student.id,
                period_start=request_data.period_start,
                period_end=request_data.period_end
            )
        )

        completed_records = (
            task_metrics["tasks_completed"]
            + case_study_metrics[
                "case_studies_completed"
            ]
        )

        if completed_records == 0:
            learning_speed_score = 0.0
            learning_level = "Insufficient Data"

        else:
            learning_speed_score = round(
                task_metrics["task_speed_score"]
                * 0.30
                + case_study_metrics[
                    "case_study_growth_score"
                ]
                * 0.25
                + case_study_metrics[
                    "revision_efficiency_score"
                ]
                * 0.15
                + activity_metrics[
                    "activity_consistency_score"
                ]
                * 0.15
                + task_metrics[
                    "deadline_learning_score"
                ]
                * 0.15,
                2
            )

            learning_level = (
                LearningCreditService
                ._get_learning_level(
                    learning_speed_score
                )
            )

        previous_record = (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id
                == student.id,
                LearningSpeedRecord.period_end
                < request_data.period_start
            )
            .order_by(
                LearningSpeedRecord.period_end.desc(),
                LearningSpeedRecord.id.desc()
            )
            .first()
        )

        previous_score = (
            float(
                previous_record.learning_speed_score
            )
            if previous_record
            else None
        )

        growth_percentage = (
            LearningCreditService
            ._calculate_growth_percentage(
                current_score=learning_speed_score,
                previous_score=previous_score
            )
        )

        analysis_notes = (
            LearningCreditService
            ._generate_analysis_notes(
                learning_speed_score=(
                    learning_speed_score
                ),
                growth_percentage=growth_percentage,
                task_speed_score=(
                    task_metrics[
                        "task_speed_score"
                    ]
                ),
                revision_efficiency_score=(
                    case_study_metrics[
                        "revision_efficiency_score"
                    ]
                ),
                activity_consistency_score=(
                    activity_metrics[
                        "activity_consistency_score"
                    ]
                ),
                completed_records=completed_records
            )
        )

        record = LearningSpeedRecord(
            student_id=student.id,
            period_start=request_data.period_start,
            period_end=request_data.period_end,

            tasks_completed=(
                task_metrics["tasks_completed"]
            ),

            case_studies_completed=(
                case_study_metrics[
                    "case_studies_completed"
                ]
            ),

            activity_days=(
                activity_metrics["activity_days"]
            ),

            average_task_completion_days=(
                task_metrics[
                    "average_task_completion_days"
                ]
            ),

            average_case_study_score=(
                case_study_metrics[
                    "average_case_study_score"
                ]
            ),

            average_revision_count=(
                case_study_metrics[
                    "average_revision_count"
                ]
            ),

            task_speed_score=(
                task_metrics["task_speed_score"]
            ),

            case_study_growth_score=(
                case_study_metrics[
                    "case_study_growth_score"
                ]
            ),

            revision_efficiency_score=(
                case_study_metrics[
                    "revision_efficiency_score"
                ]
            ),

            activity_consistency_score=(
                activity_metrics[
                    "activity_consistency_score"
                ]
            ),

            deadline_learning_score=(
                task_metrics[
                    "deadline_learning_score"
                ]
            ),

            learning_speed_score=(
                learning_speed_score
            ),

            previous_period_score=previous_score,
            growth_percentage=growth_percentage,
            learning_level=learning_level,
            analysis_notes=analysis_notes
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
                    "Learning-speed analysis already "
                    "exists for this period."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return record

    @staticmethod
    def award_engineering_credit(
        db: Session,
        mentor: Mentor,
        credit_data: EngineeringCreditCreate
    ) -> EngineeringCredit:
        student = (
            db.query(Student)
            .filter(
                Student.id == credit_data.student_id
            )
            .first()
        )

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student was not found."
            )

        if student.mentor_id != mentor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only award engineering "
                    "credits to your assigned students."
                )
            )

        credit = EngineeringCredit(
            student_id=student.id,
            awarded_by_mentor_id=mentor.id,
            category=credit_data.category,
            credit_value=credit_data.credit_value,
            reason=credit_data.reason,
            source_type=credit_data.source_type,
            source_id=credit_data.source_id
        )

        try:
            db.add(credit)
            db.commit()
            db.refresh(credit)

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Engineering credits have already "
                    "been awarded for this source."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return credit

    @staticmethod
    def get_student_learning_records(
        db: Session,
        student_id: int,
        limit: int = 50
    ) -> list[LearningSpeedRecord]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(LearningSpeedRecord)
            .filter(
                LearningSpeedRecord.student_id
                == student_id
            )
            .order_by(
                LearningSpeedRecord.period_end.desc(),
                LearningSpeedRecord.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_student_credits(
        db: Session,
        student_id: int,
        limit: int = 100
    ) -> list[EngineeringCredit]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        return (
            db.query(EngineeringCredit)
            .filter(
                EngineeringCredit.student_id
                == student_id
            )
            .order_by(
                EngineeringCredit.awarded_at.desc(),
                EngineeringCredit.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_credit_totals(
        db: Session,
        student_id: int
    ) -> dict[str, int]:
        credits = (
            db.query(EngineeringCredit)
            .filter(
                EngineeringCredit.student_id
                == student_id
            )
            .all()
        )

        positive_credits = sum(
            credit.credit_value
            for credit in credits
            if credit.credit_value > 0
        )

        negative_credits = sum(
            credit.credit_value
            for credit in credits
            if credit.credit_value < 0
        )

        return {
            "total_credits": (
                positive_credits
                + negative_credits
            ),
            "positive_credits": positive_credits,
            "negative_credits": negative_credits,
            "total_records": len(credits)
        }

    @staticmethod
    def get_learning_speed_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        latest_subquery = (
            db.query(
                LearningSpeedRecord.student_id.label(
                    "student_id"
                ),
                func.max(
                    LearningSpeedRecord.id
                ).label(
                    "latest_record_id"
                )
            )
            .group_by(
                LearningSpeedRecord.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                LearningSpeedRecord,
                Student
            )
            .join(
                latest_subquery,
                LearningSpeedRecord.id
                == latest_subquery.c.latest_record_id
            )
            .join(
                Student,
                Student.id
                == LearningSpeedRecord.student_id
            )
            .order_by(
                desc(
                    LearningSpeedRecord
                    .learning_speed_score
                ),
                desc(
                    LearningSpeedRecord
                    .growth_percentage
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
                "learning_speed_score": (
                    record.learning_speed_score
                ),
                "previous_period_score": (
                    record.previous_period_score
                ),
                "growth_percentage": (
                    record.growth_percentage
                ),
                "learning_level": (
                    record.learning_level
                ),
                "tasks_completed": (
                    record.tasks_completed
                ),
                "case_studies_completed": (
                    record.case_studies_completed
                ),
                "activity_days": (
                    record.activity_days
                ),
                "period_start": (
                    record.period_start
                ),
                "period_end": record.period_end
            })

        return rankings

    @staticmethod
    def get_credit_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        rows = (
            db.query(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                func.coalesce(
                    func.sum(
                        EngineeringCredit.credit_value
                    ),
                    0
                ).label("total_credits"),
                func.coalesce(
                    func.sum(
                        func.greatest(
                            EngineeringCredit.credit_value,
                            0
                        )
                    ),
                    0
                ).label("positive_credits"),
                func.coalesce(
                    func.sum(
                        func.least(
                            EngineeringCredit.credit_value,
                            0
                        )
                    ),
                    0
                ).label("penalty_credits"),
                func.count(
                    EngineeringCredit.id
                ).label("credit_records")
            )
            .outerjoin(
                EngineeringCredit,
                EngineeringCredit.student_id
                == Student.id
            )
            .group_by(
                Student.id,
                Student.name
            )
            .order_by(
                desc("total_credits")
            )
            .limit(safe_limit)
            .all()
        )

        return [
            {
                "rank": rank,
                "student_id": row.student_id,
                "student_name": row.student_name,
                "total_credits": int(
                    row.total_credits or 0
                ),
                "positive_credits": int(
                    row.positive_credits or 0
                ),
                "penalty_credits": int(
                    row.penalty_credits or 0
                ),
                "credit_records": int(
                    row.credit_records or 0
                )
            }
            for rank, row in enumerate(
                rows,
                start=1
            )
        ]

    @staticmethod
    def get_summary(
        db: Session
    ) -> dict[str, Any]:
        latest_subquery = (
            db.query(
                LearningSpeedRecord.student_id.label(
                    "student_id"
                ),
                func.max(
                    LearningSpeedRecord.id
                ).label(
                    "latest_record_id"
                )
            )
            .group_by(
                LearningSpeedRecord.student_id
            )
            .subquery()
        )

        learning_records = (
            db.query(LearningSpeedRecord)
            .join(
                latest_subquery,
                LearningSpeedRecord.id
                == latest_subquery.c.latest_record_id
            )
            .all()
        )

        credits = (
            db.query(EngineeringCredit)
            .all()
        )

        def count_level(
            level: str
        ) -> int:
            return sum(
                1
                for record in learning_records
                if record.learning_level == level
            )

        average_learning_score = (
            sum(
                float(
                    record.learning_speed_score
                )
                for record in learning_records
            )
            / len(learning_records)
            if learning_records
            else 0.0
        )

        average_growth = (
            sum(
                float(
                    record.growth_percentage
                )
                for record in learning_records
            )
            / len(learning_records)
            if learning_records
            else 0.0
        )

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

        return {
            "total_learning_records": len(
                learning_records
            ),
            "fast_learners": count_level(
                "Fast Learner"
            ),
            "steady_learners": count_level(
                "Steady Learner"
            ),
            "learners_needing_improvement": (
                count_level(
                    "Needs Improvement"
                )
            ),
            "insufficient_data_students": (
                count_level(
                    "Insufficient Data"
                )
            ),
            "average_learning_speed_score": round(
                average_learning_score,
                2
            ),
            "average_growth_percentage": round(
                average_growth,
                2
            ),
            "total_credit_transactions": len(
                credits
            ),
            "total_positive_credits": (
                positive_credits
            ),
            "total_penalty_credits": (
                penalty_credits
            ),
            "net_engineering_credits": (
                positive_credits
                + penalty_credits
            )
        }

    @staticmethod
    def _calculate_task_metrics(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        tasks = (
            db.query(Task)
            .filter(
                Task.student_id == student_id,
                Task.status == "Approved",
                Task.completed_at.isnot(None),
                func.date(Task.completed_at)
                >= period_start,
                func.date(Task.completed_at)
                <= period_end
            )
            .all()
        )

        completion_days = []
        speed_scores = []

        for task in tasks:
            expected_days = max(
                1,
                (
                    task.due_date
                    - task.start_date
                ).days + 1
            )

            completion_date = (
                task.submitted_at.date()
                if task.submitted_at
                else task.completed_at.date()
            )

            actual_days = max(
                1,
                (
                    completion_date
                    - task.start_date
                ).days + 1
            )

            completion_days.append(
                actual_days
            )

            speed_score = min(
                100.0,
                expected_days
                / actual_days
                * 100
            )

            speed_scores.append(
                speed_score
            )

        average_completion_days = (
            sum(completion_days)
            / len(completion_days)
            if completion_days
            else 0.0
        )

        task_speed_score = (
            sum(speed_scores)
            / len(speed_scores)
            if speed_scores
            else 0.0
        )

        deadline_records = [
            task
            for task in tasks
            if task.deadline_status
            in {"On Time", "Late"}
        ]

        on_time_count = sum(
            1
            for task in deadline_records
            if task.deadline_status == "On Time"
        )

        deadline_score = (
            on_time_count
            / len(deadline_records)
            * 100
            if deadline_records
            else 0.0
        )

        return {
            "tasks_completed": len(tasks),
            "average_task_completion_days": round(
                average_completion_days,
                2
            ),
            "task_speed_score": round(
                task_speed_score,
                2
            ),
            "deadline_learning_score": round(
                deadline_score,
                2
            )
        }

    @staticmethod
    def _calculate_case_study_metrics(
        db: Session,
        student_id: int,
        period_start: date,
        period_end: date
    ) -> dict[str, Any]:
        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.student_id == student_id,
                CaseStudy.status.in_([
                    "Approved",
                    "Failed"
                ]),
                CaseStudy.evaluated_at.isnot(None),
                func.date(CaseStudy.evaluated_at)
                >= period_start,
                func.date(CaseStudy.evaluated_at)
                <= period_end
            )
            .all()
        )

        scores = [
            float(case_study.final_score or 0)
            for case_study in case_studies
        ]

        revisions = [
            case_study.revision_count
            for case_study in case_studies
        ]

        average_score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        average_revisions = (
            sum(revisions) / len(revisions)
            if revisions
            else 0.0
        )

        revision_efficiency = max(
            0.0,
            100.0
            - average_revisions * 25
        )

        return {
            "case_studies_completed": len(
                case_studies
            ),
            "average_case_study_score": round(
                average_score,
                2
            ),
            "average_revision_count": round(
                average_revisions,
                2
            ),
            "case_study_growth_score": round(
                average_score,
                2
            ),
            "revision_efficiency_score": round(
                revision_efficiency,
                2
            )
        }

    @staticmethod
    def _calculate_activity_metrics(
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

        total_period_days = max(
            1,
            (
                period_end
                - period_start
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

        return {
            "activity_days": activity_days,
            "activity_consistency_score": round(
                consistency_score,
                2
            )
        }

    @staticmethod
    def _calculate_growth_percentage(
        current_score: float,
        previous_score: float | None
    ) -> float:
        if previous_score is None:
            return 0.0

        if previous_score == 0:
            return (
                100.0
                if current_score > 0
                else 0.0
            )

        return round(
            (
                current_score
                - previous_score
            )
            / previous_score
            * 100,
            2
        )

    @staticmethod
    def _get_learning_level(
        score: float
    ) -> str:
        if score >= 80:
            return "Fast Learner"

        if score >= 60:
            return "Steady Learner"

        return "Needs Improvement"

    @staticmethod
    def _generate_analysis_notes(
        learning_speed_score: float,
        growth_percentage: float,
        task_speed_score: float,
        revision_efficiency_score: float,
        activity_consistency_score: float,
        completed_records: int
    ) -> str:
        if completed_records == 0:
            return (
                "Insufficient completed tasks and case "
                "studies for learning-speed analysis."
            )

        notes = []

        if learning_speed_score >= 80:
            notes.append(
                "The student demonstrates fast learning."
            )

        elif learning_speed_score >= 60:
            notes.append(
                "The student demonstrates steady learning."
            )

        else:
            notes.append(
                "The student requires additional mentoring."
            )

        if growth_percentage > 10:
            notes.append(
                "Performance has improved significantly "
                "compared with the previous period."
            )

        elif growth_percentage < -10:
            notes.append(
                "Performance has declined compared with "
                "the previous period."
            )

        if task_speed_score < 60:
            notes.append(
                "Task completion speed needs improvement."
            )

        if revision_efficiency_score < 60:
            notes.append(
                "The student requires frequent revisions."
            )

        if activity_consistency_score < 50:
            notes.append(
                "Daily activity consistency is low."
            )

        return " ".join(notes)