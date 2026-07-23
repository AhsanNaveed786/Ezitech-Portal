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

class CaseStudy(Base):
    __tablename__ = "case_studies"

    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 "
            "AND progress_percentage <= 100",
            name="check_case_study_progress"
        ),
        CheckConstraint(
            "revision_count >= 0",
            name="check_case_study_revision_count"
        ),
        CheckConstraint(
            "technical_score IS NULL OR "
            "(technical_score >= 0 AND technical_score <= 100)",
            name="check_case_study_technical_score"
        ),
        CheckConstraint(
            "code_quality_score IS NULL OR "
            "(code_quality_score >= 0 AND code_quality_score <= 100)",
            name="check_case_study_code_quality_score"
        ),
        CheckConstraint(
            "documentation_score IS NULL OR "
            "(documentation_score >= 0 AND documentation_score <= 100)",
            name="check_case_study_documentation_score"
        ),
        CheckConstraint(
            "problem_solving_score IS NULL OR "
            "(problem_solving_score >= 0 AND problem_solving_score <= 100)",
            name="check_case_study_problem_solving_score"
        ),
        CheckConstraint(
            "presentation_score IS NULL OR "
            "(presentation_score >= 0 AND presentation_score <= 100)",
            name="check_case_study_presentation_score"
        ),
        CheckConstraint(
            "final_score IS NULL OR "
            "(final_score >= 0 AND final_score <= 100)",
            name="check_case_study_final_score"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(250),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    objectives = Column(
        Text,
        nullable=False
    )

    requirements = Column(
        Text,
        nullable=True
    )

    technology = Column(
        String(100),
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=False,
        index=True
    )

    difficulty_level = Column(
        Enum(
            "Easy",
            "Medium",
            "Advanced",
            name="case_study_difficulty_enum"
        ),
        nullable=False,
        default="Medium",
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

    assigned_by_mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    status = Column(
        Enum(
            "Assigned",
            "In Progress",
            "Submitted",
            "Revision Required",
            "Resubmitted",
            "Approved",
            "Failed",
            "Cancelled",
            "Overdue",
            name="case_study_status_enum"
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

    evaluated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    github_repository_url = Column(
        String(500),
        nullable=True
    )

    live_demo_url = Column(
        String(500),
        nullable=True
    )

    documentation_url = Column(
        String(500),
        nullable=True
    )

    submission_notes = Column(
        Text,
        nullable=True
    )

    student_blockers = Column(
        Text,
        nullable=True
    )

    learning_outcome = Column(
        Text,
        nullable=True
    )

    technical_score = Column(
        Float,
        nullable=True
    )

    code_quality_score = Column(
        Float,
        nullable=True
    )

    documentation_score = Column(
        Float,
        nullable=True
    )

    problem_solving_score = Column(
        Float,
        nullable=True
    )

    presentation_score = Column(
        Float,
        nullable=True
    )

    final_score = Column(
        Float,
        nullable=True
    )

    performance_level = Column(
        Enum(
            "Excellent",
            "Good",
            "Average",
            "Weak",
            name="case_study_performance_enum"
        ),
        nullable=True,
        index=True
    )

    mentor_feedback = Column(
        Text,
        nullable=True
    )

    strengths = Column(
        Text,
        nullable=True
    )

    weak_areas = Column(
        Text,
        nullable=True
    )

    revision_instructions = Column(
        Text,
        nullable=True
    )

    revision_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    deadline_status = Column(
        Enum(
            "Pending",
            "On Time",
            "Late",
            "Overdue",
            name="case_study_deadline_enum"
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

class MentorFeedback(Base):
    __tablename__ = "mentor_feedback"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "mentor_id",
            "review_date",
            name="uq_student_mentor_feedback_date"
        ),

        CheckConstraint(
            "technical_skill_score >= 0 "
            "AND technical_skill_score <= 100",
            name="check_feedback_technical_skill"
        ),

        CheckConstraint(
            "problem_solving_score >= 0 "
            "AND problem_solving_score <= 100",
            name="check_feedback_problem_solving"
        ),

        CheckConstraint(
            "consistency_score >= 0 "
            "AND consistency_score <= 100",
            name="check_feedback_consistency"
        ),

        CheckConstraint(
            "learning_attitude_score >= 0 "
            "AND learning_attitude_score <= 100",
            name="check_feedback_learning_attitude"
        ),

        CheckConstraint(
            "leadership_score >= 0 "
            "AND leadership_score <= 100",
            name="check_feedback_leadership"
        ),

        CheckConstraint(
            "communication_clarity_score >= 0 "
            "AND communication_clarity_score <= 100",
            name="check_feedback_communication_clarity"
        ),

        CheckConstraint(
            "responsiveness_score >= 0 "
            "AND responsiveness_score <= 100",
            name="check_feedback_responsiveness"
        ),

        CheckConstraint(
            "professionalism_score >= 0 "
            "AND professionalism_score <= 100",
            name="check_feedback_professionalism"
        ),

        CheckConstraint(
            "collaboration_score >= 0 "
            "AND collaboration_score <= 100",
            name="check_feedback_collaboration"
        ),

        CheckConstraint(
            "meeting_participation_score >= 0 "
            "AND meeting_participation_score <= 100",
            name="check_feedback_meeting_participation"
        ),

        CheckConstraint(
            "communication_score >= 0 "
            "AND communication_score <= 100",
            name="check_feedback_communication_score"
        ),

        CheckConstraint(
            "overall_feedback_score >= 0 "
            "AND overall_feedback_score <= 100",
            name="check_feedback_overall_score"
        ),
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

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    review_date = Column(
        Date,
        nullable=False,
        index=True
    )

    review_period = Column(
        Enum(
            "Weekly",
            "Monthly",
            "Final",
            name="mentor_feedback_period_enum"
        ),
        nullable=False,
        default="Weekly"
    )

    technical_skill_score = Column(
        Float,
        nullable=False
    )

    problem_solving_score = Column(
        Float,
        nullable=False
    )

    consistency_score = Column(
        Float,
        nullable=False
    )

    learning_attitude_score = Column(
        Float,
        nullable=False
    )

    leadership_score = Column(
        Float,
        nullable=False
    )

    communication_clarity_score = Column(
        Float,
        nullable=False
    )

    responsiveness_score = Column(
        Float,
        nullable=False
    )

    professionalism_score = Column(
        Float,
        nullable=False
    )

    collaboration_score = Column(
        Float,
        nullable=False
    )

    meeting_participation_score = Column(
        Float,
        nullable=False
    )

    communication_score = Column(
        Float,
        nullable=False
    )

    overall_feedback_score = Column(
        Float,
        nullable=False
    )

    performance_level = Column(
        Enum(
            "Excellent",
            "Good",
            "Average",
            "Weak",
            name="mentor_feedback_performance_enum"
        ),
        nullable=False,
        index=True
    )

    communication_level = Column(
        Enum(
            "Excellent",
            "Good",
            "Average",
            "Weak",
            name="communication_performance_enum"
        ),
        nullable=False,
        index=True
    )

    strengths = Column(
        Text,
        nullable=True
    )

    weak_areas = Column(
        Text,
        nullable=True
    )

    improvement_plan = Column(
        Text,
        nullable=True
    )

    general_feedback = Column(
        Text,
        nullable=False
    )

    leadership_potential = Column(
        Enum(
            "High",
            "Medium",
            "Low",
            name="leadership_potential_enum"
        ),
        nullable=False,
        default="Low",
        index=True
    )

    requires_mentor_meeting = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )