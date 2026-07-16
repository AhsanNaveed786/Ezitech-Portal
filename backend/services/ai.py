from sqlalchemy.orm import Session
from utils.groq import client
import json
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