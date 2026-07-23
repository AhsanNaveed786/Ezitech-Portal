from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models import (
    Mentor,
    Student,
    Task
)
from backend.schemas import (
    TaskCreate,
    TaskProgressUpdate,
    TaskReviewRequest,
    TaskSubmissionRequest
)


class TaskManagementService:

    @staticmethod
    def assign_task(
        db: Session,
        mentor: Mentor,
        task_data: TaskCreate
    ) -> Task:
        student = (
            db.query(Student)
            .filter(
                Student.id == task_data.student_id
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
                    "You can only assign tasks to "
                    "your assigned students."
                )
            )

        if task_data.due_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past."
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            student_id=student.id,
            assigned_by_mentor_id=mentor.id,
            difficulty_level=(
                task_data.difficulty_level
            ),
            priority=task_data.priority,
            start_date=task_data.start_date,
            due_date=task_data.due_date,
            status="Assigned",
            progress_percentage=0.0,
            deadline_status="Pending",
            days_late=0
        )

        try:
            db.add(task)
            db.commit()
            db.refresh(task)

        except Exception:
            db.rollback()
            raise

        return task

    @staticmethod
    def update_task_progress(
        db: Session,
        student: Student,
        task_id: int,
        progress_data: TaskProgressUpdate
    ) -> Task:
        task = (
            db.query(Task)
            .filter(
                Task.id == task_id,
                Task.student_id == student.id
            )
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task was not found."
            )

        if task.status in {
            "Submitted",
            "Approved",
            "Cancelled"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Task cannot be updated while "
                    f"its status is {task.status}."
                )
            )

        task.progress_percentage = (
            progress_data.progress_percentage
        )

        task.status = progress_data.status
        task.blockers = progress_data.blockers

        if (
            task.started_at is None
            and progress_data.progress_percentage > 0
        ):
            task.started_at = datetime.now(
                timezone.utc
            )

        TaskManagementService._update_overdue_state(
            task
        )

        try:
            db.commit()
            db.refresh(task)

        except Exception:
            db.rollback()
            raise

        return task

    @staticmethod
    def submit_task(
        db: Session,
        student: Student,
        task_id: int,
        submission_data: TaskSubmissionRequest
    ) -> Task:
        task = (
            db.query(Task)
            .filter(
                Task.id == task_id,
                Task.student_id == student.id
            )
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task was not found."
            )

        if task.status in {
            "Approved",
            "Submitted",
            "Cancelled"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Task cannot be submitted while "
                    f"its status is {task.status}."
                )
            )

        submitted_time = datetime.now(
            timezone.utc
        )

        task.github_repository_url = (
            submission_data.github_repository_url
        )

        task.github_commit_url = (
            submission_data.github_commit_url
        )

        task.submission_notes = (
            submission_data.submission_notes
        )

        task.submitted_at = submitted_time
        task.progress_percentage = 100.0
        task.status = "Submitted"

        TaskManagementService._set_deadline_result(
            task=task,
            completion_date=submitted_time.date()
        )

        try:
            db.commit()
            db.refresh(task)

        except Exception:
            db.rollback()
            raise

        return task

    @staticmethod
    def review_task(
        db: Session,
        mentor: Mentor,
        task_id: int,
        review_data: TaskReviewRequest
    ) -> Task:
        task = (
            db.query(Task)
            .filter(
                Task.id == task_id,
                Task.assigned_by_mentor_id == mentor.id
            )
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Task was not found or is not "
                    "assigned by this mentor."
                )
            )

        if task.status != "Submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only submitted tasks can be reviewed."
                )
            )

        task.mentor_feedback = (
            review_data.mentor_feedback
        )

        task.completion_score = (
            review_data.completion_score
        )

        task.reviewed_at = datetime.now(
            timezone.utc
        )

        if review_data.decision == "Approved":
            task.status = "Approved"
            task.completed_at = task.reviewed_at
            task.progress_percentage = 100.0

        else:
            task.status = "Rejected"
            task.progress_percentage = min(
                task.progress_percentage,
                90.0
            )

        try:
            db.commit()
            db.refresh(task)

        except Exception:
            db.rollback()
            raise

        return task

    @staticmethod
    def get_student_tasks(
        db: Session,
        student_id: int,
        limit: int = 50
    ) -> list[Task]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.student_id == student_id
            )
            .order_by(
                Task.due_date.asc(),
                Task.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

        TaskManagementService._sync_tasks(
            db=db,
            tasks=tasks
        )

        return tasks

    @staticmethod
    def get_mentor_tasks(
        db: Session,
        mentor_id: int,
        limit: int = 100
    ) -> list[Task]:
        safe_limit = max(
            1,
            min(limit, 200)
        )

        tasks = (
            db.query(Task)
            .filter(
                Task.assigned_by_mentor_id
                == mentor_id
            )
            .order_by(
                Task.due_date.asc(),
                Task.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

        TaskManagementService._sync_tasks(
            db=db,
            tasks=tasks
        )

        return tasks

    @staticmethod
    def get_overdue_tasks(
        db: Session
    ) -> list[dict[str, Any]]:
        tasks = (
            db.query(Task)
            .filter(
                Task.status.notin_([
                    "Approved",
                    "Cancelled"
                ]),
                Task.due_date < date.today()
            )
            .all()
        )

        TaskManagementService._sync_tasks(
            db=db,
            tasks=tasks
        )

        results = []

        for task in tasks:
            student = (
                db.query(Student)
                .filter(
                    Student.id == task.student_id
                )
                .first()
            )

            if not student:
                continue

            days_overdue = max(
                0,
                (
                    date.today()
                    - task.due_date
                ).days
            )

            results.append({
                "task_id": task.id,
                "title": task.title,
                "student_id": student.id,
                "student_name": student.name,
                "mentor_id": (
                    task.assigned_by_mentor_id
                ),
                "due_date": task.due_date,
                "status": task.status,
                "progress_percentage": (
                    task.progress_percentage
                ),
                "days_overdue": days_overdue,
                "difficulty_level": (
                    task.difficulty_level
                ),
                "priority": task.priority
            })

        results.sort(
            key=lambda item: (
                item["days_overdue"],
                item["priority"] == "Critical",
                item["priority"] == "High"
            ),
            reverse=True
        )

        return results

    @staticmethod
    def get_task_summary(
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

        tasks = (
            db.query(Task)
            .filter(
                Task.start_date >= start_date
            )
            .all()
        )

        TaskManagementService._sync_tasks(
            db=db,
            tasks=tasks
        )

        total_tasks = len(tasks)

        def count_status(task_status: str) -> int:
            return sum(
                1
                for task in tasks
                if task.status == task_status
            )

        approved_tasks = count_status(
            "Approved"
        )

        on_time_completions = sum(
            1
            for task in tasks
            if task.deadline_status == "On Time"
        )

        late_completions = sum(
            1
            for task in tasks
            if task.deadline_status == "Late"
        )

        completion_scores = [
            float(task.completion_score)
            for task in tasks
            if task.completion_score is not None
        ]

        average_score = (
            sum(completion_scores)
            / len(completion_scores)
            if completion_scores
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
            / total_tasks
            if total_tasks
            else 0.0
        )

        completion_rate = (
            approved_tasks / total_tasks * 100
            if total_tasks
            else 0.0
        )

        deadline_records = (
            on_time_completions
            + late_completions
        )

        deadline_compliance_rate = (
            on_time_completions
            / deadline_records
            * 100
            if deadline_records
            else 0.0
        )

        return {
            "period_days": safe_period,
            "total_tasks": total_tasks,
            "assigned_tasks": count_status(
                "Assigned"
            ),
            "in_progress_tasks": count_status(
                "In Progress"
            ),
            "blocked_tasks": count_status(
                "Blocked"
            ),
            "submitted_tasks": count_status(
                "Submitted"
            ),
            "approved_tasks": approved_tasks,
            "rejected_tasks": count_status(
                "Rejected"
            ),
            "overdue_tasks": count_status(
                "Overdue"
            ),
            "on_time_completions": (
                on_time_completions
            ),
            "late_completions": (
                late_completions
            ),
            "average_completion_score": round(
                average_score,
                2
            ),
            "average_progress_percentage": round(
                average_progress,
                2
            ),
            "task_completion_rate": round(
                completion_rate,
                2
            ),
            "deadline_compliance_rate": round(
                deadline_compliance_rate,
                2
            )
        }

    @staticmethod
    def _set_deadline_result(
        task: Task,
        completion_date: date
    ) -> None:
        if completion_date <= task.due_date:
            task.deadline_status = "On Time"
            task.days_late = 0

        else:
            task.deadline_status = "Late"
            task.days_late = (
                completion_date
                - task.due_date
            ).days

    @staticmethod
    def _update_overdue_state(
        task: Task
    ) -> None:
        if (
            task.due_date < date.today()
            and task.status not in {
                "Approved",
                "Submitted",
                "Cancelled"
            }
        ):
            task.status = "Overdue"
            task.deadline_status = "Overdue"
            task.days_late = (
                date.today()
                - task.due_date
            ).days

    @staticmethod
    def _sync_tasks(
        db: Session,
        tasks: list[Task]
    ) -> None:
        changed = False

        for task in tasks:
            previous_status = task.status
            previous_deadline_status = (
                task.deadline_status
            )

            TaskManagementService._update_overdue_state(
                task
            )

            if (
                previous_status != task.status
                or previous_deadline_status
                != task.deadline_status
            ):
                changed = True

        if changed:
            try:
                db.commit()

                for task in tasks:
                    db.refresh(task)

            except Exception:
                db.rollback()
                raise