import asyncio

from backend.services.github_report import (
    GitHubDataCollector,
    GitHubRepositoryAnalyzer
)


async def main():
    collector = GitHubDataCollector()
    analyzer = GitHubRepositoryAnalyzer()

    github_data = await collector.collect_student_github_data(
        username="student_username",
        repository_limit=5,
        commit_limit=30
    )

    report = analyzer.analyze_student_data(
        collected_data=github_data
    )

    print(report)


if __name__ == "__main__":
    asyncio.run(main())