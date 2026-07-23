from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    Mentor,
    MentorFeedback,
    Student
)
from backend.schemas import (
    MentorFeedbackCreate,
    MentorFeedbackUpdate
)


class MentorFeedbackService:

    SCORE_FIELDS = (
        "technical_skill_score",
        "problem_solving_score",
        "consistency_score",
        "learning_attitude_score",
        "leadership_score",
        "communication_clarity_score",
        "responsiveness_score",
        "professionalism_score",
        "collaboration_score",
        "meeting_participation_score"
    )

    @staticmethod
    def create_feedback(
        db: Session,
        mentor: Mentor,
        feedback_data: MentorFeedbackCreate
    ) -> MentorFeedback:
        student = (
            db.query(Student)
            .filter(
                Student.id == feedback_data.student_id
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
                    "You can only submit feedback for "
                    "your assigned students."
                )
            )

        if feedback_data.review_date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Feedback review date cannot be "
                    "in the future."
                )
            )

        existing_feedback = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.student_id
                == student.id,
                MentorFeedback.mentor_id
                == mentor.id,
                MentorFeedback.review_date
                == feedback_data.review_date
            )
            .first()
        )

        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Feedback already exists for this "
                    "student on this review date."
                )
            )

        calculated = (
            MentorFeedbackService
            .calculate_scores(
                feedback_data.model_dump()
            )
        )

        feedback = MentorFeedback(
            student_id=student.id,
            mentor_id=mentor.id,
            review_date=feedback_data.review_date,
            review_period=feedback_data.review_period,

            technical_skill_score=(
                feedback_data.technical_skill_score
            ),

            problem_solving_score=(
                feedback_data.problem_solving_score
            ),

            consistency_score=(
                feedback_data.consistency_score
            ),

            learning_attitude_score=(
                feedback_data.learning_attitude_score
            ),

            leadership_score=(
                feedback_data.leadership_score
            ),

            communication_clarity_score=(
                feedback_data
                .communication_clarity_score
            ),

            responsiveness_score=(
                feedback_data.responsiveness_score
            ),

            professionalism_score=(
                feedback_data.professionalism_score
            ),

            collaboration_score=(
                feedback_data.collaboration_score
            ),

            meeting_participation_score=(
                feedback_data
                .meeting_participation_score
            ),

            communication_score=(
                calculated["communication_score"]
            ),

            overall_feedback_score=(
                calculated["overall_feedback_score"]
            ),

            performance_level=(
                calculated["performance_level"]
            ),

            communication_level=(
                calculated["communication_level"]
            ),

            leadership_potential=(
                calculated["leadership_potential"]
            ),

            requires_mentor_meeting=(
                calculated[
                    "requires_mentor_meeting"
                ]
            ),

            strengths=feedback_data.strengths,
            weak_areas=feedback_data.weak_areas,

            improvement_plan=(
                feedback_data.improvement_plan
            ),

            general_feedback=(
                feedback_data.general_feedback
            )
        )

        try:
            db.add(feedback)
            db.commit()
            db.refresh(feedback)

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Feedback already exists for this "
                    "student and review date."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return feedback

    @staticmethod
    def update_feedback(
        db: Session,
        mentor: Mentor,
        feedback_id: int,
        feedback_data: MentorFeedbackUpdate
    ) -> MentorFeedback:
        feedback = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.id == feedback_id,
                MentorFeedback.mentor_id
                == mentor.id
            )
            .first()
        )

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Feedback was not found or does not "
                    "belong to this mentor."
                )
            )

        update_values = feedback_data.model_dump(
            exclude_unset=True
        )

        for field_name, value in update_values.items():
            setattr(
                feedback,
                field_name,
                value
            )

        score_values = {
            field_name: getattr(
                feedback,
                field_name
            )
            for field_name
            in MentorFeedbackService.SCORE_FIELDS
        }

        calculated = (
            MentorFeedbackService
            .calculate_scores(
                score_values
            )
        )

        feedback.communication_score = (
            calculated["communication_score"]
        )

        feedback.overall_feedback_score = (
            calculated["overall_feedback_score"]
        )

        feedback.performance_level = (
            calculated["performance_level"]
        )

        feedback.communication_level = (
            calculated["communication_level"]
        )

        feedback.leadership_potential = (
            calculated["leadership_potential"]
        )

        feedback.requires_mentor_meeting = (
            calculated[
                "requires_mentor_meeting"
            ]
        )

        try:
            db.commit()
            db.refresh(feedback)

        except Exception:
            db.rollback()
            raise

        return feedback

    @staticmethod
    def get_feedback_by_id(
        db: Session,
        feedback_id: int
    ) -> MentorFeedback | None:
        return (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.id == feedback_id
            )
            .first()
        )

    @staticmethod
    def get_student_feedback(
        db: Session,
        student_id: int,
        limit: int = 50
    ) -> list[MentorFeedback]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.student_id
                == student_id
            )
            .order_by(
                MentorFeedback.review_date.desc(),
                MentorFeedback.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_mentor_feedback_records(
        db: Session,
        mentor_id: int,
        limit: int = 100
    ) -> list[MentorFeedback]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        return (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.mentor_id
                == mentor_id
            )
            .order_by(
                MentorFeedback.review_date.desc(),
                MentorFeedback.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_latest_feedback_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        latest_feedback_subquery = (
            db.query(
                MentorFeedback.student_id.label(
                    "student_id"
                ),
                func.max(
                    MentorFeedback.id
                ).label(
                    "latest_feedback_id"
                )
            )
            .group_by(
                MentorFeedback.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                MentorFeedback,
                Student
            )
            .join(
                latest_feedback_subquery,
                MentorFeedback.id
                == latest_feedback_subquery
                .c.latest_feedback_id
            )
            .join(
                Student,
                Student.id
                == MentorFeedback.student_id
            )
            .order_by(
                desc(
                    MentorFeedback
                    .communication_score
                ),
                desc(
                    MentorFeedback
                    .leadership_score
                ),
                desc(
                    MentorFeedback
                    .overall_feedback_score
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
            feedback, student = row

            rankings.append({
                "rank": rank,
                "student_id": student.id,
                "student_name": student.name,
                "mentor_id": feedback.mentor_id,

                "communication_score": (
                    feedback.communication_score
                ),

                "communication_level": (
                    feedback.communication_level
                ),

                "leadership_score": (
                    feedback.leadership_score
                ),

                "leadership_potential": (
                    feedback.leadership_potential
                ),

                "overall_feedback_score": (
                    feedback
                    .overall_feedback_score
                ),

                "review_date": (
                    feedback.review_date
                )
            })

        return rankings

    @staticmethod
    def get_weak_communicators(
        db: Session,
        score_threshold: float = 60
    ) -> list[dict[str, Any]]:
        threshold = max(
            0.0,
            min(
                float(score_threshold),
                100.0
            )
        )

        latest_feedback_subquery = (
            db.query(
                MentorFeedback.student_id.label(
                    "student_id"
                ),
                func.max(
                    MentorFeedback.id
                ).label(
                    "latest_feedback_id"
                )
            )
            .group_by(
                MentorFeedback.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                MentorFeedback,
                Student
            )
            .join(
                latest_feedback_subquery,
                MentorFeedback.id
                == latest_feedback_subquery
                .c.latest_feedback_id
            )
            .join(
                Student,
                Student.id
                == MentorFeedback.student_id
            )
            .filter(
                MentorFeedback.communication_score
                < threshold
            )
            .order_by(
                MentorFeedback
                .communication_score
                .asc()
            )
            .all()
        )

        return [
            {
                "student_id": student.id,
                "student_name": student.name,
                "mentor_id": feedback.mentor_id,

                "communication_score": (
                    feedback.communication_score
                ),

                "communication_level": (
                    feedback.communication_level
                ),

                "weak_areas": feedback.weak_areas,

                "improvement_plan": (
                    feedback.improvement_plan
                ),

                "requires_mentor_meeting": (
                    feedback
                    .requires_mentor_meeting
                ),

                "review_date": feedback.review_date
            }
            for feedback, student in rows
        ]

    @staticmethod
    def get_leadership_potential(
        db: Session,
        minimum_score: float = 75
    ) -> list[dict[str, Any]]:
        score = max(
            0.0,
            min(
                float(minimum_score),
                100.0
            )
        )

        latest_feedback_subquery = (
            db.query(
                MentorFeedback.student_id.label(
                    "student_id"
                ),
                func.max(
                    MentorFeedback.id
                ).label(
                    "latest_feedback_id"
                )
            )
            .group_by(
                MentorFeedback.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                MentorFeedback,
                Student
            )
            .join(
                latest_feedback_subquery,
                MentorFeedback.id
                == latest_feedback_subquery
                .c.latest_feedback_id
            )
            .join(
                Student,
                Student.id
                == MentorFeedback.student_id
            )
            .filter(
                MentorFeedback.leadership_score
                >= score
            )
            .order_by(
                desc(
                    MentorFeedback
                    .leadership_score
                ),
                desc(
                    MentorFeedback
                    .communication_score
                )
            )
            .all()
        )

        return [
            {
                "student_id": student.id,
                "student_name": student.name,
                "mentor_id": feedback.mentor_id,

                "leadership_score": (
                    feedback.leadership_score
                ),

                "leadership_potential": (
                    feedback.leadership_potential
                ),

                "communication_score": (
                    feedback.communication_score
                ),

                "overall_feedback_score": (
                    feedback
                    .overall_feedback_score
                ),

                "review_date": feedback.review_date
            }
            for feedback, student in rows
        ]

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

        feedback_records = (
            db.query(MentorFeedback)
            .filter(
                MentorFeedback.review_date
                >= start_date
            )
            .all()
        )

        total_records = len(
            feedback_records
        )

        students_reviewed = len({
            feedback.student_id
            for feedback in feedback_records
        })

        mentors_participated = len({
            feedback.mentor_id
            for feedback in feedback_records
        })

        def count_performance(
            level: str
        ) -> int:
            return sum(
                1
                for feedback in feedback_records
                if feedback.performance_level
                == level
            )

        strong_communicators = sum(
            1
            for feedback in feedback_records
            if feedback.communication_score >= 75
        )

        weak_communicators = sum(
            1
            for feedback in feedback_records
            if feedback.communication_score < 60
        )

        high_leadership = sum(
            1
            for feedback in feedback_records
            if feedback.leadership_potential
            == "High"
        )

        mentor_meetings = sum(
            1
            for feedback in feedback_records
            if feedback.requires_mentor_meeting
        )

        def calculate_average(
            field_name: str
        ) -> float:
            if not feedback_records:
                return 0.0

            total = sum(
                float(
                    getattr(
                        feedback,
                        field_name
                    )
                    or 0
                )
                for feedback in feedback_records
            )

            return round(
                total / total_records,
                2
            )

        return {
            "period_days": safe_period,

            "total_feedback_records": (
                total_records
            ),

            "students_reviewed": students_reviewed,

            "mentors_participated": (
                mentors_participated
            ),

            "excellent_performers": (
                count_performance("Excellent")
            ),

            "good_performers": (
                count_performance("Good")
            ),

            "average_performers": (
                count_performance("Average")
            ),

            "weak_performers": (
                count_performance("Weak")
            ),

            "strong_communicators": (
                strong_communicators
            ),

            "weak_communicators": (
                weak_communicators
            ),

            "high_leadership_potential": (
                high_leadership
            ),

            "mentor_meetings_required": (
                mentor_meetings
            ),

            "average_technical_score": (
                calculate_average(
                    "technical_skill_score"
                )
            ),

            "average_communication_score": (
                calculate_average(
                    "communication_score"
                )
            ),

            "average_leadership_score": (
                calculate_average(
                    "leadership_score"
                )
            ),

            "average_overall_feedback_score": (
                calculate_average(
                    "overall_feedback_score"
                )
            )
        }

    @staticmethod
    def calculate_scores(
        values: dict[str, Any]
    ) -> dict[str, Any]:
        communication_score = (
            float(
                values[
                    "communication_clarity_score"
                ]
            ) * 0.25
            + float(
                values["responsiveness_score"]
            ) * 0.20
            + float(
                values["professionalism_score"]
            ) * 0.20
            + float(
                values["collaboration_score"]
            ) * 0.20
            + float(
                values[
                    "meeting_participation_score"
                ]
            ) * 0.15
        )

        technical_performance = (
            float(
                values["technical_skill_score"]
            ) * 0.30
            + float(
                values["problem_solving_score"]
            ) * 0.25
            + float(
                values["consistency_score"]
            ) * 0.20
            + float(
                values["learning_attitude_score"]
            ) * 0.15
            + float(
                values["leadership_score"]
            ) * 0.10
        )

        overall_score = (
            technical_performance * 0.70
            + communication_score * 0.30
        )

        communication_score = round(
            communication_score,
            2
        )

        overall_score = round(
            overall_score,
            2
        )

        leadership_score = float(
            values["leadership_score"]
        )

        performance_level = (
            MentorFeedbackService
            .get_performance_level(
                overall_score
            )
        )

        communication_level = (
            MentorFeedbackService
            .get_performance_level(
                communication_score
            )
        )

        if (
            leadership_score >= 85
            and communication_score >= 75
            and overall_score >= 80
        ):
            leadership_potential = "High"

        elif (
            leadership_score >= 65
            and communication_score >= 60
        ):
            leadership_potential = "Medium"

        else:
            leadership_potential = "Low"

        requires_meeting = (
            overall_score < 55
            or communication_score < 50
            or float(
                values["consistency_score"]
            ) < 45
        )

        return {
            "communication_score": (
                communication_score
            ),

            "overall_feedback_score": (
                overall_score
            ),

            "performance_level": (
                performance_level
            ),

            "communication_level": (
                communication_level
            ),

            "leadership_potential": (
                leadership_potential
            ),

            "requires_mentor_meeting": (
                requires_meeting
            )
        }

    @staticmethod
    def get_performance_level(
        score: float
    ) -> str:
        if score >= 85:
            return "Excellent"

        if score >= 70:
            return "Good"

        if score >= 55:
            return "Average"

        return "Weak"