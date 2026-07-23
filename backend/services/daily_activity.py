from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import (
    DailyActivity,
    Mentor,
    Student
)
from backend.schemas import (
    DailyActivityCreate,
    DailyActivityUpdate,
    DailyActivityVerificationRequest
)


class DailyActivityService:
    @staticmethod
    def create_activity(
        db: Session,
        student: Student,
        activity_data: DailyActivityCreate
    ) -> DailyActivity:
        if activity_data.activity_date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Daily activity cannot be submitted "
                    "for a future date."
                )
            )

        existing_activity = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id == student.id,
                DailyActivity.activity_date
                == activity_data.activity_date
            )
            .first()
        )

        if existing_activity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An activity record already exists "
                    "for this date."
                )
            )

        activity = DailyActivity(
            student_id=student.id,
            activity_date=activity_data.activity_date,
            task_title=activity_data.task_title,
            work_summary=activity_data.work_summary,
            hours_worked=activity_data.hours_worked,
            task_status=activity_data.task_status,
            repository_url=activity_data.repository_url,
            commit_url=activity_data.commit_url,
            blockers=activity_data.blockers,
            learning_outcome=(
                activity_data.learning_outcome
            ),
            verification_status="Pending",
            is_verified=False
        )

        try:
            db.add(activity)
            db.commit()
            db.refresh(activity)

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An activity record already exists "
                    "for this student and date."
                )
            ) from error

        except Exception:
            db.rollback()
            raise

        return activity

    @staticmethod
    def update_activity(
        db: Session,
        student: Student,
        activity_id: int,
        activity_data: DailyActivityUpdate
    ) -> DailyActivity:
        activity = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.id == activity_id,
                DailyActivity.student_id == student.id
            )
            .first()
        )

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily activity was not found."
            )

        if activity.verification_status == "Verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "A verified daily activity cannot "
                    "be modified."
                )
            )

        update_values = activity_data.model_dump(
            exclude_unset=True
        )

        for field_name, value in update_values.items():
            setattr(
                activity,
                field_name,
                value
            )

        activity.verification_status = "Pending"
        activity.is_verified = False
        activity.mentor_id = None
        activity.mentor_feedback = None
        activity.verified_at = None

        try:
            db.commit()
            db.refresh(activity)

        except Exception:
            db.rollback()
            raise

        return activity

    @staticmethod
    def get_student_activities(
        db: Session,
        student_id: int,
        limit: int = 30
    ) -> list[DailyActivity]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(DailyActivity)
            .filter(
                DailyActivity.student_id == student_id
            )
            .order_by(
                DailyActivity.activity_date.desc(),
                DailyActivity.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def count_student_activities(
        db: Session,
        student_id: int
    ) -> int:
        return (
            db.query(
                func.count(DailyActivity.id)
            )
            .filter(
                DailyActivity.student_id == student_id
            )
            .scalar()
            or 0
        )

    @staticmethod
    def get_activity_by_id(
        db: Session,
        activity_id: int
    ) -> DailyActivity | None:
        return (
            db.query(DailyActivity)
            .filter(
                DailyActivity.id == activity_id
            )
            .first()
        )

    @staticmethod
    def verify_activity(
        db: Session,
        mentor: Mentor,
        activity_id: int,
        verification_data: (
            DailyActivityVerificationRequest
        )
    ) -> DailyActivity:
        activity = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.id == activity_id
            )
            .first()
        )

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily activity was not found."
            )

        student = (
            db.query(Student)
            .filter(
                Student.id == activity.student_id
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
                    "You can only verify activities "
                    "of your assigned students."
                )
            )

        activity.verification_status = (
            verification_data.verification_status
        )

        activity.mentor_feedback = (
            verification_data.mentor_feedback
        )

        activity.mentor_id = mentor.id
        activity.verified_at = datetime.utcnow()

        activity.is_verified = (
            verification_data.verification_status
            == "Verified"
        )

        try:
            db.commit()
            db.refresh(activity)

        except Exception:
            db.rollback()
            raise

        return activity

    @staticmethod
    def get_mentor_student_activities(
        db: Session,
        mentor: Mentor,
        student_id: int,
        limit: int = 30
    ) -> list[DailyActivity]:
        student = (
            db.query(Student)
            .filter(
                Student.id == student_id
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
                    "This student is not assigned "
                    "to the current mentor."
                )
            )

        return (
            DailyActivityService
            .get_student_activities(
                db=db,
                student_id=student_id,
                limit=limit
            )
        )

    @staticmethod
    def get_inactive_students(
        db: Session,
        inactivity_days: int = 3
    ) -> list[dict[str, Any]]:
        safe_days = max(
            1,
            min(inactivity_days, 90)
        )

        today = date.today()
        cutoff_date = today - timedelta(
            days=safe_days
        )

        last_activity_subquery = (
            db.query(
                DailyActivity.student_id.label(
                    "student_id"
                ),
                func.max(
                    DailyActivity.activity_date
                ).label(
                    "last_activity_date"
                )
            )
            .group_by(
                DailyActivity.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                Student,
                last_activity_subquery
                .c.last_activity_date
            )
            .outerjoin(
                last_activity_subquery,
                Student.id
                == last_activity_subquery.c.student_id
            )
            .all()
        )

        inactive_students = []

        for student, last_activity_date in rows:
            if last_activity_date is None:
                inactive_students.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "email": student.email,
                    "batch": student.batch,
                    "mentor_id": student.mentor_id,
                    "last_activity_date": None,
                    "days_inactive": None,
                    "activity_status": (
                        "No Activity Submitted"
                    )
                })

                continue

            days_inactive = (
                today - last_activity_date
            ).days

            if (
                last_activity_date <= cutoff_date
                or days_inactive >= safe_days
            ):
                inactive_students.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "email": student.email,
                    "batch": student.batch,
                    "mentor_id": student.mentor_id,
                    "last_activity_date": (
                        last_activity_date
                    ),
                    "days_inactive": days_inactive,
                    "activity_status": "Inactive"
                })

        inactive_students.sort(
            key=lambda item: (
                item["days_inactive"]
                if item["days_inactive"] is not None
                else 999999
            ),
            reverse=True
        )

        return inactive_students

    @staticmethod
    def get_activity_summary(
        db: Session,
        period_days: int = 7
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

        total_students = (
            db.query(
                func.count(Student.id)
            )
            .scalar()
            or 0
        )

        activities = (
            db.query(DailyActivity)
            .filter(
                DailyActivity.activity_date
                >= start_date
            )
            .all()
        )

        students_with_activity = len({
            activity.student_id
            for activity in activities
        })

        total_records = len(activities)

        verified_records = sum(
            1
            for activity in activities
            if activity.verification_status
            == "Verified"
        )

        pending_records = sum(
            1
            for activity in activities
            if activity.verification_status
            == "Pending"
        )

        rejected_records = sum(
            1
            for activity in activities
            if activity.verification_status
            == "Rejected"
        )

        completed_tasks = sum(
            1
            for activity in activities
            if activity.task_status == "Completed"
        )

        in_progress_tasks = sum(
            1
            for activity in activities
            if activity.task_status
            == "In Progress"
        )

        blocked_tasks = sum(
            1
            for activity in activities
            if activity.task_status == "Blocked"
        )

        total_hours = round(
            sum(
                float(
                    activity.hours_worked
                    or 0
                )
                for activity in activities
            ),
            2
        )

        average_hours = (
            total_hours / total_records
            if total_records > 0
            else 0.0
        )

        submission_rate = (
            students_with_activity
            / total_students
            * 100
            if total_students > 0
            else 0.0
        )

        return {
            "period_days": safe_period,
            "total_students": total_students,
            "students_with_activity": (
                students_with_activity
            ),
            "students_without_activity": max(
                0,
                total_students
                - students_with_activity
            ),
            "total_activity_records": total_records,
            "verified_records": verified_records,
            "pending_records": pending_records,
            "rejected_records": rejected_records,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "total_hours_worked": total_hours,
            "average_hours_per_record": round(
                average_hours,
                2
            ),
            "activity_submission_rate": round(
                submission_rate,
                2
            )
        }