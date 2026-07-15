from sqlalchemy.orm import Session
from datetime import datetime
from backend.schemas import (
    ProjectSubmission,
    ProjectReview
)
from backend.models import Project, Student, Mentor
def submit_project(
    student_id: int,
    project: ProjectSubmission,
    db: Session
):

    new_project = Project(
        student_id=student_id,
        title=project.title,
        description=project.description,
        github_link=project.github_link,
        tech_stack=project.tech_stack
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project submitted successfully."
    }

def project_history(
    student_id: int,
    db: Session
):

    projects = db.query(Project).filter(
        Project.student_id == student_id
    ).order_by(
        Project.submitted_at.desc()
    ).all()

    return projects

def pending_projects(
    db: Session
):

    projects = (
        db.query(
            Project,
            Student.name,
            Student.email,
            Student.batch
        )
        .join(
            Student,
            Project.student_id == Student.id
        )
        .filter(
            Project.status == "Pending"
        )
        .order_by(
            Project.submitted_at.desc()
        )
        .all()
    )

    result = []

    for project, name, email, batch in projects:

        result.append({
            "project_id": project.id,
            "student_name": name,
            "student_email": email,
            "batch": batch,
            "title": project.title,
            "description": project.description,
            "github_link": project.github_link,
            "tech_stack": project.tech_stack,
            "submitted_at": project.submitted_at,
            "status": project.status
        })

    return result

def approve_project(
    project_id: int,
    mentor_id: int,
    db: Session
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        return {
            "message": "Project not found."
        }

    if project.status != "Pending":
        return {
            "message": "Project already reviewed."
        }

    project.status = "Approved"
    project.mentor_id = mentor_id
    project.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "message": "Project approved successfully."
    }

def reject_project(
    project_id: int,
    mentor_id: int,
    review: ProjectReview,
    db: Session
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        return {
            "message": "Project not found."
        }

    if project.status != "Pending":
        return {
            "message": "Project already reviewed."
        }

    project.status = "Rejected"
    project.mentor_id = mentor_id
    project.mentor_remarks = review.remarks
    project.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "message": "Project rejected successfully."
    }

def approve_project(
    project_id: int,
    mentor_id: int,
    review: ProjectReview,
    db: Session
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        return {
            "message": "Project not found."
        }

    if project.status != "Pending":
        return {
            "message": "Project already reviewed."
        }

    project.status = "Approved"
    project.mentor_id = mentor_id
    project.mentor_remarks = review.remarks
    project.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return {
        "message": "Project approved successfully."
    }

def my_project_result(
    student_id: int,
    db: Session
):

    projects = db.query(Project).filter(
        Project.student_id == student_id
    ).order_by(
        Project.submitted_at.desc()
    ).all()

    result = []

    for project in projects:

        result.append({
            "project_id": project.id,
            "title": project.title,
            "github_link": project.github_link,
            "tech_stack": project.tech_stack,
            "status": project.status,
            "mentor_remarks": project.mentor_remarks,
            "submitted_at": project.submitted_at,
            "reviewed_at": project.reviewed_at
        })

    return result


def resubmit_project(
    project_id: int,
    student_id: int,
    project: ProjectSubmission,
    db: Session
):

    existing_project = db.query(Project).filter(
        Project.id == project_id,
        Project.student_id == student_id
    ).first()

    if existing_project is None:
        return {
            "message": "Project not found."
        }

    if existing_project.status != "Rejected":
        return {
            "message": "Only rejected projects can be resubmitted."
        }

    existing_project.title = project.title
    existing_project.description = project.description
    existing_project.github_link = project.github_link
    existing_project.tech_stack = project.tech_stack

    existing_project.status = "Pending"
    existing_project.mentor_remarks = None
    existing_project.mentor_id = None
    existing_project.reviewed_at = None
    existing_project.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(existing_project)

    return {
        "message": "Project resubmitted successfully."
    }

def admin_all_projects(
    db: Session
):

    projects = (
        db.query(
            Project,
            Student.name,
            Student.email
        )
        .join(
            Student,
            Project.student_id == Student.id
        )
        .order_by(
            Project.submitted_at.desc()
        )
        .all()
    )

    result = []

    for project, student_name, student_email in projects:

        mentor_name = None

        if project.mentor_id is not None:

            mentor = db.query(Mentor).filter(
                Mentor.id == project.mentor_id
            ).first()

            if mentor:
                mentor_name = mentor.name

        result.append({
            "project_id": project.id,
            "student_name": student_name,
            "student_email": student_email,
            "title": project.title,
            "github_link": project.github_link,
            "tech_stack": project.tech_stack,
            "status": project.status,
            "mentor_name": mentor_name,
            "mentor_remarks": project.mentor_remarks,
            "submitted_at": project.submitted_at,
            "reviewed_at": project.reviewed_at
        })

    return result