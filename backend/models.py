from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func
)

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func
)


from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func
)
from sqlalchemy.dialects.postgresql import JSONB

from backend.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    phone_number = Column(
        String(11),
        unique=True,
        nullable=False
    )

    github_username = Column(
        String(100),
        unique=True,
        nullable=True
    )

    gender = Column(
        Enum(
            "Male",
            "Female",
            "Other",
            name="gender_enum"
        ),
        nullable=False
    )

    batch = Column(
        String(20),
        nullable=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    phone_number = Column(
        String(11),
        unique=True,
        nullable=False
    )

    gender = Column(
        Enum(
            "Male",
            "Female",
            "Other",
            name="gender_enum"
        ),
        nullable=False
    )

    department = Column(
        String(50),
        nullable=False
    )


class Admin(Base):
    __tablename__ = "admins"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    phone_number = Column(
        String(11),
        unique=True,
        nullable=False
    )

    gender = Column(
        Enum(
            "Male",
            "Female",
            "Other",
            name="gender_enum"
        ),
        nullable=False
    )


class CEO(Base):
    __tablename__ = "ceos"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    phone_number = Column(
        String(11),
        unique=True,
        nullable=False
    )

    gender = Column(
        Enum(
            "Male",
            "Female",
            "Other",
            name="gender_enum"
        ),
        nullable=False
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    date = Column(
        Date,
        nullable=False
    )

    status = Column(
        Enum(
            "Present",
            "Absent",
            name="attendance_enum"
        ),
        nullable=False
    )

    checked_in_time = Column(
        DateTime,
        nullable=True
    )

    checked_out_time = Column(
        DateTime,
        nullable=True
    )


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(
        Integer,
        primary_key=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    reason = Column(
        String(500),
        nullable=False
    )

    leave_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        Enum(
            "Pending",
            "Approved",
            "Rejected",
            name="leave_status_enum"
        ),
        default="Pending",
        nullable=False
    )

    applied_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    title = Column(
        String(150),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=False
    )

    github_link = Column(
        String(300),
        nullable=False
    )

    tech_stack = Column(
        String(300),
        nullable=False
    )

    status = Column(
        Enum(
            "Pending",
            "Approved",
            "Rejected",
            name="project_status_enum"
        ),
        default="Pending",
        nullable=False
    )

    mentor_remarks = Column(
        String(1000),
        nullable=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    submitted_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )


class GitHubReport(Base):
    __tablename__ = "github_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    github_username = Column(
        String(100),
        nullable=False,
        index=True
    )

    profile_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    activity_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    repository_quality_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    documentation_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    testing_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    ai_code_quality_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    final_github_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True
    )

    performance_level = Column(
        String(50),
        nullable=False
    )

    assessment_status = Column(
        String(30),
        nullable=False,
        default="partial"
    )

    repositories_analyzed = Column(
        Integer,
        nullable=False,
        default=0
    )

    repositories_with_ai_review = Column(
        Integer,
        nullable=False,
        default=0
    )

    best_repository_name = Column(
        String(255),
        nullable=True
    )

    report_json = Column(
        JSONB,
        nullable=False
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )


class DailyActivity(Base):
    __tablename__ = "daily_activities"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "activity_date",
            name="uq_student_daily_activity"
        ),
        CheckConstraint(
            "hours_worked >= 0 AND hours_worked <= 24",
            name="check_daily_activity_hours"
        )
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    activity_date = Column(
        Date,
        nullable=False,
        index=True
    )

    task_title = Column(
        String(200),
        nullable=False
    )

    work_summary = Column(
        String(2000),
        nullable=False
    )

    hours_worked = Column(
        Float,
        nullable=False,
        default=0.0
    )

    task_status = Column(
        Enum(
            "Not Started",
            "In Progress",
            "Completed",
            "Blocked",
            name="daily_task_status_enum"
        ),
        nullable=False,
        default="In Progress"
    )

    repository_url = Column(
        String(500),
        nullable=True
    )

    commit_url = Column(
        String(500),
        nullable=True
    )

    blockers = Column(
        String(1000),
        nullable=True
    )

    learning_outcome = Column(
        String(1500),
        nullable=True
    )

    submitted_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    verification_status = Column(
        Enum(
            "Pending",
            "Verified",
            "Rejected",
            name="activity_verification_status_enum"
        ),
        nullable=False,
        default="Pending",
        index=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    mentor_feedback = Column(
        String(1500),
        nullable=True
    )

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    verified_at = Column(
        DateTime,
        nullable=True
    )

class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 "
            "AND progress_percentage <= 100",
            name="check_task_progress_percentage"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    assigned_by_mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    difficulty_level = Column(
        Enum(
            "Easy",
            "Medium",
            "Advanced",
            name="task_difficulty_enum"
        ),
        nullable=False,
        default="Medium"
    )

    priority = Column(
        Enum(
            "Low",
            "Medium",
            "High",
            "Critical",
            name="task_priority_enum"
        ),
        nullable=False,
        default="Medium"
    )

    status = Column(
        Enum(
            "Assigned",
            "In Progress",
            "Completed",
            "Blocked",
            "Submitted",
            "Approved",
            "Rejected",
            "Overdue",
            "Cancelled",
            name="task_status_enum"
        ),
        nullable=False,
        default="Assigned",
        index=True
    )

    progress_percentage = Column(
        Float,
        nullable=False,
        default=0.0
    )

    assigned_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    start_date = Column(
        Date,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False,
        index=True
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    github_repository_url = Column(
        String(500),
        nullable=True
    )

    github_commit_url = Column(
        String(500),
        nullable=True
    )

    submission_notes = Column(
        Text,
        nullable=True
    )

    blockers = Column(
        Text,
        nullable=True
    )

    mentor_feedback = Column(
        Text,
        nullable=True
    )

    completion_score = Column(
        Float,
        nullable=True
    )

    deadline_status = Column(
        Enum(
            "Pending",
            "On Time",
            "Late",
            "Overdue",
            name="deadline_status_enum"
        ),
        nullable=False,
        default="Pending",
        index=True
    )

    days_late = Column(
        Integer,
        nullable=False,
        default=0
    )