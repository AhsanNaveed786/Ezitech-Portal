from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from backend.models import Student
from backend.schemas import StudentRegistration
from utils.security import hash_password, verify_password
from utils.jwt_handler import create_access_token

from backend.models import Student, Mentor, Admin, CEO

from backend.schemas import (
    StudentRegistration,
    MentorRegistration,
    AdminRegistration,
    CEORegistration
)


def register_student(student: StudentRegistration, db: Session):

    existing_student = db.query(Student).filter(
        Student.email == student.email
    ).first()

    if existing_student:
        return {"message": "Student already exists"}

    new_student = Student(
        name=student.name,
        email=student.email,
        password=hash_password(student.password),
        github_username=student.github_username,
        phone_number=student.phone_number,
        batch=student.batch,
        gender=student.gender
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student registered successfully"
    }


def login_student(form_data: OAuth2PasswordRequestForm, db: Session):

    existing_student = db.query(Student).filter(
        Student.email == form_data.username
    ).first()

    if not existing_student:
        return {"message": "Invalid email"}

    if not verify_password(form_data.password, existing_student.password):
        return {"message": "Invalid password"}

    access_token = create_access_token(
        data={
            "student_id": existing_student.id,
            "email": existing_student.email,
            "role": "student"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def register_mentor(mentor: MentorRegistration, db: Session):

    existing_mentor = db.query(Mentor).filter(
        Mentor.email == mentor.email
    ).first()

    if existing_mentor:
        return {"message": "Mentor already exists"}

    new_mentor = Mentor(
        name=mentor.name,
        email=mentor.email,
        password=hash_password(mentor.password),
        phone_number=mentor.phone_number,
        department=mentor.department,
        gender=mentor.gender
    )

    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)

    return {
        "message": "Mentor registered successfully"
    }


def login_mentor(form_data: OAuth2PasswordRequestForm, db: Session):

    existing_mentor = db.query(Mentor).filter(
        Mentor.email == form_data.username
    ).first()

    if not existing_mentor:
        return {"message": "Invalid email"}

    if not verify_password(form_data.password, existing_mentor.password):
        return {"message": "Invalid password"}

    access_token = create_access_token(
        data={
            "mentor_id": existing_mentor.id,
            "email": existing_mentor.email,
            "role": "mentor"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



def register_admin(admin: AdminRegistration, db: Session):

    existing_admin = db.query(Admin).filter(
        Admin.email == admin.email
    ).first()

    if existing_admin:
        return {"message": "Admin already exists"}

    new_admin = Admin(
        name=admin.name,
        email=admin.email,
        password=hash_password(admin.password),
        phone_number=admin.phone_number,
        gender=admin.gender
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "message": "Admin registered successfully"
    }


def login_admin(form_data: OAuth2PasswordRequestForm, db: Session):

    existing_admin = db.query(Admin).filter(
        Admin.email == form_data.username
    ).first()

    if not existing_admin:
        return {"message": "Invalid email"}

    if not verify_password(form_data.password, existing_admin.password):
        return {"message": "Invalid password"}

    access_token = create_access_token(
        data={
            "admin_id": existing_admin.id,
            "email": existing_admin.email,
            "role": "admin"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def register_ceo(ceo: CEORegistration, db: Session):

    existing_ceo = db.query(CEO).filter(
        CEO.email == ceo.email
    ).first()

    if existing_ceo:
        return {"message": "CEO already exists"}

    new_ceo = CEO(
        name=ceo.name,
        email=ceo.email,
        password=hash_password(ceo.password),
        phone_number=ceo.phone_number,
        gender=ceo.gender
    )

    db.add(new_ceo)
    db.commit()
    db.refresh(new_ceo)

    return {
        "message": "CEO registered successfully"
    }


def login_ceo(form_data: OAuth2PasswordRequestForm, db: Session):

    existing_ceo = db.query(CEO).filter(
        CEO.email == form_data.username
    ).first()

    if not existing_ceo:
        return {"message": "Invalid email"}

    if not verify_password(form_data.password, existing_ceo.password):
        return {"message": "Invalid password"}

    access_token = create_access_token(
        data={
            "ceo_id": existing_ceo.id,
            "email": existing_ceo.email,
            "role": "ceo"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }