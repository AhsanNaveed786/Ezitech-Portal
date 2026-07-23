from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Admin,
    Mentor,
    Student
)
from backend.schemas import (
    OverdueTasksResponse,
    TaskCreate,
    TaskListResponse,
    TaskProgressUpdate,
    TaskResponse,
    TaskReviewRequest,
    TaskSubmissionRequest,
    TaskSummaryResponse
)
from backend.services.task_management import (
    TaskManagementService
)
from utils.dependencies import (
    get_current_admin,
    get_current_mentor,
    get_current_student
)


router = APIRouter(
    prefix="/tasks",
    tags=["Task Management"]
)


@router.post(
    "/mentor/assign",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_task(
    task_data: TaskCreate,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return TaskManagementService.assign_task(
        db=db,
        mentor=current_mentor,
        task_data=task_data
    )


@router.get(
    "/mentor/my-tasks",
    response_model=TaskListResponse
)
def get_mentor_assigned_tasks(
    limit: int = Query(
        default=100,
        ge=1,
        le=200
    ),
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    tasks = (
        TaskManagementService
        .get_mentor_tasks(
            db=db,
            mentor_id=current_mentor.id,
            limit=limit
        )
    )

    return {
        "total_records": len(tasks),
        "tasks": tasks
    }


@router.patch(
    "/mentor/{task_id}/review",
    response_model=TaskResponse
)
def review_submitted_task(
    task_id: int,
    review_data: TaskReviewRequest,
    current_mentor: Mentor = Depends(
        get_current_mentor
    ),
    db: Session = Depends(get_db)
):
    return TaskManagementService.review_task(
        db=db,
        mentor=current_mentor,
        task_id=task_id,
        review_data=review_data
    )


@router.get(
    "/student/my-tasks",
    response_model=TaskListResponse
)
def get_my_tasks(
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    ),
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    tasks = (
        TaskManagementService
        .get_student_tasks(
            db=db,
            student_id=current_student.id,
            limit=limit
        )
    )

    return {
        "total_records": len(tasks),
        "tasks": tasks
    }


@router.patch(
    "/student/{task_id}/progress",
    response_model=TaskResponse
)
def update_task_progress(
    task_id: int,
    progress_data: TaskProgressUpdate,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return (
        TaskManagementService
        .update_task_progress(
            db=db,
            student=current_student,
            task_id=task_id,
            progress_data=progress_data
        )
    )


@router.post(
    "/student/{task_id}/submit",
    response_model=TaskResponse
)
def submit_task(
    task_id: int,
    submission_data: TaskSubmissionRequest,
    current_student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):
    return TaskManagementService.submit_task(
        db=db,
        student=current_student,
        task_id=task_id,
        submission_data=submission_data
    )


@router.get(
    "/admin/overdue",
    response_model=OverdueTasksResponse
)
def get_overdue_tasks(
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    overdue_tasks = (
        TaskManagementService
        .get_overdue_tasks(
            db=db
        )
    )

    return {
        "total_overdue_tasks": len(
            overdue_tasks
        ),
        "overdue_tasks": overdue_tasks
    }


@router.get(
    "/admin/summary",
    response_model=TaskSummaryResponse
)
def get_task_summary(
    period_days: int = Query(
        default=30,
        ge=1,
        le=365
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    return (
        TaskManagementService
        .get_task_summary(
            db=db,
            period_days=period_days
        )
    )