from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Admin, CEO, Mentor, Student
from utils.jwt_handler import verify_access_token


# One common JWT bearer scheme for every role.
# Swagger will ask only for the JWT token.
bearer_scheme = HTTPBearer(
    scheme_name="JWT Access Token",
    description=(
        "Login through the appropriate endpoint, copy the "
        "access_token and paste it here."
    ),
    auto_error=False
)


UserModel = Union[
    Student,
    Mentor,
    Admin,
    CEO
]


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None
) -> str:
    """
    Extract the JWT token from the Authorization header.

    Expected header:

    Authorization: Bearer <token>
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    token = credentials.credentials.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return token


def _decode_token(
    credentials: HTTPAuthorizationCredentials | None
) -> dict:
    """
    Extract, decode and validate the JWT access token.
    """

    token = _extract_token(credentials)

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return payload


def _get_user_from_payload(
    payload: dict,
    db: Session
) -> UserModel:
    """
    Find the authenticated user using the role and ID
    stored inside the JWT payload.
    """

    role = payload.get("role")

    if role == "student":
        user_id = payload.get("student_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Student ID is missing from token"
            )

        user = (
            db.query(Student)
            .filter(Student.id == user_id)
            .first()
        )

    elif role == "mentor":
        user_id = payload.get("mentor_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mentor ID is missing from token"
            )

        user = (
            db.query(Mentor)
            .filter(Mentor.id == user_id)
            .first()
        )

    elif role == "admin":
        user_id = payload.get("admin_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin ID is missing from token"
            )

        user = (
            db.query(Admin)
            .filter(Admin.id == user_id)
            .first()
        )

    elif role == "ceo":
        user_id = payload.get("ceo_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CEO ID is missing from token"
            )

        user = (
            db.query(CEO)
            .filter(CEO.id == user_id)
            .first()
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user role in token"
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user was not found"
        )

    return user


def _require_role(
    payload: dict,
    required_role: str
) -> None:
    """
    Ensure that the JWT belongs to the required role.
    """

    token_role = payload.get("role")

    if token_role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"This endpoint is available to "
                f"{required_role}s only"
            )
        )


# Generic authenticated user
# Use this on endpoints accessible by every logged-in role.

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> UserModel:
    payload = _decode_token(credentials)

    return _get_user_from_payload(
        payload=payload,
        db=db
    )


# Student-only dependency

def get_current_student(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> Student:
    payload = _decode_token(credentials)

    _require_role(
        payload=payload,
        required_role="student"
    )

    user = _get_user_from_payload(
        payload=payload,
        db=db
    )

    if not isinstance(user, Student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students only"
        )

    return user


# Mentor-only dependency

def get_current_mentor(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> Mentor:
    payload = _decode_token(credentials)

    _require_role(
        payload=payload,
        required_role="mentor"
    )

    user = _get_user_from_payload(
        payload=payload,
        db=db
    )

    if not isinstance(user, Mentor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentors only"
        )

    return user


# Admin-only dependency

def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> Admin:
    payload = _decode_token(credentials)

    _require_role(
        payload=payload,
        required_role="admin"
    )

    user = _get_user_from_payload(
        payload=payload,
        db=db
    )

    if not isinstance(user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )

    return user


# CEO-only dependency

def get_current_ceo(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
) -> CEO:
    payload = _decode_token(credentials)

    _require_role(
        payload=payload,
        required_role="ceo"
    )

    user = _get_user_from_payload(
        payload=payload,
        db=db
    )

    if not isinstance(user, CEO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CEO only"
        )

    return user