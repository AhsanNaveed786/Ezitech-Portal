from sqlalchemy.orm import Session
from utils.groq import client
from datetime import date, timedelta
import json

import json
import re

from collections import defaultdict
from sqlalchemy.orm import Session

from backend.models import Project
from utils.groq import client


from collections import defaultdict
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session

from backend.models import Student, Attendance, Project
from utils.groq import client


from backend.models import (
    Attendance,
    Leave,
    Mentor,
    Project,
    Student
)
from fastapi import HTTPException


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

    "score_breakdown": {

        "attendance": round(attendance_score),

        "projects": round(project_score),

        "discipline": round(leave_score)
    },
    "skill_growth": result["skill_growth"],
    "weak_areas": result["weak_areas"],
    "recommendations": result["recommendations"],
    "next_case_study": result["next_case_study"]
    }


def ai_learning_roadmap(
    student: Student,
    db: Session
):

    total_attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id
    ).count()

    present_days = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.status == "Present"
    ).count()

    attendance_percentage = 0

    if total_attendance > 0:
        attendance_percentage = (
            present_days / total_attendance
        ) * 100

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

    rejected_leaves = db.query(Leave).filter(
        Leave.student_id == student.id,
        Leave.status == "Rejected"
    ).count()

    attendance_score = attendance_percentage * 0.4

    project_percentage = 0

    if total_projects > 0:
        project_percentage = (
            approved_projects / total_projects
        ) * 100

    project_score = project_percentage * 0.4

    discipline_score = max(
        0,
        20 - (rejected_leaves * 5)
    )

    engineering_score = round(
        attendance_score
        + project_score
        + discipline_score
    )

    prompt = f"""
You are a senior software engineering career mentor.

Create a personalized learning roadmap for the student below.

Student Profile:

Name: {student.name}
Batch: {student.batch}
Engineering Score: {engineering_score}/100
Attendance: {attendance_percentage:.1f}%
Total Projects: {total_projects}
Approved Projects: {approved_projects}
Pending Projects: {pending_projects}
Rejected Projects: {rejected_projects}

Instructions:

- Determine the student's current level from the available data.
- Create a practical roadmap of 6 to 10 weeks.
- Do not limit the roadmap to Python, FastAPI, or SQL.
- Recommend technologies from different software engineering areas.
- Include backend, frontend, databases, AI, cloud, DevOps, security, testing, system design, or mobile development where relevant.
- Do not recommend every technology at once.
- Select technologies that form a logical learning sequence.
- Each week must contain one main topic and one practical goal.
- Focus on hands-on projects rather than only theory.
- The roadmap should help the student become a complete software engineer.
- Avoid repeating the same technology in multiple weeks.
- Make recommendations according to the student's current level.
- Return only valid JSON.
- Do not include markdown code blocks.
- Do not include text outside the JSON object.

Technologies may include, but are not limited to:

Programming:
Python, Java, JavaScript, TypeScript, C++, Go, Rust, C#

Backend:
FastAPI, Django, Flask, Node.js, Express.js, NestJS, Spring Boot, ASP.NET Core

Frontend:
HTML, CSS, Tailwind CSS, Bootstrap, React, Next.js, Vue.js, Angular

Mobile:
React Native, Flutter, Android development

Databases:
PostgreSQL, MySQL, SQLite, MongoDB, Redis, Elasticsearch

Artificial Intelligence:
NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch, NLP, Computer Vision, LangChain, RAG, Vector Databases, Prompt Engineering, AI Agents, MCP, n8n

Cloud and DevOps:
Docker, Kubernetes, Linux, GitHub Actions, CI/CD, Nginx, AWS, Azure, Google Cloud, Terraform

Software Engineering:
Data Structures, Algorithms, OOP, SOLID Principles, Design Patterns, Clean Architecture, REST APIs, GraphQL, Microservices, System Design

Testing and Security:
Unit Testing, Integration Testing, Pytest, API Testing, JWT, OAuth2, OWASP Top 10, Secure Coding

Required JSON format:

{{
    "current_level": "Beginner, Intermediate, or Advanced",
    "estimated_completion": "Number of weeks",
    "roadmap": [
        {{
            "week": 1,
            "topic": "Technology or concept",
            "goal": "Practical learning goal"
        }}
    ]
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

        temperature=0.4,

        response_format={
            "type": "json_object"
        }
    )

    content = completion.choices[0].message.content

    result = json.loads(content)

    return {
        "current_level": result["current_level"],
        "estimated_completion": result["estimated_completion"],
        "roadmap": result["roadmap"]
    }

def calculate_student_engineering_score(
    student: Student,
    db: Session
):
    total_attendance = (
        db.query(Attendance)
        .filter(Attendance.student_id == student.id)
        .count()
    )

    present_days = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.status == "Present"
        )
        .count()
    )

    attendance_percentage = 0.0

    if total_attendance > 0:
        attendance_percentage = (
            present_days / total_attendance
        ) * 100

    total_projects = (
        db.query(Project)
        .filter(Project.student_id == student.id)
        .count()
    )

    approved_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.status == "Approved"
        )
        .count()
    )

    pending_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.status == "Pending"
        )
        .count()
    )

    rejected_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.status == "Rejected"
        )
        .count()
    )

    rejected_leaves = (
        db.query(Leave)
        .filter(
            Leave.student_id == student.id,
            Leave.status == "Rejected"
        )
        .count()
    )

    attendance_score = attendance_percentage * 0.4

    project_completion_percentage = 0.0

    if total_projects > 0:
        project_completion_percentage = (
            approved_projects / total_projects
        ) * 100

    project_score = project_completion_percentage * 0.4

    discipline_score = max(
        0,
        20 - (rejected_leaves * 5)
    )

    engineering_score = round(
        attendance_score
        + project_score
        + discipline_score
    )

    engineering_score = max(
        0,
        min(100, engineering_score)
    )

    if engineering_score >= 80:
        performance_level = "Excellent"

    elif engineering_score >= 65:
        performance_level = "Good"

    elif engineering_score >= 50:
        performance_level = "Average"

    else:
        performance_level = "Needs Improvement"

    return {
        "student_id": student.id,
        "student_name": student.name,
        "engineering_score": engineering_score,

        "attendance_score": round(attendance_score),
        "project_score": round(project_score),
        "discipline_score": round(discipline_score),

        "attendance_percentage": round(
            attendance_percentage,
            2
        ),

        "project_completion_percentage": round(
            project_completion_percentage,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,
        "rejected_leaves": rejected_leaves,
        "performance_level": performance_level
    }

def get_mentor_students(
    mentor: Mentor,
    db: Session
):
    students = (
        db.query(Student)
        .filter(Student.mentor_id == mentor.id)
        .all()
    )

    return students

def get_mentor_top_performers(
    mentor: Mentor,
    db: Session,
    limit: int = 5
):
    students = get_mentor_students(
        mentor=mentor,
        db=db
    )

    performances = [
        calculate_student_engineering_score(
            student=student,
            db=db
        )
        for student in students
    ]

    performances.sort(
        key=lambda item: item["engineering_score"],
        reverse=True
    )

    return performances[:limit]

def get_mentor_weak_performers(
    mentor: Mentor,
    db: Session,
    limit: int = 5
):
    students = get_mentor_students(
        mentor=mentor,
        db=db
    )

    performances = [
        calculate_student_engineering_score(
            student=student,
            db=db
        )
        for student in students
    ]

    performances.sort(
        key=lambda item: item["engineering_score"]
    )

    weak_students = [
        student
        for student in performances
        if student["engineering_score"] < 60
    ]

    return weak_students[:limit]

def get_mentor_team_analytics(
    mentor: Mentor,
    db: Session
):
    students = get_mentor_students(
        mentor=mentor,
        db=db
    )

    total_students = len(students)

    if total_students == 0:
        return {
            "total_students": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "students_requiring_attention": 0
        }

    performances = [
        calculate_student_engineering_score(
            student=student,
            db=db
        )
        for student in students
    ]

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_students

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_students

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    students_requiring_attention = sum(
        1
        for item in performances
        if item["engineering_score"] < 60
    )

    return {
        "total_students": total_students,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "students_requiring_attention":
            students_requiring_attention
    }


def get_student_engineering_growth(
    mentor: Mentor,
    student_id: int,
    db: Session
):
    student = (
        db.query(Student)
        .filter(
            Student.id == student_id,
            Student.mentor_id == mentor.id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found or not assigned to this mentor"
        )

    performance = calculate_student_engineering_score(
        student=student,
        db=db
    )

    score = performance["engineering_score"]

    if score >= 80:
        current_level = "Advanced"
        growth_status = "Strong growth"

    elif score >= 60:
        current_level = "Intermediate"
        growth_status = "Steady growth"

    elif score >= 40:
        current_level = "Developing"
        growth_status = "Slow growth"

    else:
        current_level = "Beginner"
        growth_status = "Requires immediate attention"

    return {
        "student_id": student.id,
        "student_name": student.name,
        "engineering_score": score,

        "attendance_score":
            performance["attendance_score"],

        "project_score":
            performance["project_score"],

        "discipline_score":
            performance["discipline_score"],

        "attendance_percentage":
            performance["attendance_percentage"],

        "project_completion_percentage":
            performance["project_completion_percentage"],

        "current_level": current_level,
        "growth_status": growth_status
    }


def get_mentor_ai_recommendations(
    mentor: Mentor,
    db: Session
):
    students = get_mentor_students(
        mentor=mentor,
        db=db
    )

    if not students:
        return []

    student_performance_data = [
        calculate_student_engineering_score(
            student=student,
            db=db
        )
        for student in students
    ]

    compact_data = [
        {
            "student_id": item["student_id"],
            "student_name": item["student_name"],
            "engineering_score":
                item["engineering_score"],
            "attendance_percentage":
                item["attendance_percentage"],
            "approved_projects":
                item["approved_projects"],
            "pending_projects":
                item["pending_projects"],
            "rejected_projects":
                item["rejected_projects"],
            "performance_level":
                item["performance_level"]
        }
        for item in student_performance_data
    ]

    prompt = f"""
You are an experienced software engineering mentor.

Analyze the following students and provide one practical
recommendation for each student.

Student performance data:

{json.dumps(compact_data, indent=2)}

Instructions:

- Provide one recommendation for every student.
- Recommendations must be specific and practical.
- Do not limit recommendations to Python, FastAPI or SQL.
- Recommend learning activities from frontend, backend,
  AI, cloud, DevOps, databases, testing, security,
  communication, Git, system design or problem solving.
- Students with low attendance should receive an
  attendance or consistency recommendation.
- Students with rejected projects should receive a
  technical improvement recommendation.
- Strong students should receive advanced challenges.
- Priority must be High, Medium or Low.
- Return valid JSON only.
- Do not include markdown.
- Do not include additional explanation.

Required JSON format:

{{
    "recommendations": [
        {{
            "student_id": 1,
            "student_name": "Student name",
            "recommendation": "Practical recommendation",
            "priority": "High"
        }}
    ]
}}
"""

    try:
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

        content = completion.choices[0].message.content

        result = json.loads(content)

        return result.get(
            "recommendations",
            []
        )

    except Exception:
        return generate_fallback_recommendations(
            student_performance_data
        )
    
def generate_fallback_recommendations(
    performances: list
):
    recommendations = []

    for item in performances:
        score = item["engineering_score"]
        attendance = item["attendance_percentage"]
        rejected_projects = item["rejected_projects"]

        if attendance < 70:
            recommendation = (
                "Improve attendance consistency and create "
                "a weekly learning schedule."
            )
            priority = "High"

        elif rejected_projects > 0:
            recommendation = (
                "Review rejected project feedback, improve "
                "testing and resubmit the project."
            )
            priority = "High"

        elif score < 60:
            recommendation = (
                "Strengthen programming fundamentals and "
                "complete a small practical project."
            )
            priority = "Medium"

        elif score < 80:
            recommendation = (
                "Work on a full-stack project using a new "
                "frontend, backend or database technology."
            )
            priority = "Medium"

        else:
            recommendation = (
                "Build an advanced project involving system "
                "design, cloud deployment or AI integration."
            )
            priority = "Low"

        recommendations.append({
            "student_id": item["student_id"],
            "student_name": item["student_name"],
            "recommendation": recommendation,
            "priority": priority
        })

    return recommendations

def get_complete_mentor_ai_dashboard(
    mentor: Mentor,
    db: Session
):
    team_analytics = get_mentor_team_analytics(
        mentor=mentor,
        db=db
    )

    top_performers = get_mentor_top_performers(
        mentor=mentor,
        db=db
    )

    weak_performers = get_mentor_weak_performers(
        mentor=mentor,
        db=db
    )

    ai_recommendations = get_mentor_ai_recommendations(
        mentor=mentor,
        db=db
    )

    return {
        "team_analytics": team_analytics,
        "top_performers": top_performers,
        "weak_performers": weak_performers,
        "ai_recommendations": ai_recommendations
    }

def calculate_admin_intern_readiness(
    student: Student,
    db: Session
):
    total_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id
        )
        .count()
    )

    present_days = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.status == "Present"
        )
        .count()
    )

    attendance_percentage = 0.0

    if total_attendance > 0:
        attendance_percentage = (
            present_days / total_attendance
        ) * 100

    total_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id
        )
        .count()
    )

    approved_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.status == "Approved"
        )
        .count()
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    project_score = (
        project_approval_percentage * 0.60
    )

    attendance_score = (
        attendance_percentage * 0.40
    )

    readiness_score = (
        project_score + attendance_score
    )

    return {
        "student_id": student.id,
        "student_name": student.name,

        "attendance_percentage": round(
            attendance_percentage,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "readiness_score": round(
            readiness_score,
            2
        )
    }


def get_admin_top_interns(
    db: Session,
    limit: int = 10
):
    students = db.query(Student).all()

    intern_performance = []

    for student in students:
        performance = calculate_admin_intern_readiness(
            student=student,
            db=db
        )

        if (
            performance["total_projects"] == 0
            and performance["attendance_percentage"] == 0
        ):
            continue

        intern_performance.append(performance)

    intern_performance.sort(
        key=lambda item: (
            item["readiness_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    top_interns = intern_performance[:limit]

    ranked_interns = []

    for index, intern in enumerate(
        top_interns,
        start=1
    ):
        ranked_interns.append({
            "rank": index,
            "student_id": intern["student_id"],
            "student_name": intern["student_name"],
            "attendance_percentage": intern["attendance_percentage"],
            "total_projects": intern["total_projects"],
            "approved_projects": intern["approved_projects"],
            "project_approval_percentage": intern[
                "project_approval_percentage"
            ],
            "readiness_score": intern["readiness_score"]
        })

    return {
        "top_interns": ranked_interns
    }


def get_admin_ai_recommendations(
    db: Session,
    limit: int = 10
):
    top_intern_data = get_admin_top_interns(
        db=db,
        limit=limit
    )

    top_interns = top_intern_data["top_interns"]

    if not top_interns:
        return {
            "interns": []
        }

    prompt = f"""
You are an AI decision-support assistant for an internship management platform.

Analyze the top-performing interns below and recommend suitable administrative actions.

Intern data:

{json.dumps(top_interns, indent=2)}

Allowed recommendation types:

- Promote Intern
- Assign Advanced Case Study
- Assign Easier Case Study
- Schedule Mentor Meeting
- Recommend Interview
- Recommend Job Placement
- Recommend Internship Extension
- Recommend Certificate Eligibility

Rules:

- Give recommendations according to attendance, approved projects,
  project approval percentage and readiness score.
- Strong interns may receive more than one recommendation.
- Do not recommend easier case studies to strong interns.
- Do not recommend job placement unless performance is consistently strong.
- Internship extension should only be recommended for interns who need more time.
- Certificate eligibility should only be recommended when attendance and
  project performance are satisfactory.
- Priority must be High, Medium or Low.
- Give a clear and short reason for every recommendation.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "interns": [
        {{
            "student_id": 1,
            "student_name": "Student Name",
            "readiness_score": 90,
            "attendance_percentage": 95,
            "approved_projects": 6,
            "recommendations": [
                {{
                    "type": "Recommend Interview",
                    "reason": "Strong attendance and project performance.",
                    "priority": "High"
                }}
            ]
        }}
    ]
}}
"""

    try:
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

        content = completion.choices[0].message.content

        result = json.loads(content)

        return result

    except Exception:
        return generate_admin_fallback_recommendations(
            top_interns
        )
    

def generate_admin_fallback_recommendations(
    top_interns: list
):
    interns = []

    for intern in top_interns:
        readiness_score = intern["readiness_score"]
        attendance = intern["attendance_percentage"]
        approved_projects = intern["approved_projects"]

        recommendations = []

        if (
            readiness_score >= 85
            and attendance >= 85
            and approved_projects >= 3
        ):
            recommendations.append({
                "type": "Promote Intern",
                "reason": (
                    "The intern has strong attendance and "
                    "consistent approved project performance."
                ),
                "priority": "High"
            })

            recommendations.append({
                "type": "Recommend Interview",
                "reason": (
                    "The intern appears ready for a formal "
                    "technical evaluation."
                ),
                "priority": "High"
            })

            recommendations.append({
                "type": "Recommend Certificate Eligibility",
                "reason": (
                    "The intern has satisfactory attendance "
                    "and project completion."
                ),
                "priority": "High"
            })

        elif (
            readiness_score >= 70
            and attendance >= 75
        ):
            recommendations.append({
                "type": "Assign Advanced Case Study",
                "reason": (
                    "The intern is performing well and is ready "
                    "for a more challenging assignment."
                ),
                "priority": "Medium"
            })

            recommendations.append({
                "type": "Recommend Certificate Eligibility",
                "reason": (
                    "Current attendance and project performance "
                    "meet the expected standard."
                ),
                "priority": "Medium"
            })

        elif readiness_score >= 50:
            recommendations.append({
                "type": "Assign Easier Case Study",
                "reason": (
                    "The intern needs a more manageable task "
                    "to improve practical understanding."
                ),
                "priority": "Medium"
            })

            recommendations.append({
                "type": "Schedule Mentor Meeting",
                "reason": (
                    "A mentor discussion can help address "
                    "performance gaps."
                ),
                "priority": "High"
            })

        else:
            recommendations.append({
                "type": "Schedule Mentor Meeting",
                "reason": (
                    "The intern requires direct guidance due "
                    "to weak overall performance."
                ),
                "priority": "High"
            })

            recommendations.append({
                "type": "Recommend Internship Extension",
                "reason": (
                    "The intern may need additional time to meet "
                    "attendance and project requirements."
                ),
                "priority": "High"
            })

        if (
            readiness_score >= 92
            and attendance >= 90
            and approved_projects >= 5
        ):
            recommendations.append({
                "type": "Recommend Job Placement",
                "reason": (
                    "The intern demonstrates exceptional readiness "
                    "for an entry-level professional role."
                ),
                "priority": "High"
            })

        interns.append({
            "student_id": intern["student_id"],
            "student_name": intern["student_name"],
            "readiness_score": readiness_score,
            "attendance_percentage": attendance,
            "approved_projects": approved_projects,
            "recommendations": recommendations
        })

    return {
        "interns": interns
    }


def calculate_weekly_student_performance(
    student: Student,
    db: Session,
    start_date: date,
    end_date: date
):
    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        )
        .all()
    )

    total_attendance = len(attendance_records)

    present_days = sum(
        1
        for record in attendance_records
        if record.status == "Present"
    )

    attendance_percentage = 0.0

    if total_attendance > 0:
        attendance_percentage = (
            present_days / total_attendance
        ) * 100

    weekly_projects = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.submitted_at >= start_date,
            Project.submitted_at < end_date + timedelta(days=1)
        )
        .all()
    )

    total_projects = len(weekly_projects)

    approved_projects = sum(
        1
        for project in weekly_projects
        if project.status == "Approved"
    )

    pending_projects = sum(
        1
        for project in weekly_projects
        if project.status == "Pending"
    )

    rejected_projects = sum(
        1
        for project in weekly_projects
        if project.status == "Rejected"
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    attendance_score = attendance_percentage * 0.40
    project_score = project_approval_percentage * 0.60

    engineering_score = round(
        attendance_score + project_score,
        2
    )

    return {
        "student_id": student.id,
        "student_name": student.name,
        "engineering_score": engineering_score,
        "attendance_percentage": round(
            attendance_percentage,
            2
        ),
        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects
    }

def get_weekly_engineering_report(
    db: Session
):
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    students = db.query(Student).all()

    performances = []

    for student in students:
        performance = calculate_weekly_student_performance(
            student=student,
            db=db,
            start_date=start_date,
            end_date=end_date
        )

        performances.append(performance)

    total_interns = len(performances)

    if total_interns == 0:
        return {
            "period_start": str(start_date),
            "period_end": str(end_date),
            "total_interns": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects_submitted": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "top_performers": [],
            "interns_requiring_attention": [],
            "productivity_level": "No Data",
            "ai_summary": "No intern performance data is available.",
            "recommendations": [
                "Add intern attendance and project records."
            ]
        }

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_interns

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_interns

    total_projects_submitted = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    sorted_performances = sorted(
        performances,
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    top_performers = sorted_performances[:5]

    interns_requiring_attention = [
        item
        for item in sorted_performances
        if (
            item["engineering_score"] < 50
            or item["attendance_percentage"] < 70
        )
    ]

    interns_requiring_attention.sort(
        key=lambda item: item["engineering_score"]
    )

    interns_requiring_attention = (
        interns_requiring_attention[:5]
    )

    if average_engineering_score >= 80:
        productivity_level = "Excellent"

    elif average_engineering_score >= 65:
        productivity_level = "Good"

    elif average_engineering_score >= 50:
        productivity_level = "Average"

    else:
        productivity_level = "Needs Improvement"

    report_data = {
        "period_start": str(start_date),
        "period_end": str(end_date),
        "total_interns": total_interns,
        "average_engineering_score": round(
            average_engineering_score,
            2
        ),
        "average_attendance": round(
            average_attendance,
            2
        ),
        "total_projects_submitted":
            total_projects_submitted,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,
        "productivity_level": productivity_level
    }

    ai_result = generate_weekly_report_ai_summary(
        report_data=report_data
    )

    return {
        **report_data,

        "top_performers": [
            {
                "student_id": item["student_id"],
                "student_name": item["student_name"],
                "engineering_score":
                    item["engineering_score"],
                "attendance_percentage":
                    item["attendance_percentage"],
                "approved_projects":
                    item["approved_projects"]
            }
            for item in top_performers
        ],

        "interns_requiring_attention": [
            {
                "student_id": item["student_id"],
                "student_name": item["student_name"],
                "engineering_score":
                    item["engineering_score"],
                "attendance_percentage":
                    item["attendance_percentage"],
                "approved_projects":
                    item["approved_projects"]
            }
            for item in interns_requiring_attention
        ],

        "ai_summary": ai_result["ai_summary"],
        "recommendations": ai_result["recommendations"]
    }


def generate_weekly_report_ai_summary(
    report_data: dict
):
    prompt = f"""
You are an AI engineering performance analyst.

Analyze the following weekly internship performance report:

{json.dumps(report_data, indent=2)}

Your task:

- Write a short and professional weekly summary.
- Identify whether team productivity is improving or weak.
- Provide three practical recommendations.
- Recommendations may cover attendance, project quality,
  mentoring, technical training, communication, testing,
  Git practices, frontend, backend, AI, cloud or DevOps.
- Keep the summary concise.
- Return valid JSON only.
- Do not return markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short weekly performance summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        content = completion.choices[0].message.content

        result = json.loads(content)

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Weekly report generated successfully."
            ),
            "recommendations": result.get(
                "recommendations",
                []
            )
        }

    except Exception:
        return generate_weekly_report_fallback(
            report_data=report_data
        )
    

def generate_weekly_report_fallback(
    report_data: dict
):
    score = report_data[
        "average_engineering_score"
    ]

    attendance = report_data[
        "average_attendance"
    ]

    rejected_projects = report_data[
        "rejected_projects"
    ]

    if score >= 80:
        summary = (
            "The team delivered strong engineering "
            "performance during the last seven days."
        )

    elif score >= 60:
        summary = (
            "The team showed satisfactory weekly progress, "
            "but some performance areas still need attention."
        )

    else:
        summary = (
            "The weekly performance indicates that the team "
            "requires additional technical and mentor support."
        )

    recommendations = []

    if attendance < 75:
        recommendations.append(
            "Improve attendance consistency and follow up "
            "with frequently absent interns."
        )

    if rejected_projects > 0:
        recommendations.append(
            "Review rejected projects with mentors and focus "
            "on code quality, testing and documentation."
        )

    if score < 70:
        recommendations.append(
            "Schedule targeted technical workshops and assign "
            "manageable practical case studies."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Encourage interns to maintain weekly progress "
            "logs and clear learning goals."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Recognize top performers and assign them more "
            "advanced engineering challenges."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }


def calculate_period_performance(
    db: Session,
    start_date: date,
    end_date: date
):
    students = db.query(Student).all()

    total_students = len(students)

    start_datetime = datetime.combine(
        start_date,
        time.min
    )

    end_datetime = datetime.combine(
        end_date + timedelta(days=1),
        time.min
    )

    student_scores = []
    student_attendance = []

    for student in students:
        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
            .all()
        )

        total_attendance = len(attendance_records)

        present_days = sum(
            1
            for record in attendance_records
            if record.status == "Present"
        )

        attendance_percentage = 0.0

        if total_attendance > 0:
            attendance_percentage = (
                present_days / total_attendance
            ) * 100

        projects = (
            db.query(Project)
            .filter(
                Project.student_id == student.id,
                Project.submitted_at >= start_datetime,
                Project.submitted_at < end_datetime
            )
            .all()
        )

        total_projects = len(projects)

        approved_projects = sum(
            1
            for project in projects
            if project.status == "Approved"
        )

        approval_percentage = 0.0

        if total_projects > 0:
            approval_percentage = (
                approved_projects / total_projects
            ) * 100

        attendance_score = (
            attendance_percentage * 0.40
        )

        project_score = (
            approval_percentage * 0.60
        )

        engineering_score = (
            attendance_score + project_score
        )

        student_scores.append(engineering_score)
        student_attendance.append(
            attendance_percentage
        )

    average_engineering_score = 0.0
    average_attendance = 0.0

    if total_students > 0:
        average_engineering_score = (
            sum(student_scores) / total_students
        )

        average_attendance = (
            sum(student_attendance) / total_students
        )

    period_projects = (
        db.query(Project)
        .filter(
            Project.submitted_at >= start_datetime,
            Project.submitted_at < end_datetime
        )
        .all()
    )

    approved_projects = sum(
        1
        for project in period_projects
        if project.status == "Approved"
    )

    pending_projects = sum(
        1
        for project in period_projects
        if project.status == "Pending"
    )

    rejected_projects = sum(
        1
        for project in period_projects
        if project.status == "Rejected"
    )

    return {
        "period_start": str(start_date),
        "period_end": str(end_date),

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": len(period_projects),
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects
    }


def get_monthly_growth_report(
    db: Session
):
    current_end = date.today()
    current_start = (
        current_end - timedelta(days=29)
    )

    previous_end = (
        current_start - timedelta(days=1)
    )

    previous_start = (
        previous_end - timedelta(days=29)
    )

    current_period = calculate_period_performance(
        db=db,
        start_date=current_start,
        end_date=current_end
    )

    previous_period = calculate_period_performance(
        db=db,
        start_date=previous_start,
        end_date=previous_end
    )

    engineering_score_growth = round(
        current_period["average_engineering_score"]
        - previous_period["average_engineering_score"],
        2
    )

    attendance_growth = round(
        current_period["average_attendance"]
        - previous_period["average_attendance"],
        2
    )

    project_growth = (
        current_period["total_projects"]
        - previous_period["total_projects"]
    )

    approved_project_growth = (
        current_period["approved_projects"]
        - previous_period["approved_projects"]
    )

    if (
        engineering_score_growth >= 10
        and attendance_growth >= 5
    ):
        growth_status = "Excellent Growth"

    elif engineering_score_growth > 0:
        growth_status = "Improving"

    elif (
        engineering_score_growth == 0
        and attendance_growth == 0
    ):
        growth_status = "Stable"

    elif engineering_score_growth >= -5:
        growth_status = "Slight Decline"

    else:
        growth_status = "Needs Attention"

    growth_data = {
        "previous_period": previous_period,
        "current_period": current_period,

        "engineering_score_growth":
            engineering_score_growth,

        "attendance_growth":
            attendance_growth,

        "project_growth":
            project_growth,

        "approved_project_growth":
            approved_project_growth,

        "growth_status":
            growth_status
    }

    ai_result = generate_monthly_growth_ai_summary(
        growth_data=growth_data
    )

    return {
        **growth_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }


def generate_monthly_growth_ai_summary(
    growth_data: dict
):
    prompt = f"""
You are an AI performance analyst for an internship platform.

Compare the previous 30-day period with the current 30-day period.

Performance data:

{json.dumps(growth_data, indent=2)}

Instructions:

- Explain whether engineering performance improved or declined.
- Mention attendance and project submission changes.
- Provide exactly three practical recommendations.
- Keep the summary short and professional.
- Return valid JSON only.
- Do not include markdown or additional text.

Required JSON format:

{{
    "ai_summary": "Monthly growth summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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
            "ai_summary": result.get(
                "ai_summary",
                "Monthly growth report generated."
            ),
            "recommendations": result.get(
                "recommendations",
                []
            )[:3]
        }

    except Exception:
        return generate_monthly_growth_fallback(
            growth_data
        )
    
def generate_monthly_growth_fallback(
    growth_data: dict
):
    score_growth = growth_data[
        "engineering_score_growth"
    ]

    attendance_growth = growth_data[
        "attendance_growth"
    ]

    approved_growth = growth_data[
        "approved_project_growth"
    ]

    if score_growth > 0:
        summary = (
            "The team showed positive engineering growth "
            "compared with the previous 30-day period."
        )

    elif score_growth == 0:
        summary = (
            "The team's engineering performance remained "
            "stable during the current period."
        )

    else:
        summary = (
            "The team's engineering performance declined "
            "compared with the previous period."
        )

    recommendations = []

    if attendance_growth < 0:
        recommendations.append(
            "Review attendance decline and follow up with "
            "interns showing inconsistent participation."
        )

    if approved_growth < 0:
        recommendations.append(
            "Arrange project review sessions to improve "
            "submission quality and approval rates."
        )

    if score_growth <= 0:
        recommendations.append(
            "Assign focused technical case studies and "
            "schedule additional mentor support."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Set measurable monthly engineering goals for "
            "every intern."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Recognize improving interns and give advanced "
            "tasks to strong performers."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Track weekly progress to identify problems "
            "before the end of the month."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }



def get_single_mentor_summary(
    mentor: Mentor,
    db: Session
):
    students = (
        db.query(Student)
        .filter(
            Student.mentor_id == mentor.id
        )
        .all()
    )

    if not students:
        return {
            "mentor_id": mentor.id,
            "mentor_name": mentor.name,
            "department": mentor.department,
            "total_assigned_students": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "students_requiring_attention": 0,
            "top_performer": None,
            "weak_performer": None,
            "performance_status": "No Students Assigned",
            "ai_summary": (
                "No students are currently assigned "
                "to this mentor."
            ),
            "recommendations": [
                "Assign interns to this mentor before generating performance analysis."
            ]
        }

    performances = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

    total_students = len(performances)

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_students

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_students

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    students_requiring_attention = sum(
        1
        for item in performances
        if (
            item["engineering_score"] < 60
            or item["attendance_percentage"] < 70
        )
    )

    sorted_performances = sorted(
        performances,
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    top_student = sorted_performances[0]

    weak_student = min(
        performances,
        key=lambda item: (
            item["engineering_score"],
            item["attendance_percentage"]
        )
    )

    if average_engineering_score >= 80:
        performance_status = "Excellent"

    elif average_engineering_score >= 65:
        performance_status = "Good"

    elif average_engineering_score >= 50:
        performance_status = "Average"

    else:
        performance_status = "Needs Improvement"

    summary_data = {
        "mentor_id": mentor.id,
        "mentor_name": mentor.name,
        "department": mentor.department,
        "total_assigned_students": total_students,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "students_requiring_attention":
            students_requiring_attention,

        "performance_status": performance_status
    }

    ai_result = generate_mentor_summary_ai_analysis(
        summary_data=summary_data
    )

    return {
        **summary_data,

        "top_performer": {
            "student_id": top_student["student_id"],
            "student_name": top_student["student_name"],
            "engineering_score":
                top_student["engineering_score"],
            "attendance_percentage":
                top_student["attendance_percentage"],
            "approved_projects":
                top_student["approved_projects"]
        },

        "weak_performer": {
            "student_id": weak_student["student_id"],
            "student_name": weak_student["student_name"],
            "engineering_score":
                weak_student["engineering_score"],
            "attendance_percentage":
                weak_student["attendance_percentage"],
            "approved_projects":
                weak_student["approved_projects"]
        },

        "ai_summary": ai_result["ai_summary"],
        "recommendations": ai_result["recommendations"]
    }

def generate_mentor_summary_ai_analysis(
    summary_data: dict
):
    prompt = f"""
You are an AI performance analyst for an internship platform.

Analyze the following mentor team performance data:

{json.dumps(summary_data, indent=2)}

Instructions:

- Write a short professional summary of the mentor's team.
- Evaluate engineering performance, attendance and project results.
- Mention whether students require additional mentor attention.
- Provide exactly three practical recommendations.
- Recommendations should help the mentor improve student performance.
- Keep the response concise.
- Return valid JSON only.
- Do not return markdown.
- Do not include additional text.

Required JSON format:

{{
    "ai_summary": "Short mentor team summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        content = completion.choices[0].message.content

        result = json.loads(content)

        recommendations = result.get(
            "recommendations",
            []
        )

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Mentor summary generated successfully."
            ),
            "recommendations": recommendations[:3]
        }

    except Exception:
        return generate_mentor_summary_fallback(
            summary_data=summary_data
        )
    
def generate_mentor_summary_fallback(
    summary_data: dict
):
    score = summary_data[
        "average_engineering_score"
    ]

    attendance = summary_data[
        "average_attendance"
    ]

    rejected_projects = summary_data[
        "rejected_projects"
    ]

    attention_count = summary_data[
        "students_requiring_attention"
    ]

    if score >= 80:
        summary = (
            "The mentor's team is showing strong engineering "
            "performance and consistent project progress."
        )

    elif score >= 60:
        summary = (
            "The mentor's team is performing reasonably well, "
            "but some students still require focused support."
        )

    else:
        summary = (
            "The mentor's team requires additional technical "
            "guidance and closer performance monitoring."
        )

    recommendations = []

    if attendance < 75:
        recommendations.append(
            "Follow up with students who have inconsistent attendance."
        )

    if rejected_projects > 0:
        recommendations.append(
            "Conduct project review sessions focused on code quality, testing and documentation."
        )

    if attention_count > 0:
        recommendations.append(
            "Schedule individual mentoring sessions for students requiring attention."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Assign practical case studies according to each student's current skill level."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Give advanced engineering challenges to the strongest performers."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Review student progress every week using measurable learning goals."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }


def get_mentor_summary_report(
    db: Session
):
    mentors = db.query(Mentor).all()

    mentor_summaries = []

    for mentor in mentors:
        mentor_summary = get_single_mentor_summary(
            mentor=mentor,
            db=db
        )

        mentor_summaries.append(
            mentor_summary
        )

    mentor_summaries.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["average_attendance"],
            item["approved_projects"]
        ),
        reverse=True
    )

    return {
        "total_mentors": len(mentor_summaries),
        "mentors": mentor_summaries
    }



def calculate_single_team_performance(
    team_name: str,
    students: list,
    db: Session
):
    performances = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

    total_students = len(performances)

    if total_students == 0:
        return {
            "team_name": team_name,
            "total_students": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "project_approval_percentage": 0.0,
            "students_requiring_attention": 0,
            "top_performer": None,
            "performance_status": "No Data"
        }

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_students

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_students

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    students_requiring_attention = sum(
        1
        for item in performances
        if (
            item["engineering_score"] < 60
            or item["attendance_percentage"] < 70
        )
    )

    sorted_performances = sorted(
        performances,
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    top_student = sorted_performances[0]

    if average_engineering_score >= 80:
        performance_status = "Excellent"

    elif average_engineering_score >= 65:
        performance_status = "Good"

    elif average_engineering_score >= 50:
        performance_status = "Average"

    else:
        performance_status = "Needs Improvement"

    return {
        "team_name": team_name,
        "total_students": total_students,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "students_requiring_attention":
            students_requiring_attention,

        "top_performer": {
            "student_id": top_student["student_id"],
            "student_name": top_student["student_name"],
            "engineering_score":
                top_student["engineering_score"],
            "attendance_percentage":
                top_student["attendance_percentage"],
            "approved_projects":
                top_student["approved_projects"]
        },

        "performance_status": performance_status
    }


def get_team_performance_report(
    db: Session
):
    students = db.query(Student).all()

    grouped_students = defaultdict(list)

    for student in students:
        team_name = student.batch

        if not team_name:
            team_name = "Unassigned Batch"

        grouped_students[team_name].append(
            student
        )

    team_reports = []

    for team_name, team_students in grouped_students.items():
        team_report = calculate_single_team_performance(
            team_name=team_name,
            students=team_students,
            db=db
        )

        team_reports.append(team_report)

    team_reports.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        ),
        reverse=True
    )

    total_teams = len(team_reports)

    total_students = sum(
        item["total_students"]
        for item in team_reports
    )

    if total_students == 0:
        return {
            "total_teams": 0,
            "total_students": 0,
            "overall_average_engineering_score": 0.0,
            "overall_average_attendance": 0.0,
            "strongest_team": None,
            "weakest_team": None,
            "teams": [],
            "ai_summary": (
                "No student performance data is currently available."
            ),
            "recommendations": [
                "Add students and performance records before generating team analysis."
            ]
        }

    weighted_engineering_total = sum(
        item["average_engineering_score"]
        * item["total_students"]
        for item in team_reports
    )

    weighted_attendance_total = sum(
        item["average_attendance"]
        * item["total_students"]
        for item in team_reports
    )

    overall_average_engineering_score = (
        weighted_engineering_total / total_students
    )

    overall_average_attendance = (
        weighted_attendance_total / total_students
    )

    strongest_team = team_reports[0]["team_name"]

    weakest_team = min(
        team_reports,
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        )
    )["team_name"]

    report_data = {
        "total_teams": total_teams,
        "total_students": total_students,

        "overall_average_engineering_score": round(
            overall_average_engineering_score,
            2
        ),

        "overall_average_attendance": round(
            overall_average_attendance,
            2
        ),

        "strongest_team": strongest_team,
        "weakest_team": weakest_team,

        "teams": team_reports
    }

    ai_result = generate_team_performance_ai_analysis(
        report_data=report_data
    )

    return {
        **report_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }


def generate_team_performance_ai_analysis(
    report_data: dict
):
    compact_teams = [
        {
            "team_name": team["team_name"],
            "total_students": team["total_students"],
            "average_engineering_score":
                team["average_engineering_score"],
            "average_attendance":
                team["average_attendance"],
            "project_approval_percentage":
                team["project_approval_percentage"],
            "students_requiring_attention":
                team["students_requiring_attention"],
            "performance_status":
                team["performance_status"]
        }
        for team in report_data["teams"]
    ]

    prompt_data = {
        "total_teams": report_data["total_teams"],
        "total_students": report_data["total_students"],

        "overall_average_engineering_score":
            report_data[
                "overall_average_engineering_score"
            ],

        "overall_average_attendance":
            report_data[
                "overall_average_attendance"
            ],

        "strongest_team":
            report_data["strongest_team"],

        "weakest_team":
            report_data["weakest_team"],

        "teams": compact_teams
    }

    prompt = f"""
You are an AI performance analyst for an internship platform.

Analyze the following team performance report:

{json.dumps(prompt_data, indent=2)}

Instructions:

- Compare the performance of different batches.
- Mention the strongest and weakest team.
- Evaluate engineering score, attendance and project approval.
- Identify teams requiring additional support.
- Provide exactly three practical recommendations.
- Keep the summary short and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short team performance summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        recommendations = result.get(
            "recommendations",
            []
        )

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Team performance report generated successfully."
            ),

            "recommendations":
                recommendations[:3]
        }

    except Exception:
        return generate_team_performance_fallback(
            report_data=report_data
        )
    

def generate_team_performance_fallback(
    report_data: dict
):
    score = report_data[
        "overall_average_engineering_score"
    ]

    attendance = report_data[
        "overall_average_attendance"
    ]

    strongest_team = report_data[
        "strongest_team"
    ]

    weakest_team = report_data[
        "weakest_team"
    ]

    if score >= 80:
        summary = (
            f"Overall team performance is strong. "
            f"{strongest_team} is currently the highest-performing team."
        )

    elif score >= 60:
        summary = (
            f"Overall team performance is satisfactory. "
            f"{weakest_team} requires additional improvement support."
        )

    else:
        summary = (
            f"Overall team performance requires attention. "
            f"{weakest_team} should receive focused technical guidance."
        )

    recommendations = []

    if attendance < 75:
        recommendations.append(
            "Improve attendance monitoring across teams and follow up with frequently absent interns."
        )

    recommendations.append(
        f"Review the performance gaps of {weakest_team} and arrange targeted mentor sessions."
    )

    recommendations.append(
        f"Assign advanced case studies to strong performers in {strongest_team}."
    )

    if len(recommendations) < 3:
        recommendations.append(
            "Conduct cross-team technical workshops and project review sessions."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }

def normalize_technology_name(
    technology: str
):
    technology = technology.strip()

    technology_mapping = {
        "js": "JavaScript",
        "javascript": "JavaScript",

        "ts": "TypeScript",
        "typescript": "TypeScript",

        "reactjs": "React",
        "react.js": "React",
        "react": "React",

        "nextjs": "Next.js",
        "next.js": "Next.js",

        "nodejs": "Node.js",
        "node.js": "Node.js",
        "node": "Node.js",

        "expressjs": "Express.js",
        "express.js": "Express.js",
        "express": "Express.js",

        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",

        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",

        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "sqlite": "SQLite",

        "html": "HTML",
        "css": "CSS",

        "tailwind": "Tailwind CSS",
        "tailwindcss": "Tailwind CSS",
        "tailwind css": "Tailwind CSS",

        "python": "Python",
        "java": "Java",
        "c++": "C++",
        "c#": "C#",

        "docker": "Docker",
        "kubernetes": "Kubernetes",

        "git": "Git",
        "github": "GitHub",

        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",

        "langchain": "LangChain",
        "rag": "RAG",
        "n8n": "n8n"
    }

    lower_name = technology.lower()

    return technology_mapping.get(
        lower_name,
        technology.title()
    )


def parse_project_technologies(
    tech_stack: str
):
    if not tech_stack:
        return []

    technologies = re.split(
        r"[,;/|]+",
        tech_stack
    )

    cleaned_technologies = []

    for technology in technologies:
        technology = technology.strip()

        if not technology:
            continue

        normalized_name = normalize_technology_name(
            technology
        )

        if normalized_name not in cleaned_technologies:
            cleaned_technologies.append(
                normalized_name
            )

    return cleaned_technologies


def get_technology_performance_report(
    db: Session
):
    projects = db.query(Project).all()

    technology_data = defaultdict(
        lambda: {
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0
        }
    )

    for project in projects:
        technologies = parse_project_technologies(
            project.tech_stack
        )

        for technology in technologies:
            technology_data[
                technology
            ]["total_projects"] += 1

            if project.status == "Approved":
                technology_data[
                    technology
                ]["approved_projects"] += 1

            elif project.status == "Pending":
                technology_data[
                    technology
                ]["pending_projects"] += 1

            elif project.status == "Rejected":
                technology_data[
                    technology
                ]["rejected_projects"] += 1

    technology_reports = []

    for technology, data in technology_data.items():
        total_projects = data["total_projects"]

        approval_percentage = 0.0

        if total_projects > 0:
            approval_percentage = (
                data["approved_projects"]
                / total_projects
            ) * 100

        if approval_percentage >= 80:
            performance_status = "Excellent"

        elif approval_percentage >= 65:
            performance_status = "Good"

        elif approval_percentage >= 50:
            performance_status = "Average"

        else:
            performance_status = "Needs Improvement"

        technology_reports.append({
            "technology": technology,
            "total_projects": total_projects,

            "approved_projects":
                data["approved_projects"],

            "pending_projects":
                data["pending_projects"],

            "rejected_projects":
                data["rejected_projects"],

            "approval_percentage": round(
                approval_percentage,
                2
            ),

            "performance_status":
                performance_status
        })

    technology_reports.sort(
        key=lambda item: (
            item["approval_percentage"],
            item["approved_projects"],
            item["total_projects"]
        ),
        reverse=True
    )

    if not technology_reports:
        return {
            "total_technologies": 0,
            "total_projects_analyzed": 0,
            "strongest_technology": None,
            "weakest_technology": None,
            "technologies": [],
            "ai_summary": (
                "No project technology data is available."
            ),
            "recommendations": [
                "Add project records with valid technology stacks."
            ]
        }

    strongest_technology = (
        technology_reports[0]["technology"]
    )

    weakest_technology = min(
        technology_reports,
        key=lambda item: (
            item["approval_percentage"],
            item["approved_projects"],
            item["total_projects"]
        )
    )["technology"]

    report_data = {
        "total_technologies": len(
            technology_reports
        ),

        "total_projects_analyzed": len(
            projects
        ),

        "strongest_technology":
            strongest_technology,

        "weakest_technology":
            weakest_technology,

        "technologies":
            technology_reports
    }

    ai_result = (
        generate_technology_performance_ai_analysis(
            report_data=report_data
        )
    )

    return {
        **report_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }

def generate_technology_performance_ai_analysis(
    report_data: dict
):
    prompt_data = {
        "total_technologies":
            report_data["total_technologies"],

        "total_projects_analyzed":
            report_data["total_projects_analyzed"],

        "strongest_technology":
            report_data["strongest_technology"],

        "weakest_technology":
            report_data["weakest_technology"],

        "technologies":
            report_data["technologies"]
    }

    prompt = f"""
You are an AI engineering performance analyst.

Analyze the following technology performance report:

{json.dumps(prompt_data, indent=2)}

Instructions:

- Identify technologies with strong and weak project results.
- Consider approval percentage and number of projects.
- Do not judge a technology as highly successful based only
  on one approved project.
- Mention technologies with high rejection rates.
- Provide exactly three practical recommendations.
- Recommendations may include workshops, mentor support,
  easier case studies, advanced case studies, testing,
  documentation or project reviews.
- Keep the summary short and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short technology performance summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        recommendations = result.get(
            "recommendations",
            []
        )

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Technology performance report generated."
            ),

            "recommendations":
                recommendations[:3]
        }

    except Exception:
        return (
            generate_technology_performance_fallback(
                report_data=report_data
            )
        )
    
def generate_technology_performance_fallback(
    report_data: dict
):
    strongest = report_data[
        "strongest_technology"
    ]

    weakest = report_data[
        "weakest_technology"
    ]

    technologies = report_data[
        "technologies"
    ]

    rejected_technologies = sorted(
        technologies,
        key=lambda item: item[
            "rejected_projects"
        ],
        reverse=True
    )

    highest_rejected = None

    if rejected_technologies:
        highest_rejected = (
            rejected_technologies[0]
        )

    summary = (
        f"{strongest} currently shows the strongest "
        f"project performance, while {weakest} requires "
        f"additional improvement and technical support."
    )

    recommendations = [
        (
            f"Arrange focused workshops and mentor support "
            f"for {weakest}."
        ),
        (
            f"Assign advanced case studies using {strongest} "
            f"to interns showing strong performance."
        )
    ]

    if (
        highest_rejected
        and highest_rejected[
            "rejected_projects"
        ] > 0
    ):
        recommendations.append(
            (
                f"Review rejected "
                f"{highest_rejected['technology']} projects "
                f"with emphasis on testing, code quality "
                f"and documentation."
            )
        )

    else:
        recommendations.append(
            "Continue monitoring technology performance as more projects are submitted."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }

def calculate_productivity_period(
    db: Session,
    start_date: date,
    end_date: date
):
    students = db.query(Student).all()

    start_datetime = datetime.combine(
        start_date,
        time.min
    )

    end_datetime = datetime.combine(
        end_date + timedelta(days=1),
        time.min
    )

    attendance_percentages = []
    engineering_scores = []

    for student in students:
        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
            .all()
        )

        total_attendance = len(attendance_records)

        present_days = sum(
            1
            for record in attendance_records
            if record.status == "Present"
        )

        attendance_percentage = 0.0

        if total_attendance > 0:
            attendance_percentage = (
                present_days / total_attendance
            ) * 100

        student_projects = (
            db.query(Project)
            .filter(
                Project.student_id == student.id,
                Project.submitted_at >= start_datetime,
                Project.submitted_at < end_datetime
            )
            .all()
        )

        total_student_projects = len(
            student_projects
        )

        approved_student_projects = sum(
            1
            for project in student_projects
            if project.status == "Approved"
        )

        project_approval_percentage = 0.0

        if total_student_projects > 0:
            project_approval_percentage = (
                approved_student_projects
                / total_student_projects
            ) * 100

        engineering_score = (
            attendance_percentage * 0.40
            + project_approval_percentage * 0.60
        )

        attendance_percentages.append(
            attendance_percentage
        )

        engineering_scores.append(
            engineering_score
        )

    average_attendance = 0.0
    average_engineering_score = 0.0

    if students:
        average_attendance = (
            sum(attendance_percentages)
            / len(students)
        )

        average_engineering_score = (
            sum(engineering_scores)
            / len(students)
        )

    projects = (
        db.query(Project)
        .filter(
            Project.submitted_at >= start_datetime,
            Project.submitted_at < end_datetime
        )
        .all()
    )

    approved_projects = sum(
        1
        for project in projects
        if project.status == "Approved"
    )

    pending_projects = sum(
        1
        for project in projects
        if project.status == "Pending"
    )

    rejected_projects = sum(
        1
        for project in projects
        if project.status == "Rejected"
    )

    total_projects = len(projects)

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    return {
        "period_start": str(start_date),
        "period_end": str(end_date),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "average_engineering_score": round(
            average_engineering_score,
            2
        )
    }


def get_trend_label(
    change: float,
    positive_limit: float = 1.0
):
    if change >= positive_limit:
        return "Increasing"

    if change <= -positive_limit:
        return "Decreasing"

    return "Stable"

def get_productivity_trends_report(
    db: Session
):
    current_end = date.today()

    current_start = (
        current_end - timedelta(days=6)
    )

    previous_end = (
        current_start - timedelta(days=1)
    )

    previous_start = (
        previous_end - timedelta(days=6)
    )

    current_period = calculate_productivity_period(
        db=db,
        start_date=current_start,
        end_date=current_end
    )

    previous_period = calculate_productivity_period(
        db=db,
        start_date=previous_start,
        end_date=previous_end
    )

    attendance_change = round(
        current_period["average_attendance"]
        - previous_period["average_attendance"],
        2
    )

    project_submission_change = (
        current_period["total_projects"]
        - previous_period["total_projects"]
    )

    approved_project_change = (
        current_period["approved_projects"]
        - previous_period["approved_projects"]
    )

    engineering_score_change = round(
        current_period["average_engineering_score"]
        - previous_period["average_engineering_score"],
        2
    )

    approval_percentage_change = round(
        current_period["project_approval_percentage"]
        - previous_period["project_approval_percentage"],
        2
    )

    attendance_trend = get_trend_label(
        attendance_change
    )

    project_trend = get_trend_label(
        project_submission_change,
        positive_limit=1
    )

    approval_trend = get_trend_label(
        approval_percentage_change
    )

    engineering_trend = get_trend_label(
        engineering_score_change
    )

    positive_trends = sum([
        attendance_trend == "Increasing",
        project_trend == "Increasing",
        approval_trend == "Increasing",
        engineering_trend == "Increasing"
    ])

    negative_trends = sum([
        attendance_trend == "Decreasing",
        project_trend == "Decreasing",
        approval_trend == "Decreasing",
        engineering_trend == "Decreasing"
    ])

    if positive_trends >= 3:
        overall_productivity_status = (
            "Strong Improvement"
        )

    elif positive_trends >= 2:
        overall_productivity_status = (
            "Improving"
        )

    elif negative_trends >= 3:
        overall_productivity_status = (
            "Needs Immediate Attention"
        )

    elif negative_trends >= 2:
        overall_productivity_status = (
            "Declining"
        )

    else:
        overall_productivity_status = "Stable"

    trend_data = {
        "previous_period": previous_period,
        "current_period": current_period,

        "attendance_change": attendance_change,

        "project_submission_change":
            project_submission_change,

        "approved_project_change":
            approved_project_change,

        "engineering_score_change":
            engineering_score_change,

        "attendance_trend": attendance_trend,
        "project_trend": project_trend,
        "approval_trend": approval_trend,
        "engineering_trend": engineering_trend,

        "overall_productivity_status":
            overall_productivity_status
    }

    ai_result = generate_productivity_trends_ai_analysis(
        trend_data=trend_data
    )

    return {
        **trend_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }

def generate_productivity_trends_ai_analysis(
    trend_data: dict
):
    prompt = f"""
You are an AI productivity analyst for an internship platform.

Compare the current seven-day productivity period with the previous seven-day period.

Productivity data:

{json.dumps(trend_data, indent=2)}

Instructions:

- Explain attendance, project submission, project approval and engineering score trends.
- Clearly mention whether overall productivity is improving, stable or declining.
- Provide exactly three practical recommendations.
- Recommendations may include mentor meetings, attendance improvement,
  project reviews, technical workshops, easier case studies,
  advanced case studies, testing or documentation.
- Keep the summary short and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short productivity trends summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        recommendations = result.get(
            "recommendations",
            []
        )

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Productivity trends report generated."
            ),

            "recommendations":
                recommendations[:3]
        }

    except Exception:
        return generate_productivity_trends_fallback(
            trend_data=trend_data
        )
    
def generate_productivity_trends_fallback(
    trend_data: dict
):
    status = trend_data[
        "overall_productivity_status"
    ]

    attendance_trend = trend_data[
        "attendance_trend"
    ]

    project_trend = trend_data[
        "project_trend"
    ]

    engineering_trend = trend_data[
        "engineering_trend"
    ]

    if status in [
        "Strong Improvement",
        "Improving"
    ]:
        summary = (
            "Overall intern productivity is improving "
            "compared with the previous seven-day period."
        )

    elif status == "Stable":
        summary = (
            "Overall intern productivity remained stable "
            "during the current seven-day period."
        )

    else:
        summary = (
            "Overall intern productivity declined and "
            "requires additional mentor and technical support."
        )

    recommendations = []

    if attendance_trend == "Decreasing":
        recommendations.append(
            "Follow up with interns showing declining attendance and reinforce weekly participation expectations."
        )

    if project_trend == "Decreasing":
        recommendations.append(
            "Review project workloads and assign practical tasks with clear weekly deadlines."
        )

    if engineering_trend == "Decreasing":
        recommendations.append(
            "Schedule technical review sessions for interns whose engineering scores are declining."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Recognize productive interns and assign advanced case studies where appropriate."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Review pending and rejected projects with mentors to improve approval rates."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Track attendance and project activity every week to identify productivity problems early."
        )

    return {
        "ai_summary": summary,
        "recommendations": recommendations[:3]
    }

def is_student_active(
    student: Student,
    db: Session,
    activity_days: int = 14
):
    activity_start_date = (
        date.today() - timedelta(days=activity_days - 1)
    )

    activity_start_datetime = datetime.combine(
        activity_start_date,
        time.min
    )

    recent_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.date >= activity_start_date
        )
        .first()
    )

    recent_project = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.submitted_at >= activity_start_datetime
        )
        .first()
    )

    return bool(
        recent_attendance or recent_project
    )


def is_student_active(
    student: Student,
    db: Session,
    activity_days: int = 14
):
    activity_start_date = (
        date.today() - timedelta(days=activity_days - 1)
    )

    activity_start_datetime = datetime.combine(
        activity_start_date,
        time.min
    )

    recent_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.date >= activity_start_date
        )
        .first()
    )

    recent_project = (
        db.query(Project)
        .filter(
            Project.student_id == student.id,
            Project.submitted_at >= activity_start_datetime
        )
        .first()
    )

    return bool(
        recent_attendance or recent_project
    )



def get_overall_internship_health(
    db: Session
):
    students = db.query(Student).all()

    total_interns = len(students)

    if total_interns == 0:
        return {
            "health_score": 0.0,
            "health_status": "No Data",

            "metrics": {
                "total_interns": 0,
                "active_interns": 0,
                "inactive_interns": 0,
                "average_engineering_score": 0.0,
                "average_attendance": 0.0,
                "total_projects": 0,
                "approved_projects": 0,
                "pending_projects": 0,
                "rejected_projects": 0,
                "project_approval_percentage": 0.0,
                "students_requiring_attention": 0,
                "placement_ready_interns": 0
            },

            "ai_summary": (
                "No intern data is currently available."
            ),

            "recommendations": [
                "Add interns and performance records before generating platform health analysis."
            ]
        }

    performances = []

    active_interns = 0
    placement_ready_interns = 0
    students_requiring_attention = 0

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

        if is_student_active(
            student=student,
            db=db
        ):
            active_interns += 1

        if (
            performance["engineering_score"] >= 80
            and performance["attendance_percentage"] >= 80
            and performance["approved_projects"] >= 3
        ):
            placement_ready_interns += 1

        if (
            performance["engineering_score"] < 60
            or performance["attendance_percentage"] < 70
        ):
            students_requiring_attention += 1

    inactive_interns = (
        total_interns - active_interns
    )

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_interns

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_interns

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    active_percentage = (
        active_interns / total_interns
    ) * 100

    attention_percentage = (
        students_requiring_attention
        / total_interns
    ) * 100

    activity_health_score = (
        active_percentage * 0.20
    )

    engineering_health_score = (
        average_engineering_score * 0.30
    )

    attendance_health_score = (
        average_attendance * 0.25
    )

    project_health_score = (
        project_approval_percentage * 0.25
    )

    health_score = (
        activity_health_score
        + engineering_health_score
        + attendance_health_score
        + project_health_score
    )

    health_score = round(
        max(0, min(100, health_score)),
        2
    )

    if health_score >= 85:
        health_status = "Excellent"

    elif health_score >= 70:
        health_status = "Healthy"

    elif health_score >= 55:
        health_status = "Moderate"

    elif health_score >= 40:
        health_status = "Needs Improvement"

    else:
        health_status = "Critical"

    metrics = {
        "total_interns": total_interns,
        "active_interns": active_interns,
        "inactive_interns": inactive_interns,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "students_requiring_attention":
            students_requiring_attention,

        "placement_ready_interns":
            placement_ready_interns
    }

    analysis_data = {
        "health_score": health_score,
        "health_status": health_status,
        "attention_percentage": round(
            attention_percentage,
            2
        ),
        "metrics": metrics
    }

    ai_result = (
        generate_internship_health_ai_analysis(
            analysis_data=analysis_data
        )
    )

    return {
        "health_score": health_score,
        "health_status": health_status,
        "metrics": metrics,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }

def generate_internship_health_ai_analysis(
    analysis_data: dict
):
    prompt = f"""
You are an executive AI analyst for an internship management platform.

Analyze the following overall internship health data:

{json.dumps(analysis_data, indent=2)}

Instructions:

- Evaluate the overall condition of the internship program.
- Analyze intern activity, attendance, engineering performance,
  project approval rate and placement readiness.
- Mention any major risk such as inactive interns,
  weak attendance or low project approval.
- Provide exactly three practical recommendations.
- Keep the summary concise and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include any text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short overall internship health summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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

        recommendations = result.get(
            "recommendations",
            []
        )

        return {
            "ai_summary": result.get(
                "ai_summary",
                "Overall internship health report generated."
            ),

            "recommendations":
                recommendations[:3]
        }

    except Exception:
        return generate_internship_health_fallback(
            analysis_data=analysis_data
        )
    
def generate_internship_health_fallback(
    analysis_data: dict
):
    health_status = analysis_data[
        "health_status"
    ]

    metrics = analysis_data["metrics"]

    inactive_interns = metrics[
        "inactive_interns"
    ]

    average_attendance = metrics[
        "average_attendance"
    ]

    project_approval_percentage = metrics[
        "project_approval_percentage"
    ]

    attention_count = metrics[
        "students_requiring_attention"
    ]

    if health_status in [
        "Excellent",
        "Healthy"
    ]:
        summary = (
            "The internship program is currently showing "
            "healthy overall engineering and productivity performance."
        )

    elif health_status == "Moderate":
        summary = (
            "The internship program is stable, but several "
            "performance indicators require improvement."
        )

    else:
        summary = (
            "The internship program requires immediate attention "
            "due to weak activity or engineering performance."
        )

    recommendations = []

    if inactive_interns > 0:
        recommendations.append(
            "Contact inactive interns and schedule mentor follow-up meetings."
        )

    if average_attendance < 75:
        recommendations.append(
            "Improve attendance monitoring and investigate repeated absences."
        )

    if project_approval_percentage < 65:
        recommendations.append(
            "Conduct project review workshops focused on code quality, testing and documentation."
        )

    if attention_count > 0 and len(recommendations) < 3:
        recommendations.append(
            "Assign targeted learning plans to interns requiring additional support."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Assign advanced case studies to strong interns and evaluate them for placement readiness."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Review internship health metrics every week to identify risks early."
        )

    return {
        "ai_summary": summary,
        "recommendations":
            recommendations[:3]
    }


def calculate_batch_performance(
    batch_name: str,
    students: list,
    db: Session
):
    performances = []

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        performances.append(performance)

    total_students = len(performances)

    if total_students == 0:
        return {
            "batch": batch_name,
            "total_students": 0,
            "average_engineering_score": 0.0,
            "average_attendance": 0.0,
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0,
            "project_approval_percentage": 0.0,
            "placement_ready_students": 0,
            "students_requiring_attention": 0,
            "performance_status": "No Data"
        }

    average_engineering_score = sum(
        item["engineering_score"]
        for item in performances
    ) / total_students

    average_attendance = sum(
        item["attendance_percentage"]
        for item in performances
    ) / total_students

    total_projects = sum(
        item["total_projects"]
        for item in performances
    )

    approved_projects = sum(
        item["approved_projects"]
        for item in performances
    )

    pending_projects = sum(
        item["pending_projects"]
        for item in performances
    )

    rejected_projects = sum(
        item["rejected_projects"]
        for item in performances
    )

    project_approval_percentage = 0.0

    if total_projects > 0:
        project_approval_percentage = (
            approved_projects / total_projects
        ) * 100

    placement_ready_students = sum(
        1
        for item in performances
        if (
            item["engineering_score"] >= 80
            and item["attendance_percentage"] >= 80
            and item["approved_projects"] >= 3
        )
    )

    students_requiring_attention = sum(
        1
        for item in performances
        if (
            item["engineering_score"] < 60
            or item["attendance_percentage"] < 70
        )
    )

    if average_engineering_score >= 80:
        performance_status = "Excellent"

    elif average_engineering_score >= 65:
        performance_status = "Good"

    elif average_engineering_score >= 50:
        performance_status = "Average"

    else:
        performance_status = "Needs Improvement"

    return {
        "batch": batch_name,
        "total_students": total_students,

        "average_engineering_score": round(
            average_engineering_score,
            2
        ),

        "average_attendance": round(
            average_attendance,
            2
        ),

        "total_projects": total_projects,
        "approved_projects": approved_projects,
        "pending_projects": pending_projects,
        "rejected_projects": rejected_projects,

        "project_approval_percentage": round(
            project_approval_percentage,
            2
        ),

        "placement_ready_students":
            placement_ready_students,

        "students_requiring_attention":
            students_requiring_attention,

        "performance_status":
            performance_status
    }

def get_batch_comparison_report(
    db: Session
):
    students = db.query(Student).all()

    grouped_students = defaultdict(list)

    for student in students:
        batch_name = student.batch

        if not batch_name:
            batch_name = "Unassigned Batch"

        grouped_students[batch_name].append(
            student
        )

    batch_reports = []

    for batch_name, batch_students in grouped_students.items():
        batch_report = calculate_batch_performance(
            batch_name=batch_name,
            students=batch_students,
            db=db
        )

        batch_reports.append(batch_report)

    if not batch_reports:
        return {
            "total_batches": 0,
            "strongest_batch": None,
            "weakest_batch": None,
            "highest_attendance_batch": None,
            "highest_project_batch": None,
            "highest_placement_batch": None,
            "batches": [],
            "ai_summary": (
                "No batch performance data is currently available."
            ),
            "recommendations": [
                "Add students with valid batch information and performance records."
            ]
        }

    batch_reports.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        ),
        reverse=True
    )

    strongest_batch = batch_reports[0]["batch"]

    weakest_batch = min(
        batch_reports,
        key=lambda item: (
            item["average_engineering_score"],
            item["project_approval_percentage"],
            item["average_attendance"]
        )
    )["batch"]

    highest_attendance_batch = max(
        batch_reports,
        key=lambda item: (
            item["average_attendance"],
            item["average_engineering_score"]
        )
    )["batch"]

    highest_project_batch = max(
        batch_reports,
        key=lambda item: (
            item["approved_projects"],
            item["project_approval_percentage"]
        )
    )["batch"]

    highest_placement_batch = max(
        batch_reports,
        key=lambda item: (
            item["placement_ready_students"],
            item["average_engineering_score"]
        )
    )["batch"]

    report_data = {
        "total_batches": len(batch_reports),
        "strongest_batch": strongest_batch,
        "weakest_batch": weakest_batch,

        "highest_attendance_batch":
            highest_attendance_batch,

        "highest_project_batch":
            highest_project_batch,

        "highest_placement_batch":
            highest_placement_batch,

        "batches": batch_reports
    }

    ai_result = generate_batch_comparison_ai_analysis(
        report_data=report_data
    )

    return {
        **report_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }


def generate_batch_comparison_ai_analysis(
    report_data: dict
):
    prompt = f"""
You are an AI performance analyst for an internship platform.

Analyze the following batch comparison data:

{json.dumps(report_data, indent=2)}

Instructions:

- Compare all internship batches.
- Mention the strongest and weakest batch.
- Evaluate attendance, engineering score, project approval
  and placement readiness.
- Identify batches requiring mentor support.
- Provide exactly three practical recommendations.
- Keep the summary concise and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short batch comparison summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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
            "ai_summary": result.get(
                "ai_summary",
                "Batch comparison generated successfully."
            ),

            "recommendations": result.get(
                "recommendations",
                []
            )[:3]
        }

    except Exception:
        return generate_batch_comparison_fallback(
            report_data=report_data
        )
    

def generate_batch_comparison_fallback(
    report_data: dict
):
    strongest_batch = report_data[
        "strongest_batch"
    ]

    weakest_batch = report_data[
        "weakest_batch"
    ]

    highest_attendance_batch = report_data[
        "highest_attendance_batch"
    ]

    highest_placement_batch = report_data[
        "highest_placement_batch"
    ]

    summary = (
        f"{strongest_batch} is currently the strongest "
        f"performing batch, while {weakest_batch} requires "
        f"additional mentor and technical support."
    )

    recommendations = [
        (
            f"Review performance gaps in {weakest_batch} "
            f"and schedule focused mentor sessions."
        ),
        (
            f"Study the attendance practices of "
            f"{highest_attendance_batch} and apply them "
            f"to weaker batches."
        ),
        (
            f"Prepare placement-ready students from "
            f"{highest_placement_batch} for interviews "
            f"and client project evaluations."
        )
    ]

    return {
        "ai_summary": summary,
        "recommendations": recommendations
    }



def get_placement_readiness_report(
    db: Session
):
    students = db.query(Student).all()

    placement_students = []

    job_ready = 0
    interview_ready = 0
    client_ready = 0
    needs_improvement = 0

    for student in students:
        performance = calculate_student_engineering_score(
            student=student,
            db=db
        )

        score = performance["engineering_score"]

        attendance = performance[
            "attendance_percentage"
        ]

        approved_projects = performance[
            "approved_projects"
        ]

        if (
            score >= 85
            and attendance >= 90
            and approved_projects >= 4
        ):
            placement_status = "Ready for Job"

            recommended_action = (
                "Recommend Job Placement"
            )

            job_ready += 1

        elif (
            score >= 75
            and attendance >= 80
            and approved_projects >= 3
        ):
            placement_status = (
                "Ready for Interview"
            )

            recommended_action = (
                "Recommend Interview"
            )

            interview_ready += 1

        elif (
            score >= 70
            and attendance >= 75
            and approved_projects >= 2
        ):
            placement_status = (
                "Ready for Client Project"
            )

            recommended_action = (
                "Assign Advanced Case Study"
            )

            client_ready += 1

        else:
            placement_status = (
                "Needs Improvement"
            )

            recommended_action = (
                "Schedule Mentor Meeting"
            )

            needs_improvement += 1

        placement_students.append({
            "student_id": student.id,
            "student_name": student.name,
            "engineering_score": score,
            "attendance_percentage": attendance,
            "approved_projects": approved_projects,
            "placement_status": placement_status,
            "recommended_action": recommended_action
        })

    placement_students.sort(
        key=lambda item: (
            item["engineering_score"],
            item["approved_projects"],
            item["attendance_percentage"]
        ),
        reverse=True
    )

    summary = {
        "job_ready": job_ready,
        "interview_ready": interview_ready,
        "client_ready": client_ready,
        "needs_improvement": needs_improvement
    }

    report_data = {
        "summary": summary,
        "students": placement_students
    }

    ai_result = (
        generate_placement_readiness_ai_analysis(
            report_data=report_data
        )
    )

    return {
        **report_data,
        "ai_summary": ai_result["ai_summary"],
        "recommendations":
            ai_result["recommendations"]
    }

def generate_placement_readiness_ai_analysis(
    report_data: dict
):
    compact_students = [
        {
            "student_name":
                student["student_name"],

            "engineering_score":
                student["engineering_score"],

            "attendance_percentage":
                student["attendance_percentage"],

            "approved_projects":
                student["approved_projects"],

            "placement_status":
                student["placement_status"]
        }
        for student in report_data["students"]
    ]

    prompt_data = {
        "summary": report_data["summary"],
        "students": compact_students
    }

    prompt = f"""
You are an AI placement readiness analyst for an internship platform.

Analyze the following student placement readiness data:

{json.dumps(prompt_data, indent=2)}

Instructions:

- Evaluate how many students are ready for jobs, interviews,
  client projects or require improvement.
- Identify major readiness gaps.
- Mention whether the internship program has a strong hiring pipeline.
- Provide exactly three practical recommendations.
- Recommendations may include mock interviews, advanced case studies,
  mentor meetings, technical assessments or job placement preparation.
- Keep the summary concise and professional.
- Return valid JSON only.
- Do not include markdown.
- Do not include text outside the JSON object.

Required JSON format:

{{
    "ai_summary": "Short placement readiness summary",
    "recommendations": [
        "Recommendation one",
        "Recommendation two",
        "Recommendation three"
    ]
}}
"""

    try:
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
            "ai_summary": result.get(
                "ai_summary",
                "Placement readiness report generated successfully."
            ),

            "recommendations": result.get(
                "recommendations",
                []
            )[:3]
        }

    except Exception:
        return (
            generate_placement_readiness_fallback(
                report_data=report_data
            )
        )


def generate_placement_readiness_fallback(
    report_data: dict
):
    summary_data = report_data["summary"]

    job_ready = summary_data["job_ready"]

    interview_ready = summary_data[
        "interview_ready"
    ]

    client_ready = summary_data[
        "client_ready"
    ]

    needs_improvement = summary_data[
        "needs_improvement"
    ]

    total_students = (
        job_ready
        + interview_ready
        + client_ready
        + needs_improvement
    )

    ready_students = (
        job_ready
        + interview_ready
        + client_ready
    )

    if total_students == 0:
        return {
            "ai_summary": (
                "No student placement readiness data is available."
            ),

            "recommendations": [
                "Add student performance records before generating placement analysis."
            ]
        }

    readiness_percentage = (
        ready_students / total_students
    ) * 100

    if readiness_percentage >= 75:
        ai_summary = (
            "The internship program has a strong placement pipeline, "
            "with most students ready for jobs, interviews or client projects."
        )

    elif readiness_percentage >= 50:
        ai_summary = (
            "The internship program has moderate placement readiness, "
            "but several students still require additional preparation."
        )

    else:
        ai_summary = (
            "The internship program requires stronger technical and "
            "career preparation before most students are placement ready."
        )

    recommendations = []

    if job_ready > 0:
        recommendations.append(
            "Connect job-ready interns with placement opportunities and final technical interviews."
        )

    if interview_ready > 0:
        recommendations.append(
            "Schedule mock interviews and communication practice for interview-ready interns."
        )

    if client_ready > 0:
        recommendations.append(
            "Assign advanced client-style projects to students ready for practical exposure."
        )

    if needs_improvement > 0:
        recommendations.append(
            "Create focused mentoring plans for students requiring improvement."
        )

    if len(recommendations) < 3:
        recommendations.append(
            "Review placement readiness every week using attendance, project and engineering performance."
        )

    return {
        "ai_summary": ai_summary,
        "recommendations":
            recommendations[:3]
    }