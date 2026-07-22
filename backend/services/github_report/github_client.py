import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from backend.services.github_report.exceptions import (
    GitHubAPIError,
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubRepositoryNotFoundError,
    GitHubUserNotFoundError
)


# Project root:
# Ezitech Portal/
BASE_DIR = Path(__file__).resolve().parents[3]

# Project root ki .env file load karega
load_dotenv(
    dotenv_path=BASE_DIR / ".env",
    override=True
)


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        timeout: float = 20.0
    ):
        loaded_token = (
            token
            or os.getenv("GITHUB_TOKEN")
        )

        self.token = (
            loaded_token.strip()
            if loaded_token
            else None
        )

        if not self.token:
            raise GitHubAuthenticationError(
                "GITHUB_TOKEN is missing. "
                "Add it to the project root .env file."
            )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "Ezitech-AI-Mentor-Platform"
        }

        self.timeout = httpx.Timeout(
            timeout=timeout,
            connect=10.0
        )

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None
    ) -> Any:
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(
                    url,
                    params=params
                )

        except httpx.TimeoutException as error:
            raise GitHubAPIError(
                "GitHub API request timed out."
            ) from error

        except httpx.RequestError as error:
            raise GitHubAPIError(
                "Could not connect to the GitHub API."
            ) from error

        self._handle_response_errors(
            response=response,
            endpoint=endpoint
        )

        try:
            return response.json()

        except ValueError as error:
            raise GitHubAPIError(
                "GitHub API returned an invalid JSON response."
            ) from error

    def _handle_response_errors(
        self,
        response: httpx.Response,
        endpoint: str
    ) -> None:
        if response.status_code < 400:
            return

        message = self._extract_error_message(
            response
        )

        if response.status_code == 401:
            raise GitHubAuthenticationError(
                "GitHub authentication failed. "
                "The token is invalid, expired, revoked, "
                "or Python loaded the wrong token."
            )

        if response.status_code == 403:
            remaining = response.headers.get(
                "x-ratelimit-remaining"
            )

            if remaining == "0":
                reset_time = response.headers.get(
                    "x-ratelimit-reset"
                )

                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. "
                    f"Reset timestamp: {reset_time}"
                )

            raise GitHubAuthenticationError(
                f"GitHub API access was forbidden: {message}"
            )

        if response.status_code == 404:
            if endpoint.startswith("/users/"):
                raise GitHubUserNotFoundError(
                    "GitHub user was not found."
                )

            if endpoint.startswith("/repos/"):
                raise GitHubRepositoryNotFoundError(
                    "GitHub repository or requested resource "
                    "was not found."
                )

        raise GitHubAPIError(
            f"GitHub API returned status "
            f"{response.status_code}: {message}"
        )

    @staticmethod
    def _extract_error_message(
        response: httpx.Response
    ) -> str:
        try:
            body = response.json()

            return str(
                body.get(
                    "message",
                    "Unknown GitHub API error"
                )
            )

        except ValueError:
            return (
                response.text
                or "Unknown GitHub API error"
            )