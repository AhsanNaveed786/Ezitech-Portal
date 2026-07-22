from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class GitHubFinalReportBuilder:
    """
    Combines the rules-based GitHub analysis and AI code review
    into one final student GitHub evaluation report.
    """

    DEFAULT_WEIGHTS = {
        "profile_score": 0.10,
        "activity_score": 0.15,
        "repository_quality_score": 0.15,
        "documentation_score": 0.10,
        "testing_score": 0.10,
        "ai_code_quality_score": 0.40
    }

    MAX_LIST_ITEMS = 10

    def __init__(
        self,
        weights: dict[str, float] | None = None
    ):
        self.weights = (
            weights.copy()
            if weights
            else self.DEFAULT_WEIGHTS.copy()
        )

        self._validate_weights()

    def build_report(
        self,
        rules_report: dict[str, Any],
        ai_code_report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Build the final GitHub report.

        Parameters:
        - rules_report: output from GitHubRepositoryAnalyzer
        - ai_code_report: output from GitHubCodeReviewer
        """

        username = (
            rules_report.get("username")
            or ai_code_report.get("username")
        )

        rules_scores = rules_report.get(
            "scores",
            {}
        )

        profile_score = self._safe_score(
            rules_scores.get("profile_score")
        )

        activity_score = self._safe_score(
            rules_scores.get("activity_score")
        )

        repository_quality_score = self._safe_score(
            rules_scores.get(
                "repository_quality_score"
            )
        )

        documentation_score = self._safe_score(
            rules_scores.get(
                "documentation_score"
            )
        )

        testing_score = self._safe_score(
            rules_scores.get("testing_score")
        )

        code_quality_summary = ai_code_report.get(
            "code_quality_summary",
            {}
        )

        repositories_with_ai_review = self._safe_int(
            code_quality_summary.get(
                "repositories_with_ai_review"
            )
        )

        ai_code_quality_score = self._safe_score(
            code_quality_summary.get(
                "average_code_quality_score"
            )
        )

        has_successful_ai_review = (
            repositories_with_ai_review > 0
        )

        score_values = {
            "profile_score": profile_score,
            "activity_score": activity_score,
            "repository_quality_score": (
                repository_quality_score
            ),
            "documentation_score": documentation_score,
            "testing_score": testing_score,
            "ai_code_quality_score": (
                ai_code_quality_score
            )
        }

        effective_weights = self._get_effective_weights(
            has_successful_ai_review=(
                has_successful_ai_review
            )
        )

        final_score = self._calculate_weighted_score(
            scores=score_values,
            weights=effective_weights
        )

        repository_rankings = (
            self._build_repository_rankings(
                rules_report=rules_report,
                ai_code_report=ai_code_report
            )
        )

        best_repository = (
            repository_rankings[0]
            if repository_rankings
            else None
        )

        strengths = self._collect_strengths(
            rules_report=rules_report,
            ai_code_report=ai_code_report,
            score_values=score_values
        )

        weaknesses = self._collect_weaknesses(
            rules_report=rules_report,
            ai_code_report=ai_code_report,
            score_values=score_values,
            has_successful_ai_review=(
                has_successful_ai_review
            )
        )

        recommendations = (
            self._collect_recommendations(
                rules_report=rules_report,
                ai_code_report=ai_code_report
            )
        )

        security_findings = (
            self._collect_security_findings(
                ai_code_report=ai_code_report
            )
        )

        limitations = self._collect_limitations(
            ai_code_report=ai_code_report,
            has_successful_ai_review=(
                has_successful_ai_review
            )
        )

        assessment_status = (
            "complete"
            if has_successful_ai_review
            else "partial"
        )

        return {
            "username": username,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "assessment_status": assessment_status,
            "repositories_analyzed": self._safe_int(
                rules_report.get(
                    "repositories_analyzed"
                )
            ),
            "repositories_with_ai_review": (
                repositories_with_ai_review
            ),
            "scores": {
                **score_values,
                "final_github_score": final_score
            },
            "weights_used": {
                key: round(value * 100, 2)
                for key, value
                in effective_weights.items()
            },
            "performance_level": (
                self._get_performance_level(
                    final_score
                )
            ),
            "best_repository": best_repository,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "security_findings": security_findings,
            "repository_rankings": repository_rankings,
            "summary": self._build_summary(
                username=username,
                final_score=final_score,
                has_successful_ai_review=(
                    has_successful_ai_review
                ),
                best_repository=best_repository
            ),
            "limitations": limitations
        }

    def _get_effective_weights(
        self,
        has_successful_ai_review: bool
    ) -> dict[str, float]:
        """
        When AI review is unavailable, its 40% weight is
        redistributed proportionally among rules-based scores.

        This prevents a failed API call from automatically giving
        the student a zero AI code-quality score.
        """

        if has_successful_ai_review:
            return self.weights.copy()

        rules_only_weights = {
            key: value
            for key, value in self.weights.items()
            if key != "ai_code_quality_score"
        }

        total_rules_weight = sum(
            rules_only_weights.values()
        )

        if total_rules_weight <= 0:
            return rules_only_weights

        return {
            key: value / total_rules_weight
            for key, value
            in rules_only_weights.items()
        }

    @staticmethod
    def _calculate_weighted_score(
        scores: dict[str, float],
        weights: dict[str, float]
    ) -> float:
        weighted_score = sum(
            scores.get(score_name, 0.0) * weight
            for score_name, weight
            in weights.items()
        )

        return round(
            max(
                0.0,
                min(weighted_score, 100.0)
            ),
            2
        )

    def _build_repository_rankings(
        self,
        rules_report: dict[str, Any],
        ai_code_report: dict[str, Any]
    ) -> list[dict[str, Any]]:
        rules_repositories = rules_report.get(
            "repository_reports",
            []
        )

        ai_reviews = ai_code_report.get(
            "repository_reviews",
            []
        )

        ai_review_map = {}

        for review in ai_reviews:
            repository = review.get(
                "repository",
                {}
            )

            repository_name = repository.get(
                "name"
            )

            if not repository_name:
                continue

            code_review = review.get(
                "code_review",
                {}
            )

            if (
                code_review.get("review_source")
                != "groq_ai"
            ):
                continue

            ai_review_map[repository_name.lower()] = {
                "code_quality_score": self._safe_score(
                    code_review.get(
                        "overall_code_quality_score"
                    )
                ),
                "readability_score": self._safe_score(
                    code_review.get(
                        "readability_score"
                    )
                ),
                "architecture_score": self._safe_score(
                    code_review.get(
                        "architecture_score"
                    )
                ),
                "maintainability_score": self._safe_score(
                    code_review.get(
                        "maintainability_score"
                    )
                ),
                "error_handling_score": self._safe_score(
                    code_review.get(
                        "error_handling_score"
                    )
                ),
                "security_score": self._safe_score(
                    code_review.get(
                        "security_score"
                    )
                )
            }

        rankings = []

        for repository in rules_repositories:
            repository_name = repository.get(
                "name"
            )

            if not repository_name:
                continue

            rules_repository_score = self._safe_score(
                repository.get(
                    "repository_score"
                )
            )

            ai_metrics = ai_review_map.get(
                repository_name.lower()
            )

            if ai_metrics:
                final_repository_score = round(
                    rules_repository_score * 0.40
                    + ai_metrics[
                        "code_quality_score"
                    ] * 0.60,
                    2
                )

                review_status = "ai_reviewed"

            else:
                final_repository_score = (
                    rules_repository_score
                )

                review_status = "rules_only"

            rankings.append({
                "name": repository_name,
                "full_name": repository.get(
                    "full_name"
                ),
                "html_url": repository.get(
                    "html_url"
                ),
                "primary_language": repository.get(
                    "primary_language"
                ),
                "rules_repository_score": (
                    rules_repository_score
                ),
                "ai_code_quality_score": (
                    ai_metrics.get(
                        "code_quality_score"
                    )
                    if ai_metrics
                    else None
                ),
                "final_repository_score": (
                    final_repository_score
                ),
                "performance_level": (
                    self._get_performance_level(
                        final_repository_score
                    )
                ),
                "review_status": review_status,
                "documentation_score": (
                    self._safe_score(
                        repository.get(
                            "documentation_score"
                        )
                    )
                ),
                "testing_score": self._safe_score(
                    repository.get(
                        "testing_score"
                    )
                ),
                "activity_score": self._safe_score(
                    repository.get(
                        "activity_score"
                    )
                ),
                "code_metrics": (
                    ai_metrics
                    if ai_metrics
                    else None
                )
            })

        rankings.sort(
            key=lambda item: (
                item["final_repository_score"],
                item["ai_code_quality_score"] or 0,
                item["activity_score"]
            ),
            reverse=True
        )

        for index, repository in enumerate(
            rankings,
            start=1
        ):
            repository["rank"] = index

        return rankings

    def _collect_strengths(
        self,
        rules_report: dict[str, Any],
        ai_code_report: dict[str, Any],
        score_values: dict[str, float]
    ) -> list[str]:
        strengths = list(
            rules_report.get(
                "strengths",
                []
            )
        )

        for repository_review in ai_code_report.get(
            "repository_reviews",
            []
        ):
            code_review = repository_review.get(
                "code_review",
                {}
            )

            if (
                code_review.get("review_source")
                != "groq_ai"
            ):
                continue

            repository_name = (
                repository_review
                .get("repository", {})
                .get("name", "Repository")
            )

            for strength in code_review.get(
                "strong_points",
                []
            ):
                strengths.append(
                    f"{repository_name}: {strength}"
                )

        if score_values["activity_score"] >= 80:
            strengths.append(
                "The student demonstrates strong and recent GitHub activity."
            )

        if (
            score_values["ai_code_quality_score"]
            >= 70
        ):
            strengths.append(
                "The analyzed source code demonstrates good overall engineering quality."
            )

        return self._deduplicate_strings(
            strengths
        )[:self.MAX_LIST_ITEMS]

    def _collect_weaknesses(
        self,
        rules_report: dict[str, Any],
        ai_code_report: dict[str, Any],
        score_values: dict[str, float],
        has_successful_ai_review: bool
    ) -> list[str]:
        weaknesses = list(
            rules_report.get(
                "weaknesses",
                []
            )
        )

        for repository_review in ai_code_report.get(
            "repository_reviews",
            []
        ):
            code_review = repository_review.get(
                "code_review",
                {}
            )

            if (
                code_review.get("review_source")
                != "groq_ai"
            ):
                continue

            repository_name = (
                repository_review
                .get("repository", {})
                .get("name", "Repository")
            )

            for weakness in code_review.get(
                "weak_points",
                []
            ):
                weaknesses.append(
                    f"{repository_name}: {weakness}"
                )

        if score_values["testing_score"] < 40:
            weaknesses.append(
                "Automated testing evidence is limited across the analyzed repositories."
            )

        if (
            score_values[
                "repository_quality_score"
            ] < 50
        ):
            weaknesses.append(
                "Repository organization and supporting configuration files need improvement."
            )

        if not has_successful_ai_review:
            weaknesses.append(
                "Actual code quality could not be fully evaluated because no AI code review completed successfully."
            )

        return self._deduplicate_strings(
            weaknesses
        )[:self.MAX_LIST_ITEMS]

    def _collect_recommendations(
        self,
        rules_report: dict[str, Any],
        ai_code_report: dict[str, Any]
    ) -> list[dict[str, Any]]:
        recommendations = []

        for recommendation in rules_report.get(
            "recommendations",
            []
        ):
            recommendations.append({
                "priority": "medium",
                "source": "rules_analyzer",
                "title": str(
                    recommendation
                ).strip(),
                "details": str(
                    recommendation
                ).strip()
            })

        for repository_review in ai_code_report.get(
            "repository_reviews",
            []
        ):
            repository_name = (
                repository_review
                .get("repository", {})
                .get("name", "Repository")
            )

            code_review = repository_review.get(
                "code_review",
                {}
            )

            if (
                code_review.get("review_source")
                != "groq_ai"
            ):
                continue

            for recommendation in code_review.get(
                "recommendations",
                []
            ):
                if not isinstance(
                    recommendation,
                    dict
                ):
                    continue

                recommendations.append({
                    "priority": str(
                        recommendation.get(
                            "priority",
                            "medium"
                        )
                    ).lower(),
                    "source": "ai_code_review",
                    "repository": repository_name,
                    "title": str(
                        recommendation.get(
                            "title",
                            "Code improvement"
                        )
                    ).strip(),
                    "details": str(
                        recommendation.get(
                            "details",
                            ""
                        )
                    ).strip()
                })

        recommendations = (
            self._deduplicate_recommendations(
                recommendations
            )
        )

        priority_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }

        recommendations.sort(
            key=lambda item: priority_order.get(
                item.get(
                    "priority",
                    "medium"
                ),
                2
            )
        )

        return recommendations[
            :self.MAX_LIST_ITEMS
        ]

    def _collect_security_findings(
        self,
        ai_code_report: dict[str, Any]
    ) -> list[dict[str, Any]]:
        findings = []

        for repository_review in ai_code_report.get(
            "repository_reviews",
            []
        ):
            repository_name = (
                repository_review
                .get("repository", {})
                .get("name", "Repository")
            )

            code_review = repository_review.get(
                "code_review",
                {}
            )

            if (
                code_review.get("review_source")
                != "groq_ai"
            ):
                continue

            for finding in code_review.get(
                "security_findings",
                []
            ):
                if not isinstance(finding, dict):
                    continue

                findings.append({
                    "repository": repository_name,
                    "severity": str(
                        finding.get(
                            "severity",
                            "low"
                        )
                    ).lower(),
                    "file": finding.get("file"),
                    "issue": finding.get("issue"),
                    "recommendation": finding.get(
                        "recommendation"
                    )
                })

        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }

        findings.sort(
            key=lambda finding: (
                severity_order.get(
                    finding.get(
                        "severity",
                        "low"
                    ),
                    3
                )
            )
        )

        return findings[
            :self.MAX_LIST_ITEMS
        ]

    def _collect_limitations(
        self,
        ai_code_report: dict[str, Any],
        has_successful_ai_review: bool
    ) -> list[str]:
        limitations = []

        for repository_review in ai_code_report.get(
            "repository_reviews",
            []
        ):
            code_review = repository_review.get(
                "code_review",
                {}
            )

            for limitation in code_review.get(
                "review_limitations",
                []
            ):
                limitations.append(
                    str(limitation)
                )

        if not has_successful_ai_review:
            limitations.append(
                "The final score was calculated using rules-based metrics because no successful AI code review was available."
            )

        limitations.append(
            "Only public repositories available through the GitHub API were analyzed."
        )

        limitations.append(
            "The AI reviewer analyzes selected important files instead of every file in each repository."
        )

        return self._deduplicate_strings(
            limitations
        )[:self.MAX_LIST_ITEMS]

    def _build_summary(
        self,
        username: str | None,
        final_score: float,
        has_successful_ai_review: bool,
        best_repository: dict[str, Any] | None
    ) -> str:
        display_username = (
            username or "The student"
        )

        performance_level = (
            self._get_performance_level(
                final_score
            )
        )

        review_type = (
            "rules-based analysis and AI code review"
            if has_successful_ai_review
            else "rules-based GitHub analysis"
        )

        summary = (
            f"{display_username} received a final GitHub "
            f"score of {final_score}, classified as "
            f"{performance_level}. The result is based on "
            f"{review_type}."
        )

        if best_repository:
            summary += (
                f" The strongest repository is "
                f"{best_repository['name']} with a final "
                f"repository score of "
                f"{best_repository['final_repository_score']}."
            )

        return summary

    def _validate_weights(self) -> None:
        required_fields = set(
            self.DEFAULT_WEIGHTS
        )

        missing_fields = (
            required_fields - set(self.weights)
        )

        if missing_fields:
            raise ValueError(
                "Missing GitHub report weights: "
                f"{sorted(missing_fields)}"
            )

        normalized_weights = {}

        for key, value in self.weights.items():
            try:
                weight = float(value)

            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid weight for {key}."
                ) from error

            if weight < 0:
                raise ValueError(
                    f"Weight for {key} cannot be negative."
                )

            normalized_weights[key] = weight

        total_weight = sum(
            normalized_weights.values()
        )

        if total_weight <= 0:
            raise ValueError(
                "Total GitHub report weight must be greater than zero."
            )

        self.weights = {
            key: value / total_weight
            for key, value
            in normalized_weights.items()
        }

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
    def _get_performance_level(
        score: float
    ) -> str:
        if score >= 85:
            return "Excellent"

        if score >= 70:
            return "Good"

        if score >= 55:
            return "Average"

        if score >= 40:
            return "Needs Improvement"

        return "Weak"

    @staticmethod
    def _deduplicate_strings(
        items: list[Any]
    ) -> list[str]:
        unique_items = []
        seen_items = set()

        for item in items:
            cleaned_item = str(
                item
            ).strip()

            if not cleaned_item:
                continue

            comparison_value = (
                cleaned_item.lower()
            )

            if comparison_value in seen_items:
                continue

            seen_items.add(
                comparison_value
            )

            unique_items.append(
                cleaned_item
            )

        return unique_items

    @staticmethod
    def _deduplicate_recommendations(
        recommendations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        unique_recommendations = []
        seen_titles = set()

        for recommendation in recommendations:
            title = str(
                recommendation.get(
                    "title",
                    ""
                )
            ).strip()

            if not title:
                continue

            comparison_title = title.lower()

            if comparison_title in seen_titles:
                continue

            seen_titles.add(
                comparison_title
            )

            unique_recommendations.append(
                recommendation
            )

        return unique_recommendations