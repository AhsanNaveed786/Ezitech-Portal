from fastapi import FastAPI
from backend.database import engine
from backend.models import Student, Mentor, Attendance
from backend.models import Base
from backend.routers.auth_services import router as auth_router
from fastapi import Depends
from backend.routers import intelligence
from backend.routers import daily_activity
from backend.models import Student
from utils.dependencies import get_current_student
from backend.routers.attendance import router as attendance_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.leave import router as leave_router
from backend.routers.project import router as project_router
from backend.routers.ai import router as ai_router
from backend.routers import github_report
from backend.routers import task_management
from backend.routers import case_study
from backend.routers import mentor_feedback
from backend.routers import learning_credits
from backend.routers import engineering_score
from backend.routers import ai_recommendation
from backend.routers import report_dashboard
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(
    intelligence.router
)
app.include_router(
    report_dashboard.router
)
app.include_router(
    ai_recommendation.router
)
app.include_router(
    engineering_score.router
)
app.include_router(
    case_study.router
)
app.include_router(
    mentor_feedback.router
)
app.include_router(
    task_management.router
)
app.include_router(
    github_report.router
)
app.include_router(
    daily_activity.router
)
app.include_router(auth_router)
app.include_router(attendance_router)
app.include_router(dashboard_router)
app.include_router(leave_router)
app.include_router(project_router)
app.include_router(ai_router)
app.include_router(learning_credits.router)
@app.get("/student/profile")
def student_profile(current_student: Student = Depends(get_current_student)):
    return {
        "id": current_student.id,
        "name": current_student.name,
        "email": current_student.email,
        "github_username": current_student.github_username,
        "batch": current_student.batch,
        "gender": current_student.gender
    }

@app.get("/")
def home():
    return {"message": "Hello, World!"}     

@app.get("/student")
def student():
    return {"message": "Hello, Student!"}

@app.get("/admin")
def admin():
    return {"message": "Hello, Admin!"}

@app.get("/ceo")
def ceo():
    return {"message": "Hello, CEO!"}
