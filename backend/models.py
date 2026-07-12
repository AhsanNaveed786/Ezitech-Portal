
from backend.database import Base
from sqlalchemy import Column, Integer, String, Enum, Date, DateTime
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    phone_number = Column(String(11), unique=True)
    github_username = Column(String(50), unique=True)
    gender = Column(
        Enum("Male", "Female", "Other", name="gender_enum"),
        nullable=False
    )
    batch = Column(String(20))
    
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
    student_id = Column(Integer, nullable=False)
    mentor_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(
        Enum("Present", "Absent",name = "attendance_enum"), 
        nullable=False
    )
    checked_in_time = Column(DateTime)
    checked_out_time = Column(DateTime) 



