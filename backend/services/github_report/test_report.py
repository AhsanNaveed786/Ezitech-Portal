import asyncio
from pprint import pprint

from backend.services.github_report import (
    GitHubCodeReviewer,
    GitHubDataCollector,
    GitHubRepositoryAnalyzer
)


async def main():
    username = "AhsanNaveed786"

    collector = GitHubDataCollector()
    analyzer = GitHubRepositoryAnalyzer()
    code_reviewer = GitHubCodeReviewer(
        max_files=8,
        max_chars_per_file=7000,
        max_total_chars=35000
    )

    github_data = (
        await collector.collect_student_github_data(
            username=username,
            repository_limit=5,
            commit_limit=30
        )
    )

    rules_report = analyzer.analyze_student_data(
        collected_data=github_data
    )

    ai_code_report = (
        await code_reviewer.review_student_repositories(
            username=username,
            repositories=github_data["repositories"],
            repository_limit=2
        )
    )

    print("\nRULES-BASED GITHUB REPORT\n")
    pprint(rules_report)

    print("\nAI CODE-QUALITY REPORT\n")
    pprint(ai_code_report)


if __name__ == "__main__":
    asyncio.run(main())