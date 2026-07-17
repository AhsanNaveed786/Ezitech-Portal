
import datetime

from datetime import datetime

from backend.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, DateTime

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    phone_number = Column(String(11), unique=True)
    github_username = Column(String(50), unique=True)

    gender = Column(
        Enum(
            "Male",
            "Female",
            "Other",
            name="gender_enum"
        ),
        nullable=False
    )

    batch = Column(String(20))

    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id"),
        nullable=True
    )
    
class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    phone_number = Column(String(11), unique=True)
    gender = Column(
        Enum("Male", "Female", "Other", name="gender_enum"),
        nullable=False
    )
    department = Column(String(50))

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    phone_number = Column(String(11))
    gender = Column(
        Enum("Male", "Female", "Other",name = "gender_enum"), 
        nullable=False
    )

class CEO(Base):
    __tablename__ = "ceos"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    phone_number = Column(String(11))
    gender = Column(
        Enum("Male", "Female", "Other",name = "gender_enum"), 
        nullable=False
    )

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    mentor_id = Column(Integer, ForeignKey("mentors.id"))
    date = Column(Date, nullable=False)
    status = Column(
        Enum("Present", "Absent",name = "attendance_enum"), 
        nullable=False
    )
    checked_in_time = Column(DateTime)
    checked_out_time = Column(DateTime) 


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    reason = Column(String(500))

    leave_date = Column(Date)

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
        default=datetime.utcnow
    )

    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id"),
        nullable=True
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    title = Column(String(150), nullable=False)

    description = Column(String(1000), nullable=False)

    github_link = Column(String(300), nullable=False)

    tech_stack = Column(String(300), nullable=False)

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

    mentor_remarks = Column(String(1000))

    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id"),
        nullable=True
    )

    submitted_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    reviewed_at = Column(DateTime)