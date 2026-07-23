from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models import (
    CaseStudy,
    Mentor,
    Student
)
from backend.schemas import (
    CaseStudyCreate,
    CaseStudyEvaluationRequest,
    CaseStudyProgressUpdate,
    CaseStudySubmissionRequest
)


class CaseStudyService:

    @staticmethod
    def assign_case_study(
        db: Session,
        mentor: Mentor,
        case_study_data: CaseStudyCreate
    ) -> CaseStudy:
        student = (
            db.query(Student)
            .filter(
                Student.id
                == case_study_data.student_id
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
                    "You can only assign case studies "
                    "to your assigned students."
                )
            )

        if case_study_data.due_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past."
            )

        case_study = CaseStudy(
            title=case_study_data.title,
            description=case_study_data.description,
            objectives=case_study_data.objectives,
            requirements=case_study_data.requirements,
            technology=case_study_data.technology.strip(),
            category=case_study_data.category.strip(),
            difficulty_level=(
                case_study_data.difficulty_level
            ),
            student_id=student.id,
            assigned_by_mentor_id=mentor.id,
            start_date=case_study_data.start_date,
            due_date=case_study_data.due_date,
            status="Assigned",
            progress_percentage=0.0,
            revision_count=0,
            deadline_status="Pending",
            days_late=0
        )

        try:
            db.add(case_study)
            db.commit()
            db.refresh(case_study)

        except Exception:
            db.rollback()
            raise

        return case_study

    @staticmethod
    def update_progress(
        db: Session,
        student: Student,
        case_study_id: int,
        progress_data: CaseStudyProgressUpdate
    ) -> CaseStudy:
        case_study = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.id == case_study_id,
                CaseStudy.student_id == student.id
            )
            .first()
        )

        if not case_study:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case study was not found."
            )

        if case_study.status in {
            "Submitted",
            "Resubmitted",
            "Approved",
            "Failed",
            "Cancelled"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Progress cannot be updated while "
                    f"case study status is {case_study.status}."
                )
            )

        case_study.progress_percentage = (
            progress_data.progress_percentage
        )

        case_study.student_blockers = (
            progress_data.student_blockers
        )

        case_study.learning_outcome = (
            progress_data.learning_outcome
        )

        if (
            case_study.started_at is None
            and progress_data.progress_percentage > 0
        ):
            case_study.started_at = datetime.now(
                timezone.utc
            )

        case_study.status = "In Progress"

        CaseStudyService._update_overdue_state(
            case_study
        )

        try:
            db.commit()
            db.refresh(case_study)

        except Exception:
            db.rollback()
            raise

        return case_study

    @staticmethod
    def submit_case_study(
        db: Session,
        student: Student,
        case_study_id: int,
        submission_data: CaseStudySubmissionRequest
    ) -> CaseStudy:
        case_study = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.id == case_study_id,
                CaseStudy.student_id == student.id
            )
            .first()
        )

        if not case_study:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case study was not found."
            )

        allowed_statuses = {
            "Assigned",
            "In Progress",
            "Revision Required",
            "Overdue"
        }

        if case_study.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This case study cannot be submitted "
                    f"while its status is {case_study.status}."
                )
            )

        submission_time = datetime.now(
            timezone.utc
        )

        was_revision = (
            case_study.status
            == "Revision Required"
        )

        case_study.github_repository_url = (
            submission_data.github_repository_url
        )

        case_study.live_demo_url = (
            submission_data.live_demo_url
        )

        case_study.documentation_url = (
            submission_data.documentation_url
        )

        case_study.submission_notes = (
            submission_data.submission_notes
        )

        if submission_data.learning_outcome:
            case_study.learning_outcome = (
                submission_data.learning_outcome
            )

        case_study.submitted_at = submission_time
        case_study.progress_percentage = 100.0

        if was_revision:
            case_study.status = "Resubmitted"

        else:
            case_study.status = "Submitted"

        CaseStudyService._set_deadline_result(
            case_study=case_study,
            submission_date=submission_time.date()
        )

        try:
            db.commit()
            db.refresh(case_study)

        except Exception:
            db.rollback()
            raise

        return case_study

    @staticmethod
    def evaluate_case_study(
        db: Session,
        mentor: Mentor,
        case_study_id: int,
        evaluation_data: CaseStudyEvaluationRequest
    ) -> CaseStudy:
        case_study = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.id == case_study_id,
                CaseStudy.assigned_by_mentor_id
                == mentor.id
            )
            .first()
        )

        if not case_study:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Case study was not found or is not "
                    "assigned by this mentor."
                )
            )

        if case_study.status not in {
            "Submitted",
            "Resubmitted"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only submitted or resubmitted "
                    "case studies can be evaluated."
                )
            )

        final_score = (
            evaluation_data.technical_score * 0.30
            + evaluation_data.code_quality_score * 0.25
            + evaluation_data.documentation_score * 0.15
            + evaluation_data.problem_solving_score * 0.20
            + evaluation_data.presentation_score * 0.10
        )

        final_score = round(
            final_score,
            2
        )

        case_study.technical_score = (
            evaluation_data.technical_score
        )

        case_study.code_quality_score = (
            evaluation_data.code_quality_score
        )

        case_study.documentation_score = (
            evaluation_data.documentation_score
        )

        case_study.problem_solving_score = (
            evaluation_data.problem_solving_score
        )

        case_study.presentation_score = (
            evaluation_data.presentation_score
        )

        case_study.final_score = final_score
        case_study.performance_level = (
            CaseStudyService
            ._get_performance_level(
                final_score
            )
        )

        case_study.mentor_feedback = (
            evaluation_data.mentor_feedback
        )

        case_study.strengths = (
            evaluation_data.strengths
        )

        case_study.weak_areas = (
            evaluation_data.weak_areas
        )

        case_study.evaluated_at = datetime.now(
            timezone.utc
        )

        if (
            evaluation_data.decision
            == "Revision Required"
        ):
            case_study.status = (
                "Revision Required"
            )

            case_study.revision_instructions = (
                evaluation_data
                .revision_instructions
            )

            case_study.revision_count += 1
            case_study.progress_percentage = 90.0
            case_study.completed_at = None

        elif (
            evaluation_data.decision
            == "Approved"
        ):
            case_study.status = "Approved"
            case_study.progress_percentage = 100.0
            case_study.completed_at = (
                case_study.evaluated_at
            )
            case_study.revision_instructions = None

        else:
            case_study.status = "Failed"
            case_study.completed_at = (
                case_study.evaluated_at
            )
            case_study.revision_instructions = (
                evaluation_data
                .revision_instructions
            )

        try:
            db.commit()
            db.refresh(case_study)

        except Exception:
            db.rollback()
            raise

        return case_study

    @staticmethod
    def get_case_study_by_id(
        db: Session,
        case_study_id: int
    ) -> CaseStudy | None:
        case_study = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.id == case_study_id
            )
            .first()
        )

        if case_study:
            CaseStudyService._sync_case_studies(
                db=db,
                case_studies=[case_study]
            )

        return case_study

    @staticmethod
    def get_student_case_studies(
        db: Session,
        student_id: int,
        limit: int = 50
    ) -> list[CaseStudy]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.student_id == student_id
            )
            .order_by(
                CaseStudy.due_date.asc(),
                CaseStudy.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

        CaseStudyService._sync_case_studies(
            db=db,
            case_studies=case_studies
        )

        return case_studies

    @staticmethod
    def get_mentor_case_studies(
        db: Session,
        mentor_id: int,
        limit: int = 100
    ) -> list[CaseStudy]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.assigned_by_mentor_id
                == mentor_id
            )
            .order_by(
                CaseStudy.due_date.asc(),
                CaseStudy.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

        CaseStudyService._sync_case_studies(
            db=db,
            case_studies=case_studies
        )

        return case_studies

    @staticmethod
    def get_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        rows = (
            db.query(
                CaseStudy,
                Student
            )
            .join(
                Student,
                Student.id
                == CaseStudy.student_id
            )
            .filter(
                CaseStudy.status == "Approved",
                CaseStudy.final_score.isnot(None)
            )
            .order_by(
                desc(CaseStudy.final_score),
                CaseStudy.revision_count.asc(),
                CaseStudy.days_late.asc()
            )
            .limit(safe_limit)
            .all()
        )

        rankings = []

        for rank, row in enumerate(
            rows,
            start=1
        ):
            case_study, student = row

            rankings.append({
                "rank": rank,
                "case_study_id": case_study.id,
                "student_id": student.id,
                "student_name": student.name,
                "title": case_study.title,
                "technology": case_study.technology,
                "difficulty_level": (
                    case_study.difficulty_level
                ),
                "final_score": (
                    case_study.final_score
                ),
                "performance_level": (
                    case_study.performance_level
                ),
                "deadline_status": (
                    case_study.deadline_status
                ),
                "revision_count": (
                    case_study.revision_count
                )
            })

        return rankings

    @staticmethod
    def get_summary(
        db: Session,
        period_days: int = 30
    ) -> dict[str, Any]:
        safe_period = max(
            1,
            min(period_days, 365)
        )

        start_date = (
            date.today()
            - timedelta(
                days=safe_period - 1
            )
        )

        case_studies = (
            db.query(CaseStudy)
            .filter(
                CaseStudy.start_date >= start_date
            )
            .all()
        )

        CaseStudyService._sync_case_studies(
            db=db,
            case_studies=case_studies
        )

        total = len(case_studies)

        def count_status(
            status_value: str
        ) -> int:
            return sum(
                1
                for case_study in case_studies
                if case_study.status
                == status_value
            )

        def count_difficulty(
            difficulty: str
        ) -> int:
            return sum(
                1
                for case_study in case_studies
                if case_study.difficulty_level
                == difficulty
            )

        approved = count_status(
            "Approved"
        )

        failed = count_status(
            "Failed"
        )

        on_time = sum(
            1
            for case_study in case_studies
            if case_study.deadline_status
            == "On Time"
        )

        late = sum(
            1
            for case_study in case_studies
            if case_study.deadline_status
            == "Late"
        )

        scored_case_studies = [
            float(case_study.final_score)
            for case_study in case_studies
            if case_study.final_score is not None
        ]

        average_score = (
            sum(scored_case_studies)
            / len(scored_case_studies)
            if scored_case_studies
            else 0.0
        )

        completed_total = approved + failed

        approval_rate = (
            approved / completed_total * 100
            if completed_total
            else 0.0
        )

        failure_rate = (
            failed / completed_total * 100
            if completed_total
            else 0.0
        )

        deadline_total = on_time + late

        deadline_compliance = (
            on_time / deadline_total * 100
            if deadline_total
            else 0.0
        )

        return {
            "period_days": safe_period,
            "total_case_studies": total,
            "assigned_case_studies": count_status(
                "Assigned"
            ),
            "in_progress_case_studies": count_status(
                "In Progress"
            ),
            "submitted_case_studies": (
                count_status("Submitted")
                + count_status("Resubmitted")
            ),
            "revision_required_case_studies": (
                count_status(
                    "Revision Required"
                )
            ),
            "approved_case_studies": approved,
            "failed_case_studies": failed,
            "overdue_case_studies": count_status(
                "Overdue"
            ),
            "easy_case_studies": count_difficulty(
                "Easy"
            ),
            "medium_case_studies": count_difficulty(
                "Medium"
            ),
            "advanced_case_studies": count_difficulty(
                "Advanced"
            ),
            "on_time_submissions": on_time,
            "late_submissions": late,
            "average_final_score": round(
                average_score,
                2
            ),
            "approval_rate": round(
                approval_rate,
                2
            ),
            "failure_rate": round(
                failure_rate,
                2
            ),
            "deadline_compliance_rate": round(
                deadline_compliance,
                2
            )
        }

    @staticmethod
    def get_case_study_recommendations(
        db: Session
    ) -> list[dict[str, Any]]:
        students = (
            db.query(Student)
            .all()
        )

        recommendations = []

        for student in students:
            completed = (
                db.query(CaseStudy)
                .filter(
                    CaseStudy.student_id
                    == student.id,
                    CaseStudy.status.in_([
                        "Approved",
                        "Failed"
                    ]),
                    CaseStudy.final_score.isnot(None)
                )
                .all()
            )

            if not completed:
                recommendations.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "completed_case_studies": 0,
                    "average_score": 0.0,
                    "average_revision_count": 0.0,
                    "current_recommended_level": "Easy",
                    "recommendation": (
                        "Assign Easier Case Study"
                    ),
                    "reason": (
                        "The student has no completed "
                        "case-study evaluation history."
                    )
                })

                continue

            average_score = sum(
                float(
                    case_study.final_score
                    or 0
                )
                for case_study in completed
            ) / len(completed)

            average_revisions = sum(
                case_study.revision_count
                for case_study in completed
            ) / len(completed)

            on_time_count = sum(
                1
                for case_study in completed
                if case_study.deadline_status
                == "On Time"
            )

            deadline_rate = (
                on_time_count
                / len(completed)
                * 100
            )

            if (
                average_score >= 85
                and average_revisions <= 1
                and deadline_rate >= 80
            ):
                recommended_level = "Advanced"
                recommendation = (
                    "Assign Advanced Case Study"
                )
                reason = (
                    "High average score, low revision "
                    "count and strong deadline compliance."
                )

            elif (
                average_score >= 65
                and average_revisions <= 2
            ):
                recommended_level = "Medium"
                recommendation = (
                    "Continue Medium Case Studies"
                )
                reason = (
                    "The student shows acceptable "
                    "performance but still requires "
                    "further growth before advanced work."
                )

            else:
                recommended_level = "Easy"
                recommendation = (
                    "Assign Easier Case Study"
                )
                reason = (
                    "Low score or high revision count "
                    "indicates that additional practice "
                    "and mentoring are required."
                )

            recommendations.append({
                "student_id": student.id,
                "student_name": student.name,
                "completed_case_studies": len(
                    completed
                ),
                "average_score": round(
                    average_score,
                    2
                ),
                "average_revision_count": round(
                    average_revisions,
                    2
                ),
                "current_recommended_level": (
                    recommended_level
                ),
                "recommendation": recommendation,
                "reason": reason
            })

        recommendations.sort(
            key=lambda item: (
                item["average_score"],
                -item["average_revision_count"]
            ),
            reverse=True
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

        if score >= 50:
            return "Average"

        return "Weak"

    @staticmethod
    def _set_deadline_result(
        case_study: CaseStudy,
        submission_date: date
    ) -> None:
        if submission_date <= case_study.due_date:
            case_study.deadline_status = (
                "On Time"
            )
            case_study.days_late = 0

        else:
            case_study.deadline_status = "Late"
            case_study.days_late = (
                submission_date
                - case_study.due_date
            ).days

    @staticmethod
    def _update_overdue_state(
        case_study: CaseStudy
    ) -> None:
        if (
            case_study.due_date < date.today()
            and case_study.status not in {
                "Submitted",
                "Resubmitted",
                "Approved",
                "Failed",
                "Cancelled"
            }
        ):
            case_study.status = "Overdue"
            case_study.deadline_status = (
                "Overdue"
            )
            case_study.days_late = (
                date.today()
                - case_study.due_date
            ).days

    @staticmethod
    def _sync_case_studies(
        db: Session,
        case_studies: list[CaseStudy]
    ) -> None:
        changed = False

        for case_study in case_studies:
            old_status = case_study.status
            old_deadline_status = (
                case_study.deadline_status
            )
            old_days_late = (
                case_study.days_late
            )

            CaseStudyService._update_overdue_state(
                case_study
            )

            if (
                old_status != case_study.status
                or old_deadline_status
                != case_study.deadline_status
                or old_days_late
                != case_study.days_late
            ):
                changed = True

        if changed:
            try:
                db.commit()

                for case_study in case_studies:
                    db.refresh(case_study)

            except Exception:
                db.rollback()
                raise