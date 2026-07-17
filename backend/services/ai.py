from sqlalchemy.orm import Session
from utils.groq import client
from datetime import date, timedelta
import json

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