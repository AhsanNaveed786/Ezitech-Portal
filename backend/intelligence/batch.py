from sqlalchemy.orm import Session

from backend.services.ai import (
    get_batch_comparison_report
)

from backend.intelligence.common import (
    build_intelligence_response,
    calculate_confidence_score
)


def get_strongest_batch(
    question: str,
    db: Session
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=1 if batches else 0
    )

    if not batches:
        answer = (
            "No batch performance data is currently available."
        )
        data = None

    else:
        strongest_batch_name = report[
            "strongest_batch"
        ]

        data = next(
            (
                batch
                for batch in batches
                if batch["batch"] == strongest_batch_name
            ),
            batches[0]
        )

        answer = (
            f"{data['batch']} is currently the strongest batch "
            f"with an average engineering score of "
            f"{data['average_engineering_score']}, "
            f"an attendance rate of "
            f"{data['average_attendance']}%, and "
            f"{data['approved_projects']} approved projects."
        )

    return build_intelligence_response(
        question=question,
        intent="strongest_batch",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_weakest_batch(
    question: str,
    db: Session
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=1 if batches else 0
    )

    if not batches:
        answer = (
            "No batch performance data is currently available."
        )
        data = None

    else:
        weakest_batch_name = report[
            "weakest_batch"
        ]

        data = next(
            (
                batch
                for batch in batches
                if batch["batch"] == weakest_batch_name
            ),
            batches[-1]
        )

        answer = (
            f"{data['batch']} currently has the weakest "
            f"overall performance with an average engineering "
            f"score of {data['average_engineering_score']} "
            f"and attendance of {data['average_attendance']}%."
        )

    return build_intelligence_response(
        question=question,
        intent="weakest_batch",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_batch_rankings(
    question: str,
    db: Session,
    limit: int = 10
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    ranked_batches = []

    for index, batch in enumerate(
        batches[:limit],
        start=1
    ):
        ranked_batches.append({
            "rank": index,
            **batch
        })

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=len(ranked_batches)
    )

    if not ranked_batches:
        answer = (
            "No batch ranking data is currently available."
        )

    else:
        answer = (
            f"{len(ranked_batches)} batches were ranked using "
            f"engineering score, project approval performance "
            f"and attendance."
        )

    return build_intelligence_response(
        question=question,
        intent="batch_rankings",
        answer=answer,
        data=ranked_batches,
        confidence_score=confidence_score
    )


def get_highest_attendance_batch(
    question: str,
    db: Session
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=1 if batches else 0
    )

    if not batches:
        answer = (
            "No batch attendance data is currently available."
        )
        data = None

    else:
        batch_name = report[
            "highest_attendance_batch"
        ]

        data = next(
            (
                batch
                for batch in batches
                if batch["batch"] == batch_name
            ),
            None
        )

        if data:
            answer = (
                f"{data['batch']} currently has the highest "
                f"average attendance at "
                f"{data['average_attendance']}%."
            )
        else:
            answer = (
                "The highest-attendance batch could not be identified."
            )

    return build_intelligence_response(
        question=question,
        intent="highest_attendance_batch",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_highest_project_batch(
    question: str,
    db: Session
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=1 if batches else 0
    )

    if not batches:
        answer = (
            "No batch project performance data is available."
        )
        data = None

    else:
        batch_name = report[
            "highest_project_batch"
        ]

        data = next(
            (
                batch
                for batch in batches
                if batch["batch"] == batch_name
            ),
            None
        )

        if data:
            answer = (
                f"{data['batch']} currently has the strongest "
                f"project completion performance with "
                f"{data['approved_projects']} approved projects "
                f"and an approval rate of "
                f"{data['project_approval_percentage']}%."
            )
        else:
            answer = (
                "The highest-performing project batch "
                "could not be identified."
            )

    return build_intelligence_response(
        question=question,
        intent="highest_project_batch",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_highest_placement_batch(
    question: str,
    db: Session
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=1 if batches else 0
    )

    if not batches:
        answer = (
            "No batch placement-readiness data is available."
        )
        data = None

    else:
        batch_name = report[
            "highest_placement_batch"
        ]

        data = next(
            (
                batch
                for batch in batches
                if batch["batch"] == batch_name
            ),
            None
        )

        if data:
            answer = (
                f"{data['batch']} currently has the highest "
                f"placement readiness, with "
                f"{data['placement_ready_students']} students "
                f"meeting the placement criteria."
            )
        else:
            answer = (
                "The batch with the highest placement "
                "readiness could not be identified."
            )

    return build_intelligence_response(
        question=question,
        intent="highest_placement_batch",
        answer=answer,
        data=data,
        confidence_score=confidence_score
    )


def get_batches_needing_support(
    question: str,
    db: Session,
    limit: int = 10
):
    report = get_batch_comparison_report(
        db=db
    )

    batches = report["batches"]

    support_batches = [
        {
            **batch,
            "recommended_action": (
                "Schedule focused mentor sessions and "
                "targeted technical workshops."
            )
        }
        for batch in batches
        if (
            batch["average_engineering_score"] < 60
            or batch["average_attendance"] < 70
            or batch["students_requiring_attention"] > 0
        )
    ]

    support_batches.sort(
        key=lambda item: (
            item["average_engineering_score"],
            item["average_attendance"],
            -item["students_requiring_attention"]
        )
    )

    support_batches = support_batches[:limit]

    confidence_score = calculate_confidence_score(
        total_records=len(batches),
        matched_records=len(support_batches)
    )

    if not support_batches:
        answer = (
            "No batches currently meet the additional-support criteria."
        )

    else:
        answer = (
            f"{len(support_batches)} batches currently require "
            f"additional mentor or technical support."
        )

    return build_intelligence_response(
        question=question,
        intent="batches_needing_support",
        answer=answer,
        data=support_batches,
        confidence_score=confidence_score
    )