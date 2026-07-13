from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student, Mentor, Admin, CEO
from utils.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/student/login")


# Current User

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )

    role = payload.get("role")

    if role == "student":

        user = db.query(Student).filter(
            Student.id == payload["student_id"]
        ).first()

    elif role == "mentor":

        user = db.query(Mentor).filter(
            Mentor.id == payload["mentor_id"]
        ).first()

    elif role == "admin":

        user = db.query(Admin).filter(
            Admin.id == payload["admin_id"]
        ).first()

    elif role == "ceo":

        user = db.query(CEO).filter(
            CEO.id == payload["ceo_id"]
        ).first()

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Role"
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Student

def get_current_student(
    current_user=Depends(get_current_user)
):

    if not isinstance(current_user, Student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students only"
        )

    return current_user


# Mentor 

def get_current_mentor(
    current_user=Depends(get_current_user)
):

    if not isinstance(current_user, Mentor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentors only"
        )

    return current_user


# Admin 

def get_current_admin(
    current_user=Depends(get_current_user)
):

    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )

    return current_user


# CEO

def get_current_ceo(
    current_user=Depends(get_current_user)
):

    if not isinstance(current_user, CEO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CEO only"
        )

    return current_user