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