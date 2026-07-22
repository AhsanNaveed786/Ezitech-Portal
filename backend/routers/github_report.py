import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Admin, Student
from backend.schemas import (
    GitHubReportRequest,
    GitHubReportResponse
)
from backend.services.github_report import (
    GitHubCodeReviewer,
    GitHubDataCollector,
    GitHubFinalReportBuilder,
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

    github_username = (
        student.github_username.strip()
        if student.github_username
        else None
    )

    if not github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This student does not have a GitHub "
                "username registered."
            )
        )

    try:
        collector = GitHubDataCollector()

        analyzer = GitHubRepositoryAnalyzer()

        code_reviewer = GitHubCodeReviewer(
            max_files=request.max_files_per_repository,
            max_chars_per_file=7000,
            max_total_chars=35000
        )

        final_report_builder = (
            GitHubFinalReportBuilder()
        )

        github_data = (
            await collector.collect_student_github_data(
                username=github_username,
                repository_limit=request.repository_limit,
                commit_limit=request.commit_limit
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

        return {
            "student_id": student.id,
            "student_name": student.name,
            "github_username": github_username,
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
        logger.warning(
            "GitHub rate limit exceeded: %s",
            error
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(error)
        ) from error

    except GitHubAPIError as error:
        logger.exception(
            "GitHub API request failed for student %s.",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error)
        ) from error

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