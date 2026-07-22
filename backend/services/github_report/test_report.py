import asyncio
from pprint import pprint

from backend.services.github_report import (
    GitHubCodeReviewer,
    GitHubDataCollector,
    GitHubFinalReportBuilder,
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
    final_report_builder = GitHubFinalReportBuilder()

    print("\nCollecting GitHub data...\n")

    github_data = (
        await collector.collect_student_github_data(
            username=username,
            repository_limit=5,
            commit_limit=30
        )
    )

    print("Generating rules-based report...\n")

    rules_report = analyzer.analyze_student_data(
        collected_data=github_data
    )

    print("Generating AI code-quality report...\n")

    ai_code_report = (
        await code_reviewer.review_student_repositories(
            username=username,
            repositories=github_data.get(
                "repositories",
                []
            ),
            repository_limit=2
        )
    )

    print("Combining final GitHub report...\n")

    final_report = final_report_builder.build_report(
        rules_report=rules_report,
        ai_code_report=ai_code_report
    )

    print("\n" + "=" * 70)
    print("RULES-BASED GITHUB REPORT")
    print("=" * 70 + "\n")

    pprint(
        rules_report,
        sort_dicts=False
    )

    print("\n" + "=" * 70)
    print("AI CODE-QUALITY REPORT")
    print("=" * 70 + "\n")

    pprint(
        ai_code_report,
        sort_dicts=False
    )

    print("\n" + "=" * 70)
    print("FINAL STUDENT GITHUB REPORT")
    print("=" * 70 + "\n")

    pprint(
        final_report,
        sort_dicts=False
    )

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    scores = final_report.get(
        "scores",
        {}
    )

    best_repository = final_report.get(
        "best_repository"
    )

    print(
        f"Username: "
        f"{final_report.get('username')}"
    )

    print(
        f"Assessment status: "
        f"{final_report.get('assessment_status')}"
    )

    print(
        f"Final GitHub score: "
        f"{scores.get('final_github_score', 0)}"
    )

    print(
        f"Performance level: "
        f"{final_report.get('performance_level')}"
    )

    print(
        f"Repositories analyzed: "
        f"{final_report.get('repositories_analyzed', 0)}"
    )

    print(
        f"Repositories reviewed by AI: "
        f"{final_report.get('repositories_with_ai_review', 0)}"
    )

    if best_repository:
        print(
            f"Best repository: "
            f"{best_repository.get('name')}"
        )

        print(
            f"Best repository score: "
            f"{best_repository.get('final_repository_score')}"
        )

    print(
        f"\nSummary: "
        f"{final_report.get('summary')}"
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nGitHub report generation cancelled.")

    except Exception as error:
        print(
            "\nGitHub report generation failed:"
        )
        print(
            f"{type(error).__name__}: {error}"
        )