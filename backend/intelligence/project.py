from collections import defaultdict

from sqlalchemy.orm import Session

from backend.models import Project

from backend.intelligence.common import (
    build_intelligence_response,
    calculate_confidence_score
)


def analyze_projects(
    db: Session
):
    projects = db.query(Project).all()

    technology_stats = defaultdict(
        lambda: {
            "technology": "",
            "total_projects": 0,
            "approved_projects": 0,
            "pending_projects": 0,
            "rejected_projects": 0
        }
    )

    for project in projects:

        technologies = [
            tech.strip()
            for tech in project.tech_stack.split(",")
        ]

        for technology in technologies:

            stats = technology_stats[
                technology
            ]

            stats["technology"] = technology

            stats["total_projects"] += 1

            if project.status == "Approved":
                stats["approved_projects"] += 1

            elif project.status == "Rejected":
                stats["rejected_projects"] += 1

            else:
                stats["pending_projects"] += 1

    report = []

    for stats in technology_stats.values():

        approval_percentage = 0

        rejection_percentage = 0

        if stats["total_projects"] > 0:

            approval_percentage = (
                stats["approved_projects"]
                / stats["total_projects"]
            ) * 100

            rejection_percentage = (
                stats["rejected_projects"]
                / stats["total_projects"]
            ) * 100

        report.append({

            **stats,

            "project_approval_percentage":
                round(
                    approval_percentage,
                    2
                ),

            "project_rejection_percentage":
                round(
                    rejection_percentage,
                    2
                )

        })

    report.sort(

        key=lambda item: (
            item["project_approval_percentage"],
            item["approved_projects"]
        ),

        reverse=True

    )

    return report


def get_highest_success_projects(
    question: str,
    db: Session
):
    report = analyze_projects(db)

    confidence_score = calculate_confidence_score(
        len(report),
        1 if report else 0
    )

    if not report:

        answer = (
            "No project data is available."
        )

        data = None

    else:

        data = report[0]

        answer = (
            f"{data['technology']} currently has "
            f"the highest approval rate of "
            f"{data['project_approval_percentage']}%."
        )

    return build_intelligence_response(

        question=question,

        intent="highest_success_projects",

        answer=answer,

        data=data,

        confidence_score=confidence_score

    )


def get_highest_failure_projects(
    question: str,
    db: Session
):
    report = analyze_projects(db)

    report.sort(

        key=lambda item: (
            item["project_rejection_percentage"],
            item["rejected_projects"]
        ),

        reverse=True

    )

    confidence_score = calculate_confidence_score(
        len(report),
        1 if report else 0
    )

    if not report:

        answer = (
            "No project data is available."
        )

        data = None

    else:

        data = report[0]

        answer = (
            f"{data['technology']} currently has "
            f"the highest rejection rate of "
            f"{data['project_rejection_percentage']}%."
        )

    return build_intelligence_response(

        question=question,

        intent="highest_failure_projects",

        answer=answer,

        data=data,

        confidence_score=confidence_score

    )

def get_most_used_technology(
    question: str,
    db: Session
):
    report = analyze_projects(db)

    report.sort(

        key=lambda item: (
            item["total_projects"]
        ),

        reverse=True

    )

    confidence_score = calculate_confidence_score(
        len(report),
        1 if report else 0
    )

    if not report:

        answer = (
            "No project data is available."
        )

        data = None

    else:

        data = report[0]

        answer = (
            f"{data['technology']} is currently "
            f"the most frequently used technology "
            f"with {data['total_projects']} projects."
        )

    return build_intelligence_response(

        question=question,

        intent="most_used_technology",

        answer=answer,

        data=data,

        confidence_score=confidence_score

    )



def get_project_rankings(
    question: str,
    db: Session
):
    report = analyze_projects(db)

    rankings = []

    for index, item in enumerate(

        report,

        start=1

    ):

        rankings.append({

            "rank": index,

            **item

        })

    confidence_score = calculate_confidence_score(

        len(report),

        len(rankings)

    )

    return build_intelligence_response(

        question=question,

        intent="project_rankings",

        answer="Project technologies ranked successfully.",

        data=rankings,

        confidence_score=confidence_score

    )