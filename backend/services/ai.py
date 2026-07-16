from sqlalchemy.orm import Session
from utils.groq import client
import json

from backend.models import (
    Attendance,
    Leave,
    Project,
    Student
)


def ai_chat(
    message: str,
    student: Student,
    db: Session
):

    #Attendance

    total_attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id
    ).count()

    present_days = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "Present"
    ).count()

    absent_days = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "Absent"
    ).count()

    #Projects

    total_projects = db.query(Project).filter(
        Project.student_id == student.id
    ).count()

    approved_projects = db.query(Project).filter(
        Project.student_id == student.id,
        Project.status == "Approved"
    ).count()

    pending_projects = db.query(Project).filter(
        Project.student_id == student.id,
        Project.status == "Pending"
    ).count()

    rejected_projects = db.query(Project).filter(
        Project.student_id == student.id,
        Project.status == "Rejected"
    ).count()

    #Leaves

    total_leaves = db.query(Leave).filter(
        Leave.student_id == student.id
    ).count()

    approved_leaves = db.query(Leave).filter(
        Leave.student_id == student.id,
        Leave.status == "Approved"
    ).count()

    pending_leaves = db.query(Leave).filter(
        Leave.student_id == student.id,
        Leave.status == "Pending"
    ).count()

    rejected_leaves = db.query(Leave).filter(
        Leave.student_id == student.id,
        Leave.status == "Rejected"
    ).count()

    system_prompt = f"""
You are the official AI Mentor of Ezitech Internship Portal.

Student Profile

Name: {student.name}

Attendance
- Total: {total_attendance}
- Present: {present_days}
- Absent: {absent_days}

Projects
- Total: {total_projects}
- Approved: {approved_projects}
- Pending: {pending_projects}
- Rejected: {rejected_projects}

Leaves
- Total: {total_leaves}
- Approved: {approved_leaves}
- Pending: {pending_leaves}
- Rejected: {rejected_leaves}

Instructions:

- Help students in programming.
- Help with Python, FastAPI, SQL, Git and software engineering.
- Give interview guidance.
- Keep answers concise and professional.
- DO NOT mention attendance, projects or leaves unless they are relevant.
- If the student asks about progress, performance, learning roadmap or career advice, personalize the answer using the profile above.
- Never answer topics unrelated to education or software engineering except greetings.
"""

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],

        temperature=0.5,
        max_tokens=1024

    )

    return {
        "response": completion.choices[0].message.content
    }


def ai_dashboard_summary(
    student: Student,
    db: Session
):

    #Attendance

    total_attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id
    ).count()

    present = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "Present"
    ).count()

    attendance_percentage = 0

    if total_attendance > 0:
        attendance_percentage = (present / total_attendance) * 100

    #Projects

    total_projects = db.query(Project).filter(
        Project.student_id == student.id
    ).count()

    approved_projects = db.query(Project).filter(
        Project.student_id == student.id,
        Project.status == "Approved"
    ).count()

    project_percentage = 0

    if total_projects > 0:
        project_percentage = (approved_projects / total_projects) * 100

    #Leaves

    rejected_leaves = db.query(Leave).filter(
        Leave.student_id == student.id,
        Leave.status == "Rejected"
    ).count()

    #Engineering Score

    attendance_score = attendance_percentage * 0.4
    project_score = project_percentage * 0.4
    leave_score = max(0, 20 - (rejected_leaves * 5))

    engineering_score = round(
        attendance_score +
        project_score +
        leave_score
    )

    prompt = f"""
You are an AI Software Engineering Mentor.

Student Engineering Score:
{engineering_score}/100

Attendance:
{attendance_percentage:.1f}%

Approved Projects:
{approved_projects}/{total_projects}

Rejected Leaves:
{rejected_leaves}

Return ONLY valid JSON.

Example:

{{
    "skill_growth":"Excellent",

    "weak_areas":[
        "Docker",
        "Testing"
    ],

    "recommendations":[
        "Complete pending projects",
        "Learn Docker",
        "Practice SQL"
    ],

    "next_case_study":"Build JWT Authentication API using FastAPI"
}}
"""

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],

        temperature=0.3,

        response_format={
            "type": "json_object"
        }

    )

    result = json.loads(
        completion.choices[0].message.content
    )

    return {

        "engineering_score": engineering_score,

        "skill_growth": result["skill_growth"],

        "weak_areas": result["weak_areas"],

        "recommendations": result["recommendations"],

        "next_case_study": result["next_case_study"]

    }