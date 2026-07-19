import base64
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.services.github_report.exceptions import (
    GitHubRepositoryNotFoundError
)

from backend.services.github_report.github_client import (
    GitHubClient
)


class GitHubDataCollector:
    def __init__(
        self,
        client: GitHubClient | None = None
    ):
        self.client = client or GitHubClient()

    async def collect_student_github_data(
        self,
        username: str,
        repository_limit: int = 10,
        commit_limit: int = 30
    ) -> dict[str, Any]:
        clean_username = self._clean_username(
            username
        )

        profile = await self.get_user_profile(
            clean_username
        )

        repositories = await self.get_user_repositories(
            username=clean_username,
            limit=repository_limit
        )

        repository_reports = []

        for repository in repositories:
            repository_name = repository["name"]

            repository_data = (
                await self.collect_repository_data(
                    owner=clean_username,
                    repository_name=repository_name,
                    commit_limit=commit_limit
                )
            )

            repository_reports.append(
                repository_data
            )

        return {
            "username": clean_username,
            "collected_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "profile": profile,
            "repository_count_analyzed": len(
                repository_reports
            ),
            "repositories": repository_reports
        }

    async def get_user_profile(
        self,
        username: str
    ) -> dict[str, Any]:
        profile = await self.client.get(
            f"/users/{username}"
        )

        return {
            "login": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "blog": profile.get("blog"),
            "avatar_url": profile.get("avatar_url"),
            "html_url": profile.get("html_url"),
            "public_repositories": profile.get(
                "public_repos",
                0
            ),
            "followers": profile.get(
                "followers",
                0
            ),
            "following": profile.get(
                "following",
                0
            ),
            "public_gists": profile.get(
                "public_gists",
                0
            ),
            "hireable": profile.get("hireable"),
            "created_at": profile.get(
                "created_at"
            ),
            "updated_at": profile.get(
                "updated_at"
            ),
            "profile_completeness": (
                self._calculate_profile_completeness(
                    profile
                )
            )
        }

    async def get_user_repositories(
        self,
        username: str,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        repositories = await self.client.get(
            f"/users/{username}/repos",
            params={
                "type": "owner",
                "sort": "updated",
                "direction": "desc",
                "per_page": safe_limit
            }
        )

        filtered_repositories = [
            repository
            for repository in repositories
            if not repository.get("fork", False)
            and not repository.get(
                "archived",
                False
            )
        ]

        filtered_repositories.sort(
            key=self._repository_priority_score,
            reverse=True
        )

        return filtered_repositories[
            :safe_limit
        ]

    async def collect_repository_data(
        self,
        owner: str,
        repository_name: str,
        commit_limit: int = 30
    ) -> dict[str, Any]:
        repository = await self.client.get(
            f"/repos/{owner}/{repository_name}"
        )

        languages = await self.get_repository_languages(
            owner=owner,
            repository_name=repository_name
        )

        root_files = await self.get_repository_root_files(
            owner=owner,
            repository_name=repository_name
        )

        readme = await self.get_repository_readme(
            owner=owner,
            repository_name=repository_name
        )

        commits = await self.get_repository_commits(
            owner=owner,
            repository_name=repository_name,
            limit=commit_limit
        )

        recent_commit_count = (
            self._count_recent_commits(
                commits=commits,
                days=90
            )
        )

        return {
            "name": repository.get("name"),
            "full_name": repository.get(
                "full_name"
            ),
            "description": repository.get(
                "description"
            ),
            "html_url": repository.get(
                "html_url"
            ),
            "homepage": repository.get(
                "homepage"
            ),
            "primary_language": repository.get(
                "language"
            ),
            "languages": languages,
            "topics": repository.get(
                "topics",
                []
            ),
            "visibility": repository.get(
                "visibility"
            ),
            "default_branch": repository.get(
                "default_branch"
            ),
            "stars": repository.get(
                "stargazers_count",
                0
            ),
            "forks": repository.get(
                "forks_count",
                0
            ),
            "open_issues": repository.get(
                "open_issues_count",
                0
            ),
            "size_kb": repository.get(
                "size",
                0
            ),
            "created_at": repository.get(
                "created_at"
            ),
            "updated_at": repository.get(
                "updated_at"
            ),
            "pushed_at": repository.get(
                "pushed_at"
            ),
            "has_issues": repository.get(
                "has_issues",
                False
            ),
            "has_projects": repository.get(
                "has_projects",
                False
            ),
            "has_wiki": repository.get(
                "has_wiki",
                False
            ),
            "root_files": root_files,
            "repository_structure": (
                self._analyze_repository_structure(
                    root_files
                )
            ),
            "readme": readme,
            "commits_analyzed": len(commits),
            "recent_commits_90_days": (
                recent_commit_count
            ),
            "commits": commits
        }

    async def get_repository_languages(
        self,
        owner: str,
        repository_name: str
    ) -> dict[str, Any]:
        languages = await self.client.get(
            f"/repos/{owner}/{repository_name}"
            "/languages"
        )

        total_bytes = sum(
            languages.values()
        )

        percentages = {}

        for language, byte_count in (
            languages.items()
        ):
            percentage = 0.0

            if total_bytes > 0:
                percentage = (
                    byte_count / total_bytes
                ) * 100

            percentages[language] = round(
                percentage,
                2
            )

        return {
            "bytes": languages,
            "percentages": percentages,
            "primary_language": (
                max(
                    languages,
                    key=languages.get
                )
                if languages
                else None
            )
        }

    async def get_repository_root_files(
        self,
        owner: str,
        repository_name: str
    ) -> list[dict[str, Any]]:
        contents = await self.client.get(
            f"/repos/{owner}/{repository_name}"
            "/contents"
        )

        if not isinstance(contents, list):
            return []

        return [
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size", 0),
                "download_url": item.get(
                    "download_url"
                )
            }
            for item in contents
        ]

    async def get_repository_readme(
        self,
        owner: str,
        repository_name: str
    ) -> dict[str, Any]:
        try:
            readme = await self.client.get(
                f"/repos/{owner}/{repository_name}"
                "/readme"
            )

        except GitHubRepositoryNotFoundError:
            return {
                "exists": False,
                "name": None,
                "content": "",
                "length": 0
            }

        encoded_content = readme.get(
            "content",
            ""
        )

        decoded_content = ""

        if encoded_content:
            try:
                decoded_content = (
                    base64.b64decode(
                        encoded_content
                    )
                    .decode(
                        "utf-8",
                        errors="replace"
                    )
                )

            except (ValueError, TypeError):
                decoded_content = ""

        return {
            "exists": True,
            "name": readme.get("name"),
            "path": readme.get("path"),
            "html_url": readme.get(
                "html_url"
            ),
            "content": decoded_content,
            "length": len(decoded_content)
        }

    async def get_repository_commits(
        self,
        owner: str,
        repository_name: str,
        limit: int = 30
    ) -> list[dict[str, Any]]:
        safe_limit = max(
            1,
            min(limit, 100)
        )

        try:
            commits = await self.client.get(
                f"/repos/{owner}/{repository_name}"
                "/commits",
                params={
                    "per_page": safe_limit
                }
            )

        except GitHubRepositoryNotFoundError:
            return []

        if not isinstance(commits, list):
            return []

        return [
            {
                "sha": commit.get("sha"),
                "html_url": commit.get(
                    "html_url"
                ),
                "message": (
                    commit.get(
                        "commit",
                        {}
                    )
                    .get(
                        "message",
                        ""
                    )
                ),
                "author_name": (
                    commit.get(
                        "commit",
                        {}
                    )
                    .get(
                        "author",
                        {}
                    )
                    .get("name")
                ),
                "author_email": (
                    commit.get(
                        "commit",
                        {}
                    )
                    .get(
                        "author",
                        {}
                    )
                    .get("email")
                ),
                "date": (
                    commit.get(
                        "commit",
                        {}
                    )
                    .get(
                        "author",
                        {}
                    )
                    .get("date")
                )
            }
            for commit in commits
        ]

    @staticmethod
    def _clean_username(
        username: str
    ) -> str:
        cleaned_username = username.strip()

        if not cleaned_username:
            raise ValueError(
                "GitHub username cannot be empty."
            )

        if "/" in cleaned_username:
            cleaned_username = (
                cleaned_username
                .rstrip("/")
                .split("/")[-1]
            )

        return cleaned_username

    @staticmethod
    def _calculate_profile_completeness(
        profile: dict[str, Any]
    ) -> dict[str, Any]:
        profile_fields = {
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get(
                "location"
            ),
            "blog": profile.get("blog"),
            "avatar": profile.get(
                "avatar_url"
            )
        }

        completed_fields = [
            field_name
            for field_name, value
            in profile_fields.items()
            if value
        ]

        total_fields = len(
            profile_fields
        )

        score = (
            len(completed_fields)
            / total_fields
        ) * 100

        return {
            "score": round(score, 2),
            "completed_fields": (
                completed_fields
            ),
            "missing_fields": [
                field_name
                for field_name, value
                in profile_fields.items()
                if not value
            ]
        }

    @staticmethod
    def _repository_priority_score(
        repository: dict[str, Any]
    ) -> float:
        score = 0.0

        if repository.get("description"):
            score += 10

        if repository.get("language"):
            score += 10

        if repository.get("topics"):
            score += 5

        score += min(
            repository.get(
                "stargazers_count",
                0
            ),
            20
        )

        score += min(
            repository.get(
                "forks_count",
                0
            ),
            10
        )

        pushed_at = repository.get(
            "pushed_at"
        )

        if pushed_at:
            try:
                pushed_date = (
                    datetime.fromisoformat(
                        pushed_at.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                age = (
                    datetime.now(
                        timezone.utc
                    )
                    - pushed_date
                )

                if age.days <= 30:
                    score += 30

                elif age.days <= 90:
                    score += 20

                elif age.days <= 180:
                    score += 10

            except ValueError:
                pass

        return score

    @staticmethod
    def _analyze_repository_structure(
        root_files: list[dict[str, Any]]
    ) -> dict[str, Any]:
        names = {
            str(item.get("name", "")).lower()
            for item in root_files
        }

        directories = {
            str(item.get("name", "")).lower()
            for item in root_files
            if item.get("type") == "dir"
        }

        has_readme = any(
            name.startswith("readme")
            for name in names
        )

        has_gitignore = (
            ".gitignore" in names
        )

        has_license = any(
            name.startswith("license")
            for name in names
        )

        has_requirements = (
            "requirements.txt" in names
            or "pyproject.toml" in names
            or "package.json" in names
            or "pom.xml" in names
            or "build.gradle" in names
        )

        has_tests = any(
            name in directories
            for name in {
                "test",
                "tests",
                "__tests__"
            }
        )

        has_source_folder = any(
            name in directories
            for name in {
                "src",
                "app",
                "backend",
                "frontend"
            }
        )

        structure_checks = {
            "has_readme": has_readme,
            "has_gitignore": has_gitignore,
            "has_license": has_license,
            "has_dependency_file": (
                has_requirements
            ),
            "has_tests_folder": has_tests,
            "has_source_folder": (
                has_source_folder
            )
        }

        passed_checks = sum(
            1
            for value in structure_checks.values()
            if value
        )

        score = (
            passed_checks
            / len(structure_checks)
        ) * 100

        return {
            **structure_checks,
            "structure_score": round(
                score,
                2
            )
        }

    @staticmethod
    def _count_recent_commits(
        commits: list[dict[str, Any]],
        days: int
    ) -> int:
        cutoff_date = (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        )

        recent_count = 0

        for commit in commits:
            commit_date = commit.get(
                "date"
            )

            if not commit_date:
                continue

            try:
                parsed_date = (
                    datetime.fromisoformat(
                        commit_date.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                if parsed_date >= cutoff_date:
                    recent_count += 1

            except ValueError:
                continue

        return recent_count