class GitHubServiceError(Exception):
    """Base exception for GitHub report services."""


class GitHubUserNotFoundError(GitHubServiceError):
    """Raised when a GitHub user does not exist."""


class GitHubRepositoryNotFoundError(GitHubServiceError):
    """Raised when a GitHub repository does not exist."""


class GitHubRateLimitError(GitHubServiceError):
    """Raised when the GitHub API rate limit is exceeded."""


class GitHubAuthenticationError(GitHubServiceError):
    """Raised when the GitHub token is invalid or unauthorized."""


class GitHubAPIError(GitHubServiceError):
    """Raised for unexpected GitHub API errors."""