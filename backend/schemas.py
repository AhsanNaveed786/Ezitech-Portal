from pydantic import BaseModel


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

class CEORegistration(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str

class AttendanceRecord(BaseModel):
    status: str

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