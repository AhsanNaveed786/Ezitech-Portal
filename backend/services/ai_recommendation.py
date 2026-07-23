from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    AIRecommendation,
    Admin,
    EngineeringPerformanceRecord,
    Mentor,
    Student
)


class AIRecommendationService:

    @staticmethod
    def generate_recommendations(
        db: Session,
        student_id: int,
        engineering_performance_record_id: int | None = None,
        mentor: Mentor | None = None,
        admin: Admin | None = None
    ) -> list[AIRecommendation]:
        student = (
            db.query(Student)
            .filter(Student.id == student_id)
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
                    "You can only generate recommendations "
                    "for your assigned students."
                )
            )

        performance_record = (
            AIRecommendationService
            ._get_performance_record(
                db=db,
                student_id=student.id,
                record_id=(
                    engineering_performance_record_id
                )
            )
        )

        component_scores = {
            "attendance": float(
                performance_record.attendance_score
            ),
            "github": float(
                performance_record.github_score
            ),
            "daily_activity": float(
                performance_record.daily_activity_score
            ),
            "tasks": float(
                performance_record.task_score
            ),
            "case_studies": float(
                performance_record.case_study_score
            ),
            "mentor_feedback": float(
                performance_record.mentor_feedback_score
            ),
            "communication": float(
                performance_record.communication_score
            ),
            "deadline_compliance": float(
                performance_record
                .deadline_compliance_score
            ),
            "learning_speed": float(
                performance_record.learning_speed_score
            ),
            "engineering_credits": float(
                performance_record.engineering_credit_score
            )
        }

        recommendation_definitions = (
            AIRecommendationService
            ._build_recommendations(
                performance_record=performance_record,
                component_scores=component_scores
            )
        )

        generated_recommendations = []

        for recommendation_data in (
            recommendation_definitions
        ):
            existing = (
                db.query(AIRecommendation)
                .filter(
                    AIRecommendation.student_id
                    == student.id,

                    AIRecommendation
                    .engineering_performance_record_id
                    == performance_record.id,

                    AIRecommendation.recommendation_type
                    == recommendation_data[
                        "recommendation_type"
                    ]
                )
                .first()
            )

            if existing:
                generated_recommendations.append(
                    existing
                )
                continue

            recommendation = AIRecommendation(
                student_id=student.id,

                mentor_id=(
                    mentor.id
                    if mentor
                    else student.mentor_id
                ),

                engineering_performance_record_id=(
                    performance_record.id
                ),

                recommendation_type=(
                    recommendation_data[
                        "recommendation_type"
                    ]
                ),

                category=(
                    recommendation_data["category"]
                ),

                title=recommendation_data["title"],

                recommendation_reason=(
                    recommendation_data["reason"]
                ),

                recommended_action=(
                    recommendation_data["action"]
                ),

                confidence_score=(
                    recommendation_data[
                        "confidence_score"
                    ]
                ),

                priority_score=(
                    recommendation_data[
                        "priority_score"
                    ]
                ),

                priority_level=(
                    AIRecommendationService
                    ._get_priority_level(
                        recommendation_data[
                            "priority_score"
                        ]
                    )
                ),

                status="Generated",

                supporting_data={
                    "final_engineering_score": (
                        performance_record
                        .final_engineering_score
                    ),
                    "performance_level": (
                        performance_record
                        .performance_level
                    ),
                    "data_completeness_percentage": (
                        performance_record
                        .data_completeness_percentage
                    ),
                    "component_scores": (
                        component_scores
                    )
                },

                strong_areas=(
                    performance_record.strong_areas
                    or []
                ),

                weak_areas=(
                    performance_record.weak_areas
                    or []
                ),

                requires_human_review=True
            )

            db.add(recommendation)
            generated_recommendations.append(
                recommendation
            )

        try:
            db.commit()

            for recommendation in (
                generated_recommendations
            ):
                db.refresh(recommendation)

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "One or more recommendations already "
                    "exist for this performance record."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return generated_recommendations

    @staticmethod
    def submit_for_approval(
        db: Session,
        mentor: Mentor,
        recommendation_id: int
    ) -> AIRecommendation:
        recommendation = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.id
                == recommendation_id,
                AIRecommendation.mentor_id
                == mentor.id
            )
            .first()
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Recommendation was not found or "
                    "does not belong to this mentor."
                )
            )

        if recommendation.status != "Generated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only generated recommendations can "
                    "be submitted for approval."
                )
            )

        recommendation.status = "Pending Approval"
        recommendation.submitted_for_approval_at = (
            datetime.now(timezone.utc)
        )

        try:
            db.commit()
            db.refresh(recommendation)

        except Exception:
            db.rollback()
            raise

        return recommendation

    @staticmethod
    def review_recommendation(
        db: Session,
        admin: Admin,
        recommendation_id: int,
        new_status: str,
        review_notes: str | None
    ) -> AIRecommendation:
        recommendation = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.id
                == recommendation_id
            )
            .first()
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation was not found."
            )

        if recommendation.status not in {
            "Generated",
            "Pending Approval"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only generated or pending recommendations "
                    "can be reviewed."
                )
            )

        if new_status not in {
            "Approved",
            "Rejected"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Admin decision must be Approved "
                    "or Rejected."
                )
            )

        recommendation.status = new_status
        recommendation.reviewed_by_admin_id = admin.id
        recommendation.reviewed_at = (
            datetime.now(timezone.utc)
        )
        recommendation.review_notes = review_notes

        try:
            db.commit()
            db.refresh(recommendation)

        except Exception:
            db.rollback()
            raise

        return recommendation

    @staticmethod
    def complete_recommendation(
        db: Session,
        mentor: Mentor,
        recommendation_id: int,
        completion_notes: str
    ) -> AIRecommendation:
        recommendation = (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.id
                == recommendation_id,
                AIRecommendation.mentor_id
                == mentor.id
            )
            .first()
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Recommendation was not found or "
                    "does not belong to this mentor."
                )
            )

        if recommendation.status != "Approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only approved recommendations can "
                    "be marked as completed."
                )
            )

        recommendation.status = "Completed"
        recommendation.completed_at = (
            datetime.now(timezone.utc)
        )
        recommendation.completion_notes = (
            completion_notes
        )

        try:
            db.commit()
            db.refresh(recommendation)

        except Exception:
            db.rollback()
            raise

        return recommendation

    @staticmethod
    def get_recommendation_by_id(
        db: Session,
        recommendation_id: int
    ) -> AIRecommendation | None:
        return (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.id
                == recommendation_id
            )
            .first()
        )

    @staticmethod
    def get_student_recommendations(
        db: Session,
        student_id: int,
        limit: int = 100
    ) -> list[AIRecommendation]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        return (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.student_id
                == student_id
            )
            .order_by(
                AIRecommendation.priority_score.desc(),
                AIRecommendation.generated_at.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_mentor_recommendations(
        db: Session,
        mentor_id: int,
        limit: int = 100
    ) -> list[AIRecommendation]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        return (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.mentor_id
                == mentor_id
            )
            .order_by(
                AIRecommendation.priority_score.desc(),
                AIRecommendation.generated_at.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_pending_recommendations(
        db: Session,
        limit: int = 100
    ) -> list[AIRecommendation]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        return (
            db.query(AIRecommendation)
            .filter(
                AIRecommendation.status
                == "Pending Approval"
            )
            .order_by(
                AIRecommendation.priority_score.desc(),
                AIRecommendation.generated_at.asc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def get_students_by_recommendation(
        db: Session,
        recommendation_type: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        valid_types = {
            "Promote Intern",
            "Assign Advanced Case Study",
            "Assign Easier Case Study",
            "Schedule Mentor Meeting",
            "Recommend Interview",
            "Recommend Job Placement",
            "Recommend Internship Extension",
            "Recommend Certificate Eligibility"
        }

        if recommendation_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recommendation type."
            )

        rows = (
            db.query(
                AIRecommendation,
                Student,
                EngineeringPerformanceRecord
            )
            .join(
                Student,
                Student.id
                == AIRecommendation.student_id
            )
            .join(
                EngineeringPerformanceRecord,
                EngineeringPerformanceRecord.id
                == AIRecommendation
                .engineering_performance_record_id
            )
            .filter(
                AIRecommendation.recommendation_type
                == recommendation_type
            )
            .order_by(
                desc(AIRecommendation.confidence_score),
                desc(
                    EngineeringPerformanceRecord
                    .final_engineering_score
                )
            )
            .limit(safe_limit)
            .all()
        )

        return [
            {
                "student_id": student.id,
                "student_name": student.name,
                "batch": student.batch,

                "recommendation_id": (
                    recommendation.id
                ),

                "recommendation_type": (
                    recommendation
                    .recommendation_type
                ),

                "confidence_score": (
                    recommendation
                    .confidence_score
                ),

                "priority_level": (
                    recommendation.priority_level
                ),

                "status": recommendation.status,

                "final_engineering_score": (
                    performance
                    .final_engineering_score
                ),

                "generated_at": (
                    recommendation.generated_at
                )
            }
            for recommendation, student, performance
            in rows
        ]

    @staticmethod
    def get_summary(
        db: Session
    ) -> dict[str, Any]:
        recommendations = (
            db.query(AIRecommendation)
            .all()
        )

        total = len(recommendations)

        def count_status(
            status_value: str
        ) -> int:
            return sum(
                1
                for recommendation in recommendations
                if recommendation.status == status_value
            )

        def count_priority(
            priority: str
        ) -> int:
            return sum(
                1
                for recommendation in recommendations
                if recommendation.priority_level
                == priority
            )

        def count_type(
            recommendation_type: str
        ) -> int:
            return sum(
                1
                for recommendation in recommendations
                if recommendation.recommendation_type
                == recommendation_type
            )

        average_confidence = (
            sum(
                float(
                    recommendation.confidence_score
                )
                for recommendation in recommendations
            )
            / total
            if total
            else 0.0
        )

        return {
            "total_recommendations": total,

            "generated_recommendations": (
                count_status("Generated")
            ),

            "pending_approval_recommendations": (
                count_status("Pending Approval")
            ),

            "approved_recommendations": (
                count_status("Approved")
            ),

            "rejected_recommendations": (
                count_status("Rejected")
            ),

            "completed_recommendations": (
                count_status("Completed")
            ),

            "critical_priority": count_priority(
                "Critical"
            ),

            "high_priority": count_priority(
                "High"
            ),

            "medium_priority": count_priority(
                "Medium"
            ),

            "low_priority": count_priority(
                "Low"
            ),

            "promote_intern": count_type(
                "Promote Intern"
            ),

            "advanced_case_study": count_type(
                "Assign Advanced Case Study"
            ),

            "easier_case_study": count_type(
                "Assign Easier Case Study"
            ),

            "mentor_meeting": count_type(
                "Schedule Mentor Meeting"
            ),

            "interview_recommendations": count_type(
                "Recommend Interview"
            ),

            "job_placement_recommendations": count_type(
                "Recommend Job Placement"
            ),

            "internship_extensions": count_type(
                "Recommend Internship Extension"
            ),

            "certificate_recommendations": count_type(
                "Recommend Certificate Eligibility"
            ),

            "average_confidence_score": round(
                average_confidence,
                2
            )
        }

    @staticmethod
    def _get_performance_record(
        db: Session,
        student_id: int,
        record_id: int | None
    ) -> EngineeringPerformanceRecord:
        query = (
            db.query(EngineeringPerformanceRecord)
            .filter(
                EngineeringPerformanceRecord.student_id
                == student_id
            )
        )

        if record_id is not None:
            record = (
                query.filter(
                    EngineeringPerformanceRecord.id
                    == record_id
                )
                .first()
            )

        else:
            record = (
                query.order_by(
                    EngineeringPerformanceRecord
                    .period_end
                    .desc(),

                    EngineeringPerformanceRecord
                    .id
                    .desc()
                )
                .first()
            )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "No engineering performance record "
                    "was found for this student."
                )
            )

        return record

    @staticmethod
    def _build_recommendations(
        performance_record: EngineeringPerformanceRecord,
        component_scores: dict[str, float]
    ) -> list[dict[str, Any]]:
        final_score = float(
            performance_record.final_engineering_score
        )

        completeness = float(
            performance_record
            .data_completeness_percentage
        )

        recommendations = []

        if (
            performance_record.promotion_readiness
            or (
                final_score >= 80
                and completeness >= 70
            )
        ):
            recommendations.append({
                "recommendation_type": "Promote Intern",
                "category": "Performance",
                "title": "Intern is ready for promotion",
                "reason": (
                    "The intern has achieved a strong "
                    "engineering score with sufficient "
                    "performance data."
                ),
                "action": (
                    "Review the intern for promotion or "
                    "additional engineering responsibility."
                ),
                "confidence_score": (
                    AIRecommendationService
                    ._calculate_confidence(
                        base_score=final_score,
                        completeness=completeness
                    )
                ),
                "priority_score": final_score
            })

        if (
            component_scores["case_studies"] >= 78
            and component_scores["learning_speed"] >= 65
            and final_score >= 72
        ):
            confidence = (
                component_scores["case_studies"]
                * 0.50
                + component_scores["learning_speed"]
                * 0.25
                + final_score
                * 0.25
            )

            recommendations.append({
                "recommendation_type": (
                    "Assign Advanced Case Study"
                ),
                "category": "Learning",
                "title": (
                    "Assign an advanced case study"
                ),
                "reason": (
                    "The intern demonstrates strong "
                    "case-study performance and an "
                    "acceptable learning speed."
                ),
                "action": (
                    "Assign an advanced case study in "
                    "the intern's current technology."
                ),
                "confidence_score": round(
                    confidence,
                    2
                ),
                "priority_score": round(
                    confidence,
                    2
                )
            })

        if (
            component_scores["case_studies"] < 60
            or component_scores["tasks"] < 55
        ):
            weakness_score = (
                100
                - min(
                    component_scores["case_studies"],
                    component_scores["tasks"]
                )
            )

            recommendations.append({
                "recommendation_type": (
                    "Assign Easier Case Study"
                ),
                "category": "Learning",
                "title": (
                    "Assign an easier guided case study"
                ),
                "reason": (
                    "Task or case-study performance is "
                    "below the expected level."
                ),
                "action": (
                    "Assign a smaller case study with "
                    "clear milestones and mentor guidance."
                ),
                "confidence_score": round(
                    min(
                        100,
                        weakness_score
                        + completeness * 0.20
                    ),
                    2
                ),
                "priority_score": round(
                    weakness_score,
                    2
                )
            })

        if (
            component_scores["communication"] < 60
            or component_scores["mentor_feedback"] < 55
            or component_scores["daily_activity"] < 50
        ):
            lowest_score = min(
                component_scores["communication"],
                component_scores["mentor_feedback"],
                component_scores["daily_activity"]
            )

            urgency = 100 - lowest_score

            recommendations.append({
                "recommendation_type": (
                    "Schedule Mentor Meeting"
                ),
                "category": "Mentoring",
                "title": (
                    "Schedule an individual mentor meeting"
                ),
                "reason": (
                    "Communication, mentor feedback or "
                    "daily activity performance requires "
                    "additional attention."
                ),
                "action": (
                    "Schedule a one-to-one meeting and "
                    "create a measurable improvement plan."
                ),
                "confidence_score": round(
                    min(
                        100,
                        urgency
                        + completeness * 0.20
                    ),
                    2
                ),
                "priority_score": round(
                    urgency,
                    2
                )
            })

        if (
            final_score >= 72
            and component_scores["communication"] >= 65
            and component_scores["github"] >= 60
        ):
            confidence = (
                final_score * 0.50
                + component_scores["communication"]
                * 0.25
                + component_scores["github"]
                * 0.25
            )

            recommendations.append({
                "recommendation_type": (
                    "Recommend Interview"
                ),
                "category": "Placement",
                "title": (
                    "Recommend the intern for an interview"
                ),
                "reason": (
                    "The intern has sufficient technical, "
                    "communication and GitHub performance."
                ),
                "action": (
                    "Arrange a technical interview or "
                    "mock client interview."
                ),
                "confidence_score": round(
                    confidence,
                    2
                ),
                "priority_score": round(
                    confidence,
                    2
                )
            })

        if performance_record.placement_readiness:
            confidence = (
                final_score * 0.60
                + component_scores["communication"]
                * 0.20
                + component_scores[
                    "deadline_compliance"
                ]
                * 0.20
            )

            recommendations.append({
                "recommendation_type": (
                    "Recommend Job Placement"
                ),
                "category": "Placement",
                "title": (
                    "Recommend the intern for job placement"
                ),
                "reason": (
                    "The engineering performance record "
                    "indicates placement readiness."
                ),
                "action": (
                    "Move the intern to the placement "
                    "review and employer-shortlisting process."
                ),
                "confidence_score": round(
                    confidence,
                    2
                ),
                "priority_score": round(
                    confidence,
                    2
                )
            })

        if (
            final_score < 60
            or completeness < 60
            or component_scores["learning_speed"] < 50
        ):
            risk_score = (
                (100 - final_score) * 0.50
                + (100 - completeness) * 0.25
                + (
                    100
                    - component_scores["learning_speed"]
                ) * 0.25
            )

            recommendations.append({
                "recommendation_type": (
                    "Recommend Internship Extension"
                ),
                "category": "Performance",
                "title": (
                    "Consider extending the internship"
                ),
                "reason": (
                    "The intern requires additional time "
                    "or more complete performance evidence."
                ),
                "action": (
                    "Review the internship duration and "
                    "define an improvement period."
                ),
                "confidence_score": round(
                    risk_score,
                    2
                ),
                "priority_score": round(
                    risk_score,
                    2
                )
            })

        if performance_record.certificate_eligibility:
            confidence = (
                final_score * 0.60
                + component_scores["attendance"]
                * 0.20
                + component_scores[
                    "deadline_compliance"
                ]
                * 0.20
            )

            recommendations.append({
                "recommendation_type": (
                    "Recommend Certificate Eligibility"
                ),
                "category": "Certification",
                "title": (
                    "Intern is eligible for certificate review"
                ),
                "reason": (
                    "The intern meets the current score, "
                    "attendance and deadline requirements."
                ),
                "action": (
                    "Submit the intern for final certificate "
                    "eligibility verification."
                ),
                "confidence_score": round(
                    confidence,
                    2
                ),
                "priority_score": round(
                    confidence,
                    2
                )
            })

        return recommendations

    @staticmethod
    def _calculate_confidence(
        base_score: float,
        completeness: float
    ) -> float:
        return round(
            base_score * 0.70
            + completeness * 0.30,
            2
        )

    @staticmethod
    def _get_priority_level(
        priority_score: float
    ) -> str:
        if priority_score >= 85:
            return "Critical"

        if priority_score >= 70:
            return "High"

        if priority_score >= 50:
            return "Medium"

        return "Low"