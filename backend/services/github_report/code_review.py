from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import re
from statistics import mean
from typing import Any

from backend.services.github_report.exceptions import (
    GitHubAPIError,
    GitHubRepositoryNotFoundError
)
from backend.services.github_report.github_client import (
    GitHubClient
)
from utils.groq import client


logger = logging.getLogger(__name__)


class GitHubCodeReviewer:
    """
    Fetches selected source-code files from GitHub and uses
    Groq to generate a structured code-quality review.
    """

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".kt",
        ".kts",
        ".cpp",
        ".cc",
        ".cxx",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".swift",
        ".dart",
        ".sql",
        ".html",
        ".css",
        ".scss",
        ".vue"
    }

    IMPORTANT_FILENAMES = {
        "main.py",
        "app.py",
        "server.py",
        "manage.py",
        "settings.py",
        "urls.py",
        "models.py",
        "schemas.py",
        "database.py",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml"
    }

    EXCLUDED_DIRECTORIES = {
        ".git",
        ".github",
        ".idea",
        ".vscode",
        ".next",
        ".nuxt",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "vendor",
        "dist",
        "build",
        "target",
        "coverage",
        "migrations",
        "static",
        "public",
        "assets",
        "images",
        "fonts",
        "uploads",
        "datasets",
        "data"
    }

    EXCLUDED_FILENAMES = {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "composer.lock"
    }

    GENERATED_FILE_PATTERNS = {
        ".min.js",
        ".min.css",
        ".bundle.js",
        ".map"
    }

    MAX_SCORE = 100.0

    def __init__(
        self,
        github_client: GitHubClient | None = None,
        model: str | None = None,
        max_files: int = 8,
        max_chars_per_file: int = 7000,
        max_total_chars: int = 35000
    ):
        self.github_client = (
            github_client or GitHubClient()
        )

        self.model = (
            model
            or os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            )
        )

        self.max_files = max(
            1,
            min(max_files, 20)
        )

        self.max_chars_per_file = max(
            1000,
            min(max_chars_per_file, 15000)
        )

        self.max_total_chars = max(
            5000,
            min(max_total_chars, 70000)
        )

    async def review_repository(
        self,
        owner: str,
        repository_name: str,
        default_branch: str | None = None
    ) -> dict[str, Any]:
        """
        Review one GitHub repository.

        Steps:
        1. Fetch repository metadata.
        2. Fetch recursive Git tree.
        3. Select important code files.
        4. Fetch selected file contents.
        5. Send code context to Groq.
        """

        clean_owner = self._clean_value(
            owner,
            field_name="Repository owner"
        )

        clean_repository_name = self._clean_value(
            repository_name,
            field_name="Repository name"
        )

        repository = await self.github_client.get(
            f"/repos/{clean_owner}/{clean_repository_name}"
        )

        branch = (
            default_branch
            or repository.get("default_branch")
            or "main"
        )

        tree = await self._get_repository_tree(
            owner=clean_owner,
            repository_name=clean_repository_name,
            branch=branch
        )

        selected_files = self._select_code_files(
            tree=tree
        )

        source_files = await self._fetch_selected_files(
            owner=clean_owner,
            repository_name=clean_repository_name,
            branch=branch,
            selected_files=selected_files
        )

        if not source_files:
            return self._build_no_code_response(
                repository=repository,
                branch=branch
            )

        code_context = self._build_code_context(
            source_files=source_files
        )

        ai_review = await asyncio.to_thread(
            self._request_ai_review,
            repository,
            source_files,
            code_context
        )

        return {
            "repository": {
                "name": repository.get("name"),
                "full_name": repository.get(
                    "full_name"
                ),
                "html_url": repository.get(
                    "html_url"
                ),
                "description": repository.get(
                    "description"
                ),
                "primary_language": repository.get(
                    "language"
                ),
                "default_branch": branch
            },
            "files_discovered": len(tree),
            "files_selected": len(source_files),
            "analyzed_files": [
                {
                    "path": file_data["path"],
                    "language": file_data[
                        "language"
                    ],
                    "characters_analyzed": len(
                        file_data["content"]
                    ),
                    "truncated": file_data[
                        "truncated"
                    ]
                }
                for file_data in source_files
            ],
            "code_review": ai_review
        }

    async def review_student_repositories(
        self,
        username: str,
        repositories: list[dict[str, Any]],
        repository_limit: int = 3
    ) -> dict[str, Any]:
        """
        Review the strongest repositories already selected
        by the collector/analyzer.
        """

        safe_limit = max(
            1,
            min(repository_limit, 5)
        )

        selected_repositories = (
            repositories[:safe_limit]
        )

        repository_reviews = []

        for repository in selected_repositories:
            repository_name = repository.get(
                "name"
            )

            if not repository_name:
                continue

            try:
                review = await self.review_repository(
                    owner=username,
                    repository_name=repository_name,
                    default_branch=repository.get(
                        "default_branch"
                    )
                )

                repository_reviews.append(review)

            except (
                GitHubAPIError,
                GitHubRepositoryNotFoundError
            ) as error:
                logger.warning(
                    "Could not review repository %s/%s: %s",
                    username,
                    repository_name,
                    error
                )

                repository_reviews.append({
                    "repository": {
                        "name": repository_name,
                        "full_name": (
                            f"{username}/{repository_name}"
                        ),
                        "html_url": repository.get(
                            "html_url"
                        )
                    },
                    "error": str(error),
                    "code_review": (
                        self._fallback_review(
                            reason=str(error)
                        )
                    )
                })

        summary = self._build_student_code_summary(
            repository_reviews
        )

        return {
            "username": username,
            "repositories_requested": len(
                selected_repositories
            ),
            "repositories_reviewed": len(
                repository_reviews
            ),
            "code_quality_summary": summary,
            "repository_reviews": (
                repository_reviews
            )
        }

    async def _get_repository_tree(
        self,
        owner: str,
        repository_name: str,
        branch: str
    ) -> list[dict[str, Any]]:
        try:
            response = await self.github_client.get(
                f"/repos/{owner}/{repository_name}"
                f"/git/trees/{branch}",
                params={
                    "recursive": "1"
                }
            )

        except GitHubRepositoryNotFoundError:
            repository = await self.github_client.get(
                f"/repos/{owner}/{repository_name}"
            )

            fallback_branch = repository.get(
                "default_branch",
                "main"
            )

            response = await self.github_client.get(
                f"/repos/{owner}/{repository_name}"
                f"/git/trees/{fallback_branch}",
                params={
                    "recursive": "1"
                }
            )

        tree = response.get(
            "tree",
            []
        )

        if not isinstance(tree, list):
            return []

        return tree

    def _select_code_files(
        self,
        tree: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        candidates = []

        for item in tree:
            if item.get("type") != "blob":
                continue

            path = str(
                item.get(
                    "path",
                    ""
                )
            ).strip()

            if not path:
                continue

            if not self._is_allowed_file(path):
                continue

            size = int(
                item.get(
                    "size",
                    0
                )
                or 0
            )

            # Empty files and very large files are not useful
            # for a focused LLM review.
            if size <= 0 or size > 150_000:
                continue

            candidates.append({
                "path": path,
                "size": size,
                "sha": item.get("sha"),
                "priority": (
                    self._calculate_file_priority(
                        path=path,
                        size=size
                    )
                )
            })

        candidates.sort(
            key=lambda item: (
                item["priority"],
                -item["size"]
            ),
            reverse=True
        )

        return candidates[:self.max_files]

    def _is_allowed_file(
        self,
        path: str
    ) -> bool:
        normalized_path = (
            path.replace("\\", "/").lower()
        )

        path_parts = normalized_path.split("/")
        filename = path_parts[-1]

        if filename in self.EXCLUDED_FILENAMES:
            return False

        if any(
            directory in self.EXCLUDED_DIRECTORIES
            for directory in path_parts[:-1]
        ):
            return False

        if any(
            normalized_path.endswith(pattern)
            for pattern in self.GENERATED_FILE_PATTERNS
        ):
            return False

        if filename in self.IMPORTANT_FILENAMES:
            return True

        extension = self._get_extension(
            filename
        )

        return extension in self.SUPPORTED_EXTENSIONS

    def _calculate_file_priority(
        self,
        path: str,
        size: int
    ) -> float:
        normalized = (
            path.replace("\\", "/").lower()
        )

        filename = normalized.split("/")[-1]
        score = 0.0

        if filename in self.IMPORTANT_FILENAMES:
            score += 80

        important_terms = {
            "main": 30,
            "app": 30,
            "server": 30,
            "router": 25,
            "route": 25,
            "service": 25,
            "controller": 25,
            "model": 20,
            "schema": 20,
            "auth": 25,
            "security": 25,
            "database": 20,
            "repository": 15,
            "middleware": 15,
            "config": 15
        }

        for term, points in important_terms.items():
            if term in normalized:
                score += points

        preferred_directories = {
            "src",
            "app",
            "backend",
            "frontend",
            "services",
            "routers",
            "controllers",
            "models"
        }

        if any(
            directory in normalized.split("/")
            for directory in preferred_directories
        ):
            score += 20

        extension = self._get_extension(
            filename
        )

        extension_priority = {
            ".py": 25,
            ".java": 25,
            ".ts": 24,
            ".tsx": 23,
            ".js": 22,
            ".jsx": 21,
            ".go": 24,
            ".rs": 24,
            ".cs": 23,
            ".php": 20,
            ".cpp": 20,
            ".sql": 18,
            ".html": 12,
            ".css": 8
        }

        score += extension_priority.get(
            extension,
            10
        )

        # Prefer meaningful files, but do not heavily reward
        # extremely large files.
        if 500 <= size <= 20_000:
            score += 15

        elif 20_000 < size <= 60_000:
            score += 8

        return score

    async def _fetch_selected_files(
        self,
        owner: str,
        repository_name: str,
        branch: str,
        selected_files: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        tasks = [
            self._fetch_file_content(
                owner=owner,
                repository_name=repository_name,
                branch=branch,
                path=file_data["path"]
            )
            for file_data in selected_files
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        source_files = []
        total_characters = 0

        for selected_file, result in zip(
            selected_files,
            results
        ):
            if isinstance(result, Exception):
                logger.warning(
                    "Could not fetch %s: %s",
                    selected_file["path"],
                    result
                )
                continue

            content = result.strip()

            if not content:
                continue

            remaining_characters = (
                self.max_total_chars
                - total_characters
            )

            if remaining_characters <= 0:
                break

            allowed_characters = min(
                self.max_chars_per_file,
                remaining_characters
            )

            truncated = (
                len(content) > allowed_characters
            )

            content = content[
                :allowed_characters
            ]

            source_files.append({
                "path": selected_file["path"],
                "language": (
                    self._detect_language(
                        selected_file["path"]
                    )
                ),
                "content": content,
                "original_size": selected_file[
                    "size"
                ],
                "truncated": truncated
            })

            total_characters += len(content)

        return source_files

    async def _fetch_file_content(
        self,
        owner: str,
        repository_name: str,
        branch: str,
        path: str
    ) -> str:
        response = await self.github_client.get(
            f"/repos/{owner}/{repository_name}"
            f"/contents/{path}",
            params={
                "ref": branch
            }
        )

        if not isinstance(response, dict):
            return ""

        if response.get("type") != "file":
            return ""

        encoded_content = response.get(
            "content",
            ""
        )

        encoding = response.get(
            "encoding"
        )

        if (
            not encoded_content
            or encoding != "base64"
        ):
            return ""

        try:
            return (
                base64.b64decode(
                    encoded_content
                )
                .decode(
                    "utf-8",
                    errors="replace"
                )
            )

        except (
            ValueError,
            TypeError
        ):
            return ""

    def _build_code_context(
        self,
        source_files: list[dict[str, Any]]
    ) -> str:
        sections = []

        for file_data in source_files:
            sections.append(
                "\n".join([
                    (
                        "===== FILE: "
                        f"{file_data['path']} ====="
                    ),
                    (
                        "Language: "
                        f"{file_data['language']}"
                    ),
                    file_data["content"],
                    (
                        "===== END FILE: "
                        f"{file_data['path']} ====="
                    )
                ])
            )

        return "\n\n".join(sections)

    def _request_ai_review(
        self,
        repository: dict[str, Any],
        source_files: list[dict[str, Any]],
        code_context: str
    ) -> dict[str, Any]:
        prompt = self._build_review_prompt(
            repository=repository,
            source_files=source_files,
            code_context=code_context
        )

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior software engineer "
                            "performing fair, evidence-based code "
                            "reviews for student portfolios. "
                            "Review only the provided code. Do not "
                            "invent missing files, tests, features "
                            "or vulnerabilities. Return valid JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={
                    "type": "json_object"
                }
            )

            content = (
                completion
                .choices[0]
                .message
                .content
            )

            if not content:
                return self._fallback_review(
                    reason=(
                        "The AI reviewer returned "
                        "an empty response."
                    )
                )

            parsed_response = self._parse_json_response(
                content
            )

            return self._normalize_ai_review(
                parsed_response
            )

        except Exception as error:
            logger.exception(
                "Groq code review failed for %s",
                repository.get("full_name")
            )

            return self._fallback_review(
                reason=str(error)
            )

    def _build_review_prompt(
        self,
        repository: dict[str, Any],
        source_files: list[dict[str, Any]],
        code_context: str
    ) -> str:
        file_paths = [
            file_data["path"]
            for file_data in source_files
        ]

        return f"""
Review the following student GitHub repository.

Repository information:

Name: {repository.get("full_name")}
Description: {repository.get("description")}
Primary language: {repository.get("language")}
Files included in this review:
{json.dumps(file_paths, indent=2)}

Important evaluation rules:

1. Evaluate only the code included below.
2. Do not assume that unprovided files do or do not exist.
3. Missing evidence must be described as "not observed in
   the analyzed files", not as a confirmed project-wide issue.
4. Scores must be integers from 0 to 100.
5. Findings must be specific and connected to the provided code.
6. Do not reward code merely for being long.
7. Do not punish beginner-level projects for not using unnecessary
   advanced design patterns.
8. Security findings must not be invented.
9. Keep each list concise, with at most 6 items.
10. The overall_code_quality_score should reflect the weighted
    quality of the analyzed source code.

Evaluation categories:

- readability_score:
  Formatting, clarity, naming and understandable control flow.

- architecture_score:
  Separation of concerns, module organization, dependencies
  and responsibility boundaries visible in the analyzed files.

- maintainability_score:
  Reusability, modularity, duplication, coupling and ease of change.

- error_handling_score:
  Validation, exception handling, failure states and safe recovery.

- security_score:
  Secrets handling, authentication practices, input handling,
  authorization and obvious security risks visible in the code.

- api_design_score:
  Endpoint design, schemas, status handling and consistency.
  When no API code is provided, return null.

- database_quality_score:
  ORM usage, transactions, queries and database separation.
  When no database code is provided, return null.

- overall_code_quality_score:
  Overall quality from the supplied evidence.

Return this exact JSON structure:

{{
  "overall_code_quality_score": 0,
  "readability_score": 0,
  "architecture_score": 0,
  "maintainability_score": 0,
  "error_handling_score": 0,
  "security_score": 0,
  "api_design_score": null,
  "database_quality_score": null,
  "performance_level": "Weak",
  "summary": "Short evidence-based summary.",
  "strong_points": [
    "Specific strength"
  ],
  "weak_points": [
    "Specific weakness"
  ],
  "security_findings": [
    {{
      "severity": "low",
      "file": "path/to/file.py",
      "issue": "Finding",
      "recommendation": "Correction"
    }}
  ],
  "file_reviews": [
    {{
      "path": "path/to/file.py",
      "score": 0,
      "observations": [
        "Specific observation"
      ]
    }}
  ],
  "recommendations": [
    {{
      "priority": "high",
      "title": "Recommendation title",
      "details": "Actionable explanation"
    }}
  ],
  "review_limitations": [
    "Only selected files were analyzed."
  ]
}}

Valid performance levels:

- Excellent: 85 to 100
- Good: 70 to 84
- Average: 55 to 69
- Needs Improvement: 40 to 54
- Weak: below 40

Source code:

{code_context}
"""

    def _normalize_ai_review(
        self,
        review: dict[str, Any]
    ) -> dict[str, Any]:
        score_fields = [
            "overall_code_quality_score",
            "readability_score",
            "architecture_score",
            "maintainability_score",
            "error_handling_score",
            "security_score"
        ]

        normalized = dict(review)

        for field in score_fields:
            normalized[field] = (
                self._normalize_score(
                    normalized.get(field)
                )
            )

        optional_score_fields = [
            "api_design_score",
            "database_quality_score"
        ]

        for field in optional_score_fields:
            value = normalized.get(field)

            normalized[field] = (
                None
                if value is None
                else self._normalize_score(value)
            )

        overall_score = normalized[
            "overall_code_quality_score"
        ]

        normalized["performance_level"] = (
            self._get_performance_level(
                overall_score
            )
        )

        normalized["summary"] = str(
            normalized.get(
                "summary",
                "No summary was generated."
            )
        ).strip()

        normalized["strong_points"] = (
            self._normalize_string_list(
                normalized.get(
                    "strong_points"
                )
            )
        )

        normalized["weak_points"] = (
            self._normalize_string_list(
                normalized.get(
                    "weak_points"
                )
            )
        )

        normalized["security_findings"] = (
            self._normalize_object_list(
                normalized.get(
                    "security_findings"
                )
            )
        )

        normalized["file_reviews"] = (
            self._normalize_object_list(
                normalized.get(
                    "file_reviews"
                )
            )
        )

        normalized["recommendations"] = (
            self._normalize_object_list(
                normalized.get(
                    "recommendations"
                )
            )
        )

        limitations = self._normalize_string_list(
            normalized.get(
                "review_limitations"
            )
        )

        standard_limitation = (
            "The review covers selected source files, "
            "not the complete repository."
        )

        if standard_limitation not in limitations:
            limitations.append(
                standard_limitation
            )

        normalized["review_limitations"] = (
            limitations
        )

        normalized["review_source"] = (
            "groq_ai"
        )

        return normalized

    def _build_student_code_summary(
        self,
        repository_reviews: list[dict[str, Any]]
    ) -> dict[str, Any]:
        valid_reviews = []

        for repository_review in repository_reviews:
            code_review = repository_review.get(
                "code_review",
                {}
            )

            if code_review.get(
                "review_source"
            ) != "groq_ai":
                continue

            valid_reviews.append(
                repository_review
            )

        if not valid_reviews:
            return {
                "average_code_quality_score": 0.0,
                "performance_level": "Weak",
                "strongest_code_repository": None,
                "repositories_with_ai_review": 0,
                "summary": (
                    "No repository received a "
                    "successful AI code review."
                )
            }

        scores = [
            float(
                review["code_review"].get(
                    "overall_code_quality_score",
                    0
                )
            )
            for review in valid_reviews
        ]

        average_score = round(
            mean(scores),
            2
        )

        strongest = max(
            valid_reviews,
            key=lambda review: (
                review["code_review"].get(
                    "overall_code_quality_score",
                    0
                )
            )
        )

        return {
            "average_code_quality_score": (
                average_score
            ),
            "performance_level": (
                self._get_performance_level(
                    average_score
                )
            ),
            "strongest_code_repository": {
                "name": strongest[
                    "repository"
                ].get("name"),
                "html_url": strongest[
                    "repository"
                ].get("html_url"),
                "code_quality_score": (
                    strongest[
                        "code_review"
                    ].get(
                        "overall_code_quality_score",
                        0
                    )
                )
            },
            "repositories_with_ai_review": len(
                valid_reviews
            ),
            "summary": (
                f"{len(valid_reviews)} repositories "
                f"received AI code reviews with an "
                f"average score of {average_score}."
            )
        }

    def _build_no_code_response(
        self,
        repository: dict[str, Any],
        branch: str
    ) -> dict[str, Any]:
        return {
            "repository": {
                "name": repository.get("name"),
                "full_name": repository.get(
                    "full_name"
                ),
                "html_url": repository.get(
                    "html_url"
                ),
                "description": repository.get(
                    "description"
                ),
                "primary_language": repository.get(
                    "language"
                ),
                "default_branch": branch
            },
            "files_discovered": 0,
            "files_selected": 0,
            "analyzed_files": [],
            "code_review": self._fallback_review(
                reason=(
                    "No supported source-code files "
                    "were available for analysis."
                )
            )
        }

    def _fallback_review(
        self,
        reason: str
    ) -> dict[str, Any]:
        return {
            "overall_code_quality_score": 0.0,
            "readability_score": 0.0,
            "architecture_score": 0.0,
            "maintainability_score": 0.0,
            "error_handling_score": 0.0,
            "security_score": 0.0,
            "api_design_score": None,
            "database_quality_score": None,
            "performance_level": "Not Reviewed",
            "summary": (
                "The AI code review could not be completed."
            ),
            "strong_points": [],
            "weak_points": [],
            "security_findings": [],
            "file_reviews": [],
            "recommendations": [],
            "review_limitations": [
                reason
            ],
            "review_source": "fallback"
        }

    @staticmethod
    def _parse_json_response(
        content: str
    ) -> dict[str, Any]:
        cleaned_content = content.strip()

        cleaned_content = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned_content,
            flags=re.IGNORECASE
        )

        cleaned_content = re.sub(
            r"\s*```$",
            "",
            cleaned_content
        )

        parsed = json.loads(
            cleaned_content
        )

        if not isinstance(parsed, dict):
            raise ValueError(
                "AI review response must be a JSON object."
            )

        return parsed

    @staticmethod
    def _clean_value(
        value: str,
        field_name: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        return cleaned_value

    @staticmethod
    def _get_extension(
        filename: str
    ) -> str:
        lowercase_filename = filename.lower()

        for extension in sorted(
            GitHubCodeReviewer.SUPPORTED_EXTENSIONS,
            key=len,
            reverse=True
        ):
            if lowercase_filename.endswith(
                extension
            ):
                return extension

        return ""

    @staticmethod
    def _detect_language(
        path: str
    ) -> str:
        extension = (
            GitHubCodeReviewer._get_extension(
                path
            )
        )

        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript JSX",
            ".ts": "TypeScript",
            ".tsx": "TypeScript TSX",
            ".java": "Java",
            ".kt": "Kotlin",
            ".kts": "Kotlin",
            ".cpp": "C++",
            ".cc": "C++",
            ".cxx": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".hpp": "C++ Header",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".dart": "Dart",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".vue": "Vue"
        }

        return language_map.get(
            extension,
            "Unknown"
        )

    @staticmethod
    def _normalize_score(
        value: Any
    ) -> float:
        try:
            score = float(value)

        except (
            TypeError,
            ValueError
        ):
            score = 0.0

        return round(
            max(
                0.0,
                min(
                    score,
                    GitHubCodeReviewer.MAX_SCORE
                )
            ),
            2
        )

    @staticmethod
    def _normalize_string_list(
        value: Any
    ) -> list[str]:
        if not isinstance(value, list):
            return []

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ][:6]

    @staticmethod
    def _normalize_object_list(
        value: Any
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        return [
            item
            for item in value
            if isinstance(item, dict)
        ][:10]

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