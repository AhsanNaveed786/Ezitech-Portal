from pydantic import BaseModel
from datetime import date

class StudentRegistration(BaseModel):
    name: str
    email: str
    password: str
    github_username: str
    phone_number: str
    batch: str
    gender: str

class MentorRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    department: str
    gender: str

class AdminRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    gender: str

class CEORegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    gender: str
    phone_number: str

class StudentLogin(BaseModel):
    email: str
    password: str

class MentorLogin(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

class CEOLogin(BaseModel):
    email: str
    password: str

from datetime import date, datetime


class AttendanceCheckIn(BaseModel):
    mentor_id: int


class AttendanceCheckOut(BaseModel):
    pass


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    mentor_id: int
    date: date
    status: str
    checked_in_time: datetime | None
    checked_out_time: datetime | None

    class Config:
        from_attributes = True

class LeaveApplication(BaseModel):
    reason: str
    leave_date: date

class ProjectSubmission(BaseModel):
    title: str
    description: str
    github_link: str
    tech_stack: str

class ProjectReview(BaseModel):
    remarks: str

# AI Chat

class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str

from pydantic import BaseModel


class AIDashboardResponse(BaseModel):
    engineering_score: int
    skill_growth: str
    weak_areas: list[str]
    recommendations: list[str]
    next_case_study: str

class AIDashboardResponse(BaseModel):
    engineering_score: int
    skill_growth: str
    weak_areas: list[str]
    recommendations: list[str]
    next_case_study: str