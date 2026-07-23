from __future__ import annotations

from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models import (
    GitHubReport,
    Student
)


class GitHubReportStorageService:
    """
    Saves GitHub reports and provides report history,
    latest reports and student rankings.
    """

    @staticmethod
    def save_report(
        db: Session,
        student: Student,
        final_report: dict[str, Any]
    ) -> GitHubReport:
        scores = final_report.get(
            "scores",
            {}
        )

        best_repository = final_report.get(
            "best_repository"
        ) or {}

        saved_report = GitHubReport(
            student_id=student.id,
            github_username=(
                student.github_username
                or final_report.get("username")
                or ""
            ),
            profile_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get("profile_score")
                )
            ),
            activity_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get("activity_score")
                )
            ),
            repository_quality_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get(
                        "repository_quality_score"
                    )
                )
            ),
            documentation_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get(
                        "documentation_score"
                    )
                )
            ),
            testing_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get("testing_score")
                )
            ),
            ai_code_quality_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get(
                        "ai_code_quality_score"
                    )
                )
            ),
            final_github_score=(
                GitHubReportStorageService
                ._safe_score(
                    scores.get(
                        "final_github_score"
                    )
                )
            ),
            performance_level=str(
                final_report.get(
                    "performance_level",
                    "Weak"
                )
            ),
            assessment_status=str(
                final_report.get(
                    "assessment_status",
                    "partial"
                )
            ),
            repositories_analyzed=(
                GitHubReportStorageService
                ._safe_int(
                    final_report.get(
                        "repositories_analyzed"
                    )
                )
            ),
            repositories_with_ai_review=(
                GitHubReportStorageService
                ._safe_int(
                    final_report.get(
                        "repositories_with_ai_review"
                    )
                )
            ),
            best_repository_name=(
                best_repository.get("name")
            ),
            report_json=final_report
        )

        try:
            db.add(saved_report)
            db.commit()
            db.refresh(saved_report)

        except Exception:
            db.rollback()
            raise

        return saved_report

    @staticmethod
    def get_report_by_id(
        db: Session,
        report_id: int
    ) -> GitHubReport | None:
        return (
            db.query(GitHubReport)
            .filter(
                GitHubReport.id == report_id
            )
            .first()
        )

    @staticmethod
    def get_latest_student_report(
        db: Session,
        student_id: int
    ) -> GitHubReport | None:
        return (
            db.query(GitHubReport)
            .filter(
                GitHubReport.student_id
                == student_id
            )
            .order_by(
                GitHubReport.generated_at.desc(),
                GitHubReport.id.desc()
            )
            .first()
        )

    @staticmethod
    def get_student_report_history(
        db: Session,
        student_id: int,
        limit: int = 10
    ) -> list[GitHubReport]:
        safe_limit = max(
            1,
            min(limit, 50)
        )

        return (
            db.query(GitHubReport)
            .filter(
                GitHubReport.student_id
                == student_id
            )
            .order_by(
                GitHubReport.generated_at.desc(),
                GitHubReport.id.desc()
            )
            .limit(safe_limit)
            .all()
        )

    @staticmethod
    def count_student_reports(
        db: Session,
        student_id: int
    ) -> int:
        return (
            db.query(func.count(GitHubReport.id))
            .filter(
                GitHubReport.student_id
                == student_id
            )
            .scalar()
            or 0
        )

    @staticmethod
    def get_latest_student_rankings(
        db: Session,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Rank students using only their latest GitHub report.
        """

        safe_limit = max(
            1,
            min(limit, 100)
        )

        latest_report_subquery = (
            db.query(
                GitHubReport.student_id.label(
                    "student_id"
                ),
                func.max(
                    GitHubReport.id
                ).label("latest_report_id")
            )
            .group_by(
                GitHubReport.student_id
            )
            .subquery()
        )

        rows = (
            db.query(
                GitHubReport,
                Student
            )
            .join(
                latest_report_subquery,
                GitHubReport.id
                == latest_report_subquery.c.latest_report_id
            )
            .join(
                Student,
                Student.id
                == GitHubReport.student_id
            )
            .order_by(
                desc(
                    GitHubReport.final_github_score
                ),
                desc(
                    GitHubReport.ai_code_quality_score
                ),
                desc(
                    GitHubReport.activity_score
                )
            )
            .limit(safe_limit)
            .all()
        )

        rankings = []

        for rank, row in enumerate(
            rows,
            start=1
        ):
            report, student = row

            rankings.append({
                "rank": rank,
                "report_id": report.id,
                "student_id": student.id,
                "student_name": student.name,
                "github_username": (
                    report.github_username
                ),
                "final_github_score": (
                    report.final_github_score
                ),
                "ai_code_quality_score": (
                    report.ai_code_quality_score
                ),
                "activity_score": (
                    report.activity_score
                ),
                "performance_level": (
                    report.performance_level
                ),
                "best_repository_name": (
                    report.best_repository_name
                ),
                "generated_at": (
                    report.generated_at
                )
            })

        return rankings

    @staticmethod
    def _safe_score(
        value: Any
    ) -> float:
        try:
            score = float(value or 0)

        except (TypeError, ValueError):
            score = 0.0

        return round(
            max(
                0.0,
                min(score, 100.0)
            ),
            2
        )

    @staticmethod
    def _safe_int(
        value: Any
    ) -> int:
        try:
            return max(
                0,
                int(value or 0)
            )

        except (TypeError, ValueError):
            return 0

@staticmethod
def delete_report(
    db: Session,
    report_id: int
) -> bool:
    report = (
        db.query(GitHubReport)
        .filter(GitHubReport.id == report_id)
        .first()
    )

    if not report:
        return False

    try:
        db.delete(report)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return True