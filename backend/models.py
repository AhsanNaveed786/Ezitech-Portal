from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
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

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "date",
            name="uq_student_attendance_date"
        ),

        UniqueConstraint(
            "mentor_id",
            "date",
            name="uq_mentor_attendance_date"
        ),

        CheckConstraint(
            """
            (
                student_id IS NOT NULL
                AND mentor_id IS NULL
            )
            OR
            (
                student_id IS NULL
                AND mentor_id IS NOT NULL
            )
            """,
            name="check_attendance_owner"
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
        nullable=True,
        index=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    date = Column(
        Date,
        nullable=False,
        index=True
    )

    status = Column(
        Enum(
            "Present",
            "Absent",
            name="attendance_enum"
        ),
        nullable=False,
        default="Present",
        index=True
    )

    checked_in_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    checked_out_time = Column(
        DateTime(timezone=True),
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

class LearningSpeedRecord(Base):
    __tablename__ = "learning_speed_records"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "period_start",
            "period_end",
            name="uq_learning_speed_student_period"
        ),
        CheckConstraint(
            "task_speed_score >= 0 "
            "AND task_speed_score <= 100",
            name="check_learning_task_speed"
        ),
        CheckConstraint(
            "case_study_growth_score >= 0 "
            "AND case_study_growth_score <= 100",
            name="check_learning_case_study_growth"
        ),
        CheckConstraint(
            "revision_efficiency_score >= 0 "
            "AND revision_efficiency_score <= 100",
            name="check_learning_revision_efficiency"
        ),
        CheckConstraint(
            "activity_consistency_score >= 0 "
            "AND activity_consistency_score <= 100",
            name="check_learning_activity_consistency"
        ),
        CheckConstraint(
            "deadline_learning_score >= 0 "
            "AND deadline_learning_score <= 100",
            name="check_learning_deadline_score"
        ),
        CheckConstraint(
            "learning_speed_score >= 0 "
            "AND learning_speed_score <= 100",
            name="check_learning_speed_score"
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

    period_start = Column(
        Date,
        nullable=False,
        index=True
    )

    period_end = Column(
        Date,
        nullable=False,
        index=True
    )

    tasks_completed = Column(
        Integer,
        nullable=False,
        default=0
    )

    case_studies_completed = Column(
        Integer,
        nullable=False,
        default=0
    )

    activity_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    average_task_completion_days = Column(
        Float,
        nullable=False,
        default=0.0
    )

    average_case_study_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    average_revision_count = Column(
        Float,
        nullable=False,
        default=0.0
    )

    task_speed_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    case_study_growth_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    revision_efficiency_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    activity_consistency_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    deadline_learning_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    learning_speed_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True
    )

    previous_period_score = Column(
        Float,
        nullable=True
    )

    growth_percentage = Column(
        Float,
        nullable=False,
        default=0.0
    )

    learning_level = Column(
        Enum(
            "Fast Learner",
            "Steady Learner",
            "Needs Improvement",
            "Insufficient Data",
            name="learning_speed_level_enum"
        ),
        nullable=False,
        default="Insufficient Data",
        index=True
    )

    analysis_notes = Column(
        Text,
        nullable=True
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class EngineeringCredit(Base):
    __tablename__ = "engineering_credits"

    __table_args__ = (
        CheckConstraint(
            "credit_value >= -1000 "
            "AND credit_value <= 1000",
            name="check_engineering_credit_value"
        ),
        UniqueConstraint(
            "student_id",
            "source_type",
            "source_id",
            "category",
            name="uq_engineering_credit_source"
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

    awarded_by_mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    category = Column(
        Enum(
            "Task Completion",
            "Case Study",
            "GitHub Contribution",
            "Communication",
            "Leadership",
            "Consistency",
            "Deadline Compliance",
            "Learning Growth",
            "Bonus",
            "Penalty",
            name="engineering_credit_category_enum"
        ),
        nullable=False,
        index=True
    )

    credit_value = Column(
        Integer,
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    source_type = Column(
        String(100),
        nullable=True
    )

    source_id = Column(
        Integer,
        nullable=True
    )

    awarded_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

class EngineeringPerformanceRecord(Base):
    __tablename__ = "engineering_performance_records"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "period_start",
            "period_end",
            name="uq_engineering_performance_period"
        ),

        CheckConstraint(
            "attendance_score >= 0 "
            "AND attendance_score <= 100",
            name="check_engineering_attendance_score"
        ),

        CheckConstraint(
            "github_score >= 0 "
            "AND github_score <= 100",
            name="check_engineering_github_score"
        ),

        CheckConstraint(
            "daily_activity_score >= 0 "
            "AND daily_activity_score <= 100",
            name="check_engineering_activity_score"
        ),

        CheckConstraint(
            "task_score >= 0 "
            "AND task_score <= 100",
            name="check_engineering_task_score"
        ),

        CheckConstraint(
            "case_study_score >= 0 "
            "AND case_study_score <= 100",
            name="check_engineering_case_score"
        ),

        CheckConstraint(
            "mentor_feedback_score >= 0 "
            "AND mentor_feedback_score <= 100",
            name="check_engineering_feedback_score"
        ),

        CheckConstraint(
            "communication_score >= 0 "
            "AND communication_score <= 100",
            name="check_engineering_communication_score"
        ),

        CheckConstraint(
            "deadline_compliance_score >= 0 "
            "AND deadline_compliance_score <= 100",
            name="check_engineering_deadline_score"
        ),

        CheckConstraint(
            "learning_speed_score >= 0 "
            "AND learning_speed_score <= 100",
            name="check_engineering_learning_score"
        ),

        CheckConstraint(
            "engineering_credit_score >= 0 "
            "AND engineering_credit_score <= 100",
            name="check_engineering_credit_score"
        ),

        CheckConstraint(
            "final_engineering_score >= 0 "
            "AND final_engineering_score <= 100",
            name="check_final_engineering_score"
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

    generated_by_mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    generated_by_admin_id = Column(
        Integer,
        ForeignKey(
            "admins.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    period_start = Column(
        Date,
        nullable=False,
        index=True
    )

    period_end = Column(
        Date,
        nullable=False,
        index=True
    )

    attendance_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    github_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    daily_activity_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    task_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    case_study_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    mentor_feedback_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    communication_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    deadline_compliance_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    learning_speed_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    engineering_credit_score = Column(
        Float,
        nullable=False,
        default=0.0
    )

    final_engineering_score = Column(
        Float,
        nullable=False,
        default=0.0,
        index=True
    )

    performance_level = Column(
        Enum(
            "Excellent",
            "Good",
            "Average",
            "Weak",
            "Insufficient Data",
            name="engineering_performance_level_enum"
        ),
        nullable=False,
        default="Insufficient Data",
        index=True
    )

    placement_readiness = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    promotion_readiness = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    client_project_readiness = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    certificate_eligibility = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    data_completeness_percentage = Column(
        Float,
        nullable=False,
        default=0.0
    )

    strong_areas = Column(
        JSONB,
        nullable=False,
        default=list
    )

    weak_areas = Column(
        JSONB,
        nullable=False,
        default=list
    )

    recommendations = Column(
        JSONB,
        nullable=False,
        default=list
    )

    component_details = Column(
        JSONB,
        nullable=False,
        default=dict
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "engineering_performance_record_id",
            "recommendation_type",
            name="uq_student_performance_recommendation"
        ),

        CheckConstraint(
            "confidence_score >= 0 "
            "AND confidence_score <= 100",
            name="check_recommendation_confidence"
        ),

        CheckConstraint(
            "priority_score >= 0 "
            "AND priority_score <= 100",
            name="check_recommendation_priority"
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
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    engineering_performance_record_id = Column(
        Integer,
        ForeignKey(
            "engineering_performance_records.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    recommendation_type = Column(
        Enum(
            "Promote Intern",
            "Assign Advanced Case Study",
            "Assign Easier Case Study",
            "Schedule Mentor Meeting",
            "Recommend Interview",
            "Recommend Job Placement",
            "Recommend Internship Extension",
            "Recommend Certificate Eligibility",
            name="ai_recommendation_type_enum"
        ),
        nullable=False,
        index=True
    )

    category = Column(
        Enum(
            "Performance",
            "Learning",
            "Mentoring",
            "Placement",
            "Certification",
            name="ai_recommendation_category_enum"
        ),
        nullable=False,
        index=True
    )

    title = Column(
        String(250),
        nullable=False
    )

    recommendation_reason = Column(
        Text,
        nullable=False
    )

    recommended_action = Column(
        Text,
        nullable=False
    )

    confidence_score = Column(
        Float,
        nullable=False
    )

    priority_score = Column(
        Float,
        nullable=False
    )

    priority_level = Column(
        Enum(
            "Low",
            "Medium",
            "High",
            "Critical",
            name="ai_recommendation_priority_enum"
        ),
        nullable=False,
        default="Medium",
        index=True
    )

    status = Column(
        Enum(
            "Generated",
            "Pending Approval",
            "Approved",
            "Rejected",
            "Completed",
            name="ai_recommendation_status_enum"
        ),
        nullable=False,
        default="Generated",
        index=True
    )

    supporting_data = Column(
        JSONB,
        nullable=False,
        default=dict
    )

    weak_areas = Column(
        JSONB,
        nullable=False,
        default=list
    )

    strong_areas = Column(
        JSONB,
        nullable=False,
        default=list
    )

    requires_human_review = Column(
        Boolean,
        nullable=False,
        default=True
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    submitted_for_approval_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    reviewed_by_admin_id = Column(
        Integer,
        ForeignKey(
            "admins.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    review_notes = Column(
        Text,
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completion_notes = Column(
        Text,
        nullable=True
    )



class PerformanceReport(Base):
    __tablename__ = "performance_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    report_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    title = Column(
        String(250),
        nullable=False
    )

    period_start = Column(
        Date,
        nullable=False,
        index=True
    )

    period_end = Column(
        Date,
        nullable=False,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    mentor_id = Column(
        Integer,
        ForeignKey(
            "mentors.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    batch = Column(
        String(100),
        nullable=True,
        index=True
    )

    generated_by_role = Column(
        String(50),
        nullable=False
    )

    generated_by_user_id = Column(
        Integer,
        nullable=True
    )

    summary = Column(
        JSONB,
        nullable=False,
        default=dict
    )

    charts = Column(
        JSONB,
        nullable=False,
        default=list
    )

    insights = Column(
        JSONB,
        nullable=False,
        default=list
    )

    supporting_data = Column(
        JSONB,
        nullable=False,
        default=dict
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )