from sqlalchemy.orm import Session

from backend.services.ai import (
    get_technology_performance_report
)

from backend.intelligence.common import (
    build_intelligence_response,
    calculate_confidence_score
)


def get_strongest_technology(
    question: str,
    db: Session
):
    report = get_technology_performance_report(
        db=db
    )

    technologies = report.get(
        "technologies",
        []
    )

    confidence_score = calculate_confidence_score(
        total_records=len(technologies),
        matched_records=1 if technologies else 0
    )

    if not technologies:
        answer = (
            "No technology performance data is available."
        )
        data = None

    else:
        data = max(
            technologies,
            key=lambda item: (
                item.get("approval_percentage", 0),
                item.get("approved_projects", 0),
                item.get("total_projects", 0)
            )
        )

        answer = (
            f"{data['technology']} is currently the strongest "
            f"technology with a project approval rate of "
            f"{data['approval_percentage']}%."
        )

    return build_intelligence_response(
        question=question,
        intent="strongest_technology",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_weakest_technology(
    question: str,
    db: Session
):
    report = get_technology_performance_report(
        db=db
    )

    technologies = report.get(
        "technologies",
        []
    )

    confidence_score = calculate_confidence_score(
        total_records=len(technologies),
        matched_records=1 if technologies else 0
    )

    if not technologies:
        answer = (
            "No technology performance data is available."
        )
        data = None

    else:
        data = min(
            technologies,
            key=lambda item: (
                item.get("approval_percentage", 0),
                item.get("approved_projects", 0),
                item.get("total_projects", 0)
            )
        )

        answer = (
            f"{data['technology']} currently has the "
            f"lowest project approval rate of "
            f"{data['approval_percentage']}%."
        )

    return build_intelligence_response(
        question=question,
        intent="weakest_technology",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_technology_rankings(
    question: str,
    db: Session
):
    report = get_technology_performance_report(
        db=db
    )

    technologies = report.get(
        "technologies",
        []
    )

    sorted_technologies = sorted(
        technologies,
        key=lambda item: (
            item.get("approval_percentage", 0),
            item.get("approved_projects", 0),
            item.get("total_projects", 0)
        ),
        reverse=True
    )

    rankings = []

    for index, technology in enumerate(
        sorted_technologies,
        start=1
    ):
        rankings.append({
            "rank": index,
            **technology
        })

    confidence_score = calculate_confidence_score(
        total_records=len(technologies),
        matched_records=len(rankings)
    )

    if not rankings:
        answer = (
            "No technology ranking data is available."
        )

    else:
        answer = (
            f"{len(rankings)} technologies were ranked "
            f"using project approval rate, approved projects "
            f"and total project volume."
        )

    return build_intelligence_response(
        question=question,
        intent="technology_rankings",
        answer=answer,
        data=rankings,
        confidence_score=confidence_score
    )


def get_highest_completion_technology(
    question: str,
    db: Session
):
    report = get_technology_performance_report(
        db=db
    )

    technologies = report.get(
        "technologies",
        []
    )

    confidence_score = calculate_confidence_score(
        total_records=len(technologies),
        matched_records=1 if technologies else 0
    )

    if not technologies:
        answer = (
            "No technology completion data is available."
        )
        data = None

    else:
        data = max(
            technologies,
            key=lambda item: (
                item.get("approved_projects", 0),
                item.get("approval_percentage", 0),
                item.get("total_projects", 0)
            )
        )

        answer = (
            f"{data['technology']} currently has the "
            f"highest project completion performance with "
            f"{data['approved_projects']} approved projects "
            f"and an approval rate of "
            f"{data['approval_percentage']}%."
        )

    return build_intelligence_response(
        question=question,
        intent="highest_completion_technology",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )