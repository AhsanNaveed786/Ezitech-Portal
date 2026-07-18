from typing import Any


def build_intelligence_response(
    question: str,
    intent: str,
    answer: str,
    data: Any = None,
    confidence_score: float = 0.0
):
    return {
        "question": question,
        "intent": intent,
        "answer": answer,
        "confidence_score": round(
            max(0.0, min(100.0, confidence_score)),
            2
        ),
        "data": data
    }


def calculate_confidence_score(
    total_records: int,
    matched_records: int,
    data_quality_score: float = 100.0
):
    if total_records <= 0:
        return 0.0

    coverage_score = (
        matched_records / total_records
    ) * 100

    confidence_score = (
        coverage_score * 0.60
        + data_quality_score * 0.40
    )

    return round(
        max(0.0, min(100.0, confidence_score)),
        2
    )


def normalize_question(
    question: str
):
    return " ".join(
        question.lower().strip().split()
    )


def contains_any_keyword(
    question: str,
    keywords: list[str]
):
    normalized_question = normalize_question(
        question
    )

    return any(
        keyword.lower() in normalized_question
        for keyword in keywords
    )


def get_performance_level(
    engineering_score: float
):
    if engineering_score >= 85:
        return "Excellent"

    if engineering_score >= 70:
        return "Good"

    if engineering_score >= 55:
        return "Average"

    return "Needs Improvement"


def safe_percentage(
    part: int | float,
    total: int | float
):
    if total <= 0:
        return 0.0

    return round(
        (part / total) * 100,
        2
    )