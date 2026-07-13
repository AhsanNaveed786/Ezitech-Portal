from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from backend.database import get_db

from backend.schemas import (
    StudentRegistration,
    MentorRegistration,
    AdminRegistration,
    CEORegistration
)

from backend.services.authorization import (
    register_student,
    login_student,
    register_mentor,
    login_mentor,
    register_admin,
    login_admin,
    register_ceo,
    login_ceo
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/student/register")
def student_register(
    student: StudentRegistration,
    db: Session = Depends(get_db)
):
    return register_student(student, db)


@router.post("/student/login")
def student_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_student(form_data, db)

@router.post("/mentor/register")
def mentor_register(
    mentor: MentorRegistration,
    db: Session = Depends(get_db)
):
    return register_mentor(mentor, db)

@router.post("/mentor/login")
def mentor_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_mentor(form_data, db)

@router.post("/admin/register")
def admin_register(
    admin: AdminRegistration,
    db: Session = Depends(get_db)
):
    return register_admin(admin, db)


@router.post("/admin/login")
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_admin(form_data, db)

@router.post("/ceo/register")
def ceo_register(
    ceo: CEORegistration,
    db: Session = Depends(get_db)
):
    return register_ceo(ceo, db)


@router.post("/ceo/login")
def ceo_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_ceo(form_data, db)