import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Admin,
    GitHubReport,
    Student
)
from backend.schemas import (
    GitHubRankingResponse,
    GitHubReportHistoryResponse,
    GitHubReportRequest,
    GitHubReportResponse,
    GitHubSavedReportDetailResponse
)
from backend.services.github_report import (
    GitHubCodeReviewer,
    GitHubDataCollector,
    GitHubFinalReportBuilder,
    GitHubReportStorageService,
    GitHubRepositoryAnalyzer
)
from backend.services.github_report.exceptions import (
    GitHubAPIError,
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubUserNotFoundError
)
from utils.dependencies import get_current_admin


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/ai/github",
    tags=["AI GitHub Reports"]
)


def get_student_or_404(
    student_id: int,
    db: Session
) -> Student:
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student was not found."
        )

    return student


@router.post(
    "/student/{student_id}/report",
    response_model=GitHubReportResponse,
    status_code=status.HTTP_200_OK
)
async def generate_student_github_report(
    student_id: int,
    request: GitHubReportRequest,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    student = get_student_or_404(
        student_id=student_id,
        db=db
    )

    github_username = (
        student.github_username.strip()
        if student.github_username
        else None
    )

    if not github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This student does not have a "
                "GitHub username registered."
            )
        )

    try:
        collector = GitHubDataCollector()
        analyzer = GitHubRepositoryAnalyzer()

        code_reviewer = GitHubCodeReviewer(
            max_files=(
                request.max_files_per_repository
            ),
            max_chars_per_file=7000,
            max_total_chars=35000
        )

        final_report_builder = (
            GitHubFinalReportBuilder()
        )

        github_data = (
            await collector
            .collect_student_github_data(
                username=github_username,
                repository_limit=(
                    request.repository_limit
                ),
                commit_limit=(
                    request.commit_limit
                )
            )
        )

        rules_report = (
            analyzer.analyze_student_data(
                collected_data=github_data
            )
        )

        ai_code_report = (
            await code_reviewer
            .review_student_repositories(
                username=github_username,
                repositories=github_data.get(
                    "repositories",
                    []
                ),
                repository_limit=(
                    request.ai_repository_limit
                )
            )
        )

        final_report = (
            final_report_builder.build_report(
                rules_report=rules_report,
                ai_code_report=ai_code_report
            )
        )

        saved_report = (
            GitHubReportStorageService.save_report(
                db=db,
                student=student,
                final_report=final_report
            )
        )

        return {
            "student_id": student.id,
            "student_name": student.name,
            "github_username": github_username,
            "saved_report_id": saved_report.id,
            "report": final_report
        }

    except GitHubUserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"GitHub user '{github_username}' "
                "was not found."
            )
        ) from error

    except GitHubAuthenticationError as error:
        logger.exception(
            "GitHub authentication failed."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "GitHub authentication failed. "
                "Check the server GITHUB_TOKEN."
            )
        ) from error

    except GitHubRateLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(error)
        ) from error

    except GitHubAPIError as error:
        logger.exception(
            "GitHub API request failed."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error)
        ) from error

    except HTTPException:
        raise

    except Exception as error:
        logger.exception(
            "GitHub report generation failed "
            "for student %s.",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The GitHub report could not be generated."
            )
        ) from error


@router.get(
    "/student/{student_id}/latest",
    response_model=GitHubSavedReportDetailResponse
)
def get_latest_github_report(
    student_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    get_student_or_404(
        student_id=student_id,
        db=db
    )

    report = (
        GitHubReportStorageService
        .get_latest_student_report(
            db=db,
            student_id=student_id
        )
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No GitHub report exists for "
                "this student."
            )
        )

    return report


@router.get(
    "/student/{student_id}/history",
    response_model=GitHubReportHistoryResponse
)
def get_github_report_history(
    student_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    student = get_student_or_404(
        student_id=student_id,
        db=db
    )

    reports = (
        GitHubReportStorageService
        .get_student_report_history(
            db=db,
            student_id=student_id,
            limit=limit
        )
    )

    total_reports = (
        GitHubReportStorageService
        .count_student_reports(
            db=db,
            student_id=student_id
        )
    )

    return {
        "student_id": student.id,
        "student_name": student.name,
        "github_username": (
            student.github_username or ""
        ),
        "total_reports": total_reports,
        "reports": reports
    }


@router.get(
    "/report/{report_id}",
    response_model=GitHubSavedReportDetailResponse
)
def get_saved_github_report(
    report_id: int,
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    report = (
        GitHubReportStorageService
        .get_report_by_id(
            db=db,
            report_id=report_id
        )
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub report was not found."
        )

    return report


@router.get(
    "/top-students",
    response_model=GitHubRankingResponse
)
def get_top_github_students(
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    current_admin: Admin = Depends(
        get_current_admin
    ),
    db: Session = Depends(get_db)
):
    rankings = (
        GitHubReportStorageService
        .get_latest_student_rankings(
            db=db,
            limit=limit
        )
    )

    return {
        "total_students": len(rankings),
        "rankings": rankings
    }