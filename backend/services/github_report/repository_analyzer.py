from __future__ import annotations

from statistics import mean
from typing import Any


class GitHubRepositoryAnalyzer:
    PROFILE_WEIGHT = 0.15
    ACTIVITY_WEIGHT = 0.20
    REPOSITORY_QUALITY_WEIGHT = 0.30
    DOCUMENTATION_WEIGHT = 0.20
    TESTING_WEIGHT = 0.15

    def analyze_student_data(
        self,
        collected_data: dict[str, Any]
    ) -> dict[str, Any]:
        profile = collected_data.get(
            "profile",
            {}
        )

        repositories = collected_data.get(
            "repositories",
            []
        )

        repository_reports = [
            self.analyze_repository(repository)
            for repository in repositories
        ]

        profile_score = self._calculate_profile_score(
            profile=profile
        )

        activity_score = self._calculate_activity_score(
            profile=profile,
            repositories=repositories
        )

        repository_quality_score = (
            self._average_repository_metric(
                reports=repository_reports,
                metric="repository_quality_score"
            )
        )

        documentation_score = (
            self._average_repository_metric(
                reports=repository_reports,
                metric="documentation_score"
            )
        )

        testing_score = (
            self._average_repository_metric(
                reports=repository_reports,
                metric="testing_score"
            )
        )

        overall_score = self._calculate_overall_score(
            profile_score=profile_score,
            activity_score=activity_score,
            repository_quality_score=(
                repository_quality_score
            ),
            documentation_score=documentation_score,
            testing_score=testing_score
        )

        strongest_repository = (
            self._find_strongest_repository(
                repository_reports
            )
        )

        strengths = self._generate_strengths(
            profile_score=profile_score,
            activity_score=activity_score,
            repository_quality_score=(
                repository_quality_score
            ),
            documentation_score=documentation_score,
            testing_score=testing_score,
            repositories=repositories
        )

        weaknesses = self._generate_weaknesses(
            profile_score=profile_score,
            activity_score=activity_score,
            repository_quality_score=(
                repository_quality_score
            ),
            documentation_score=documentation_score,
            testing_score=testing_score,
            repositories=repositories
        )

        recommendations = self._generate_recommendations(
            profile_score=profile_score,
            activity_score=activity_score,
            repository_quality_score=(
                repository_quality_score
            ),
            documentation_score=documentation_score,
            testing_score=testing_score,
            repositories=repositories
        )

        return {
            "username": collected_data.get(
                "username"
            ),
            "collected_at": collected_data.get(
                "collected_at"
            ),
            "repositories_analyzed": len(
                repository_reports
            ),
            "scores": {
                "profile_score": profile_score,
                "activity_score": activity_score,
                "repository_quality_score": (
                    repository_quality_score
                ),
                "documentation_score": (
                    documentation_score
                ),
                "testing_score": testing_score,
                "overall_github_score": overall_score
            },
            "performance_level": (
                self._get_performance_level(
                    overall_score
                )
            ),
            "strongest_repository": (
                strongest_repository
            ),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "repository_reports": repository_reports
        }

    def analyze_repository(
        self,
        repository: dict[str, Any]
    ) -> dict[str, Any]:
        structure = repository.get(
            "repository_structure",
            {}
        )

        readme = repository.get(
            "readme",
            {}
        )

        commits = repository.get(
            "commits",
            []
        )

        repository_quality_score = (
            self._calculate_repository_quality_score(
                repository=repository,
                structure=structure
            )
        )

        documentation_score = (
            self._calculate_documentation_score(
                repository=repository,
                readme=readme,
                structure=structure
            )
        )

        testing_score = (
            self._calculate_testing_score(
                repository=repository,
                structure=structure
            )
        )

        activity_score = (
            self._calculate_repository_activity_score(
                repository=repository,
                commits=commits
            )
        )

        base_repository_score = round(
            (
                repository_quality_score * 0.40
                + documentation_score * 0.20
                + testing_score * 0.15
                + activity_score * 0.25
            ),
            2
        )

        strengths = self._repository_strengths(
            repository=repository,
            structure=structure,
            readme=readme,
            activity_score=activity_score
        )

        weaknesses = self._repository_weaknesses(
            repository=repository,
            structure=structure,
            readme=readme,
            activity_score=activity_score
        )

        return {
            "name": repository.get("name"),
            "full_name": repository.get(
                "full_name"
            ),
            "html_url": repository.get(
                "html_url"
            ),
            "primary_language": repository.get(
                "primary_language"
            ),
            "repository_score": (
                base_repository_score
            ),
            "performance_level": (
                self._get_performance_level(
                    base_repository_score
                )
            ),
            "repository_quality_score": (
                repository_quality_score
            ),
            "documentation_score": (
                documentation_score
            ),
            "testing_score": testing_score,
            "activity_score": activity_score,
            "recent_commits_90_days": (
                repository.get(
                    "recent_commits_90_days",
                    0
                )
            ),
            "strengths": strengths,
            "weaknesses": weaknesses
        }

    def _calculate_profile_score(
        self,
        profile: dict[str, Any]
    ) -> float:
        score = 0.0

        completeness = profile.get(
            "profile_completeness",
            {}
        )

        score += self._safe_number(
            completeness.get("score")
        ) * 0.60

        public_repositories = self._safe_number(
            profile.get("public_repositories")
        )

        if public_repositories >= 10:
            score += 20

        elif public_repositories >= 5:
            score += 15

        elif public_repositories >= 2:
            score += 10

        elif public_repositories >= 1:
            score += 5

        followers = self._safe_number(
            profile.get("followers")
        )

        if followers >= 20:
            score += 10

        elif followers >= 10:
            score += 7

        elif followers >= 3:
            score += 4

        if profile.get("hireable") is True:
            score += 5

        if profile.get("blog"):
            score += 5

        return self._clamp_score(score)

    def _calculate_activity_score(
        self,
        profile: dict[str, Any],
        repositories: list[dict[str, Any]]
    ) -> float:
        if not repositories:
            return 0.0

        total_recent_commits = sum(
            int(
                repository.get(
                    "recent_commits_90_days",
                    0
                )
                or 0
            )
            for repository in repositories
        )

        active_repositories = sum(
            1
            for repository in repositories
            if int(
                repository.get(
                    "recent_commits_90_days",
                    0
                )
                or 0
            ) > 0
        )

        score = 0.0

        if total_recent_commits >= 50:
            score += 60

        elif total_recent_commits >= 30:
            score += 50

        elif total_recent_commits >= 15:
            score += 40

        elif total_recent_commits >= 5:
            score += 25

        elif total_recent_commits >= 1:
            score += 10

        active_ratio = (
            active_repositories
            / len(repositories)
        )

        score += active_ratio * 30

        updated_repositories = sum(
            1
            for repository in repositories
            if repository.get("pushed_at")
        )

        update_ratio = (
            updated_repositories
            / len(repositories)
        )

        score += update_ratio * 10

        return self._clamp_score(score)

    def _calculate_repository_quality_score(
        self,
        repository: dict[str, Any],
        structure: dict[str, Any]
    ) -> float:
        score = 0.0

        structure_score = self._safe_number(
            structure.get("structure_score")
        )

        score += structure_score * 0.50

        if repository.get("description"):
            score += 10

        topics = repository.get(
            "topics",
            []
        )

        if topics:
            score += min(
                len(topics) * 2,
                10
            )

        languages = repository.get(
            "languages",
            {}
        )

        language_percentages = languages.get(
            "percentages",
            {}
        )

        if language_percentages:
            score += 10

        if self._safe_number(
            repository.get("size_kb")
        ) > 0:
            score += 5

        if repository.get("default_branch"):
            score += 5

        stars = self._safe_number(
            repository.get("stars")
        )

        forks = self._safe_number(
            repository.get("forks")
        )

        score += min(stars, 5)
        score += min(forks, 5)

        return self._clamp_score(score)

    def _calculate_documentation_score(
        self,
        repository: dict[str, Any],
        readme: dict[str, Any],
        structure: dict[str, Any]
    ) -> float:
        score = 0.0

        if readme.get("exists"):
            score += 30

        readme_content = str(
            readme.get(
                "content",
                ""
            )
            or ""
        )

        readme_length = len(
            readme_content.strip()
        )

        if readme_length >= 2000:
            score += 35

        elif readme_length >= 1000:
            score += 30

        elif readme_length >= 500:
            score += 22

        elif readme_length >= 200:
            score += 14

        elif readme_length > 0:
            score += 5

        lower_readme = readme_content.lower()

        documentation_sections = [
            "installation",
            "usage",
            "features",
            "requirements",
            "setup",
            "getting started",
            "technologies",
            "api",
            "contributing"
        ]

        present_sections = sum(
            1
            for section in documentation_sections
            if section in lower_readme
        )

        score += min(
            present_sections * 4,
            20
        )

        if repository.get("description"):
            score += 5

        if structure.get("has_license"):
            score += 5

        if repository.get("topics"):
            score += 5

        return self._clamp_score(score)

    def _calculate_testing_score(
        self,
        repository: dict[str, Any],
        structure: dict[str, Any]
    ) -> float:
        score = 0.0

        if structure.get("has_tests_folder"):
            score += 65

        root_file_names = {
            str(
                item.get(
                    "name",
                    ""
                )
            ).lower()
            for item in repository.get(
                "root_files",
                []
            )
        }

        test_configurations = {
            "pytest.ini",
            "tox.ini",
            "jest.config.js",
            "jest.config.ts",
            "vitest.config.js",
            "vitest.config.ts",
            "phpunit.xml",
            "karma.conf.js"
        }

        if root_file_names.intersection(
            test_configurations
        ):
            score += 20

        automation_files = {
            ".github",
            "github-actions.yml",
            "github-actions.yaml",
            ".travis.yml",
            "jenkinsfile"
        }

        if root_file_names.intersection(
            automation_files
        ):
            score += 15

        return self._clamp_score(score)

    def _calculate_repository_activity_score(
        self,
        repository: dict[str, Any],
        commits: list[dict[str, Any]]
    ) -> float:
        recent_commits = int(
            repository.get(
                "recent_commits_90_days",
                0
            )
            or 0
        )

        score = 0.0

        if recent_commits >= 30:
            score += 70

        elif recent_commits >= 20:
            score += 60

        elif recent_commits >= 10:
            score += 45

        elif recent_commits >= 5:
            score += 30

        elif recent_commits >= 1:
            score += 15

        meaningful_messages = sum(
            1
            for commit in commits
            if self._is_meaningful_commit_message(
                str(
                    commit.get(
                        "message",
                        ""
                    )
                )
            )
        )

        if commits:
            meaningful_ratio = (
                meaningful_messages
                / len(commits)
            )

            score += meaningful_ratio * 20

        if repository.get("pushed_at"):
            score += 10

        return self._clamp_score(score)

    def _calculate_overall_score(
        self,
        profile_score: float,
        activity_score: float,
        repository_quality_score: float,
        documentation_score: float,
        testing_score: float
    ) -> float:
        score = (
            profile_score * self.PROFILE_WEIGHT
            + activity_score * self.ACTIVITY_WEIGHT
            + repository_quality_score
            * self.REPOSITORY_QUALITY_WEIGHT
            + documentation_score
            * self.DOCUMENTATION_WEIGHT
            + testing_score * self.TESTING_WEIGHT
        )

        return self._clamp_score(score)

    @staticmethod
    def _average_repository_metric(
        reports: list[dict[str, Any]],
        metric: str
    ) -> float:
        if not reports:
            return 0.0

        values = [
            float(
                report.get(
                    metric,
                    0
                )
                or 0
            )
            for report in reports
        ]

        return round(
            mean(values),
            2
        )

    @staticmethod
    def _find_strongest_repository(
        reports: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        if not reports:
            return None

        strongest = max(
            reports,
            key=lambda report: (
                report.get(
                    "repository_score",
                    0
                ),
                report.get(
                    "activity_score",
                    0
                )
            )
        )

        return {
            "name": strongest.get("name"),
            "html_url": strongest.get(
                "html_url"
            ),
            "repository_score": strongest.get(
                "repository_score"
            ),
            "performance_level": strongest.get(
                "performance_level"
            )
        }

    def _generate_strengths(
        self,
        profile_score: float,
        activity_score: float,
        repository_quality_score: float,
        documentation_score: float,
        testing_score: float,
        repositories: list[dict[str, Any]]
    ) -> list[str]:
        strengths = []

        if profile_score >= 75:
            strengths.append(
                "GitHub profile is complete and professionally presented."
            )

        if activity_score >= 70:
            strengths.append(
                "Commit activity is consistent across recent repositories."
            )

        if repository_quality_score >= 70:
            strengths.append(
                "Repositories have organized structure and useful project metadata."
            )

        if documentation_score >= 70:
            strengths.append(
                "Repositories contain clear and detailed documentation."
            )

        if testing_score >= 60:
            strengths.append(
                "Testing practices are visible in multiple repositories."
            )

        if len(repositories) >= 5:
            strengths.append(
                "The student has a diverse public project portfolio."
            )

        if not strengths:
            strengths.append(
                "The GitHub profile contains initial project evidence that can be improved further."
            )

        return strengths

    def _generate_weaknesses(
        self,
        profile_score: float,
        activity_score: float,
        repository_quality_score: float,
        documentation_score: float,
        testing_score: float,
        repositories: list[dict[str, Any]]
    ) -> list[str]:
        weaknesses = []

        if not repositories:
            weaknesses.append(
                "No eligible public repositories were available for analysis."
            )

        if profile_score < 60:
            weaknesses.append(
                "GitHub profile information is incomplete."
            )

        if activity_score < 50:
            weaknesses.append(
                "Recent commit activity is limited or inconsistent."
            )

        if repository_quality_score < 60:
            weaknesses.append(
                "Repository structure and project organization need improvement."
            )

        if documentation_score < 60:
            weaknesses.append(
                "README files and setup instructions are incomplete."
            )

        if testing_score < 50:
            weaknesses.append(
                "Automated tests are missing from most repositories."
            )

        return weaknesses

    def _generate_recommendations(
        self,
        profile_score: float,
        activity_score: float,
        repository_quality_score: float,
        documentation_score: float,
        testing_score: float,
        repositories: list[dict[str, Any]]
    ) -> list[str]:
        recommendations = []

        if profile_score < 70:
            recommendations.append(
                "Complete the GitHub bio, location, portfolio link and professional profile details."
            )

        if activity_score < 70:
            recommendations.append(
                "Commit meaningful progress regularly instead of uploading the entire project in one commit."
            )

        if repository_quality_score < 70:
            recommendations.append(
                "Add a clear source structure, dependency file, .gitignore and license."
            )

        if documentation_score < 70:
            recommendations.append(
                "Add README sections for features, installation, usage and technologies."
            )

        if testing_score < 60:
            recommendations.append(
                "Create a tests folder and add unit or integration tests for important functionality."
            )

        if len(repositories) < 3:
            recommendations.append(
                "Publish at least three complete and distinct portfolio projects."
            )

        if not recommendations:
            recommendations.append(
                "Maintain the current quality and add CI/CD automation to strengthen the portfolio further."
            )

        return recommendations

    def _repository_strengths(
        self,
        repository: dict[str, Any],
        structure: dict[str, Any],
        readme: dict[str, Any],
        activity_score: float
    ) -> list[str]:
        strengths = []

        if structure.get("has_source_folder"):
            strengths.append(
                "Clear source-code directory is present."
            )

        if structure.get("has_dependency_file"):
            strengths.append(
                "Dependency configuration is available."
            )

        if readme.get("exists") and readme.get(
            "length",
            0
        ) >= 500:
            strengths.append(
                "README provides useful project documentation."
            )

        if structure.get("has_tests_folder"):
            strengths.append(
                "Repository includes a testing directory."
            )

        if activity_score >= 60:
            strengths.append(
                "Repository shows healthy recent development activity."
            )

        if repository.get("topics"):
            strengths.append(
                "Repository topics improve project discoverability."
            )

        return strengths

    def _repository_weaknesses(
        self,
        repository: dict[str, Any],
        structure: dict[str, Any],
        readme: dict[str, Any],
        activity_score: float
    ) -> list[str]:
        weaknesses = []

        if not repository.get("description"):
            weaknesses.append(
                "Repository description is missing."
            )

        if not structure.get("has_gitignore"):
            weaknesses.append(
                ".gitignore file is missing."
            )

        if not structure.get("has_dependency_file"):
            weaknesses.append(
                "Dependency configuration file is missing."
            )

        if not structure.get("has_tests_folder"):
            weaknesses.append(
                "Tests folder is missing."
            )

        if not readme.get("exists"):
            weaknesses.append(
                "README file is missing."
            )

        elif readme.get("length", 0) < 200:
            weaknesses.append(
                "README content is too limited."
            )

        if activity_score < 40:
            weaknesses.append(
                "Repository has limited recent activity."
            )

        return weaknesses

    @staticmethod
    def _is_meaningful_commit_message(
        message: str
    ) -> bool:
        cleaned_message = (
            message.strip().lower()
        )

        if not cleaned_message:
            return False

        weak_messages = {
            "update",
            "updated",
            "changes",
            "change",
            "fix",
            "test",
            "final",
            "done",
            "upload files",
            "initial commit"
        }

        first_line = cleaned_message.splitlines()[0]

        if first_line in weak_messages:
            return False

        return len(first_line) >= 10

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
    def _safe_number(
        value: Any
    ) -> float:
        try:
            return float(value or 0)

        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _clamp_score(
        score: float
    ) -> float:
        return round(
            max(
                0.0,
                min(float(score), 100.0)
            ),
            2
        )