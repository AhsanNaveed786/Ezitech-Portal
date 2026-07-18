import json
import logging
import os
import re
from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from backend.intelligence.batch import (
    get_batch_rankings,
    get_batches_needing_support,
    get_highest_attendance_batch,
    get_highest_placement_batch,
    get_highest_project_batch,
    get_strongest_batch,
    get_weakest_batch
)

from backend.intelligence.common import (
    build_intelligence_response,
    normalize_question
)

from backend.intelligence.mentor import (
    get_best_mentor,
    get_mentor_team_rankings,
    get_mentors_needing_support,
    get_weakest_mentor
)

from backend.intelligence.project import (
    get_highest_failure_projects,
    get_highest_success_projects,
    get_most_used_technology,
    get_project_rankings
)

from backend.intelligence.student import (
    get_interview_ready_students,
    get_job_ready_students,
    get_students_needing_mentoring,
    get_top_students,
    get_weak_students
)

from backend.intelligence.technology import (
    get_highest_completion_technology,
    get_strongest_technology,
    get_technology_rankings,
    get_weakest_technology
)

from utils.groq import client


logger = logging.getLogger(__name__)

INTELLIGENCE_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


SUPPORTED_INTENTS = {
    "top_students",
    "weak_students",
    "job_ready_students",
    "interview_ready_students",
    "students_needing_mentoring",

    "best_mentor",
    "weakest_mentor",
    "mentor_team_rankings",
    "mentors_needing_support",

    "strongest_technology",
    "weakest_technology",
    "technology_rankings",
    "highest_completion_technology",

    "strongest_batch",
    "weakest_batch",
    "batch_rankings",
    "highest_attendance_batch",
    "highest_project_batch",
    "highest_placement_batch",
    "batches_needing_support",

    "highest_success_projects",
    "highest_failure_projects",
    "most_used_technology",
    "project_rankings",

    "unsupported_query"
}


LIMIT_SUPPORTED_INTENTS = {
    "top_students",
    "weak_students",
    "job_ready_students",
    "interview_ready_students",
    "students_needing_mentoring",
    "mentor_team_rankings",
    "mentors_needing_support",
    "batch_rankings",
    "batches_needing_support"
}


INTENT_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "top_students": get_top_students,
    "weak_students": get_weak_students,
    "job_ready_students": get_job_ready_students,
    "interview_ready_students": get_interview_ready_students,
    "students_needing_mentoring":
        get_students_needing_mentoring,

    "best_mentor": get_best_mentor,
    "weakest_mentor": get_weakest_mentor,
    "mentor_team_rankings": get_mentor_team_rankings,
    "mentors_needing_support":
        get_mentors_needing_support,

    "strongest_technology": get_strongest_technology,
    "weakest_technology": get_weakest_technology,
    "technology_rankings": get_technology_rankings,
    "highest_completion_technology":
        get_highest_completion_technology,

    "strongest_batch": get_strongest_batch,
    "weakest_batch": get_weakest_batch,
    "batch_rankings": get_batch_rankings,
    "highest_attendance_batch":
        get_highest_attendance_batch,
    "highest_project_batch": get_highest_project_batch,
    "highest_placement_batch":
        get_highest_placement_batch,
    "batches_needing_support":
        get_batches_needing_support,

    "highest_success_projects":
        get_highest_success_projects,
    "highest_failure_projects":
        get_highest_failure_projects,
    "most_used_technology": get_most_used_technology,
    "project_rankings": get_project_rankings
}


def contains_phrase(
    question: str,
    phrases: list[str]
) -> bool:
    return any(
        phrase in question
        for phrase in phrases
    )


def extract_requested_limit(
    question: str,
    default_limit: int = 10
) -> int:
    patterns = [
        r"\btop\s+(\d{1,2})\b",
        r"\bfirst\s+(\d{1,2})\b",
        r"\bshow\s+(\d{1,2})\b",
        r"\blist\s+(\d{1,2})\b",
        r"\b(\d{1,2})\s+(?:students|interns|mentors|batches)\b"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            question,
            flags=re.IGNORECASE
        )

        if match:
            requested_limit = int(
                match.group(1)
            )

            return max(
                1,
                min(requested_limit, 50)
            )

    return default_limit


def classify_intent_with_rules(
    question: str
) -> str | None:
    normalized = normalize_question(question)

    mentions_student = contains_phrase(
        normalized,
        [
            "student",
            "students",
            "intern",
            "interns"
        ]
    )

    mentions_mentor = contains_phrase(
        normalized,
        [
            "mentor",
            "mentors",
            "mentor team"
        ]
    )

    mentions_batch = contains_phrase(
        normalized,
        [
            "batch",
            "batches"
        ]
    )

    mentions_technology = contains_phrase(
        normalized,
        [
            "technology",
            "technologies",
            "tech stack",
            "tech"
        ]
    )

    mentions_project = contains_phrase(
        normalized,
        [
            "project",
            "projects",
            "case study",
            "case studies"
        ]
    )

    # Student intelligence

    if mentions_student and contains_phrase(
        normalized,
        [
            "job ready",
            "ready for job",
            "ready for hiring",
            "hire ready",
            "hiring ready"
        ]
    ):
        return "job_ready_students"

    if mentions_student and contains_phrase(
        normalized,
        [
            "interview ready",
            "ready for interview",
            "recommend interview"
        ]
    ):
        return "interview_ready_students"

    if mentions_student and contains_phrase(
        normalized,
        [
            "need mentoring",
            "needs mentoring",
            "need mentor",
            "needs mentor",
            "mentor meeting",
            "require mentoring",
            "require support"
        ]
    ):
        return "students_needing_mentoring"

    if mentions_student and contains_phrase(
        normalized,
        [
            "weak",
            "weakest",
            "struggling",
            "low performing",
            "poor performing",
            "needs improvement"
        ]
    ):
        return "weak_students"

    if mentions_student and contains_phrase(
        normalized,
        [
            "top",
            "best",
            "strongest",
            "highest performing",
            "top performing"
        ]
    ):
        return "top_students"

    # Mentor intelligence

    if mentions_mentor and contains_phrase(
        normalized,
        [
            "ranking",
            "rankings",
            "rank all",
            "compare mentors"
        ]
    ):
        return "mentor_team_rankings"

    if mentions_mentor and contains_phrase(
        normalized,
        [
            "need support",
            "needs support",
            "require support",
            "requires support",
            "help required"
        ]
    ):
        return "mentors_needing_support"

    if mentions_mentor and contains_phrase(
        normalized,
        [
            "weak",
            "weakest",
            "lowest performing",
            "worst"
        ]
    ):
        return "weakest_mentor"

    if mentions_mentor and contains_phrase(
        normalized,
        [
            "best",
            "strongest",
            "highest performing",
            "top performing",
            "highest-performing"
        ]
    ):
        return "best_mentor"

    # Batch intelligence

    if mentions_batch and contains_phrase(
        normalized,
        [
            "highest attendance",
            "best attendance",
            "most attendance"
        ]
    ):
        return "highest_attendance_batch"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "highest project",
            "most approved projects",
            "best project performance",
            "highest completion"
        ]
    ):
        return "highest_project_batch"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "highest placement",
            "most placement ready",
            "placement readiness",
            "ready for hiring"
        ]
    ):
        return "highest_placement_batch"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "need support",
            "needs support",
            "require support",
            "requires support"
        ]
    ):
        return "batches_needing_support"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "ranking",
            "rankings",
            "compare batches",
            "rank all"
        ]
    ):
        return "batch_rankings"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "weak",
            "weakest",
            "worst",
            "lowest performing"
        ]
    ):
        return "weakest_batch"

    if mentions_batch and contains_phrase(
        normalized,
        [
            "best",
            "strongest",
            "top",
            "highest performing"
        ]
    ):
        return "strongest_batch"

    # Technology and project intelligence

    if (
        mentions_technology or mentions_project
    ) and contains_phrase(
        normalized,
        [
            "highest failure",
            "highest rejection",
            "most rejected",
            "failure rate",
            "rejection rate",
            "fails most"
        ]
    ):
        return "highest_failure_projects"

    if (
        mentions_technology or mentions_project
    ) and contains_phrase(
        normalized,
        [
            "highest success",
            "highest approval",
            "most successful",
            "success rate",
            "approval rate"
        ]
    ):
        return "highest_success_projects"

    if contains_phrase(
        normalized,
        [
            "most used technology",
            "most popular technology",
            "most common technology",
            "frequently used technology"
        ]
    ):
        return "most_used_technology"

    if mentions_technology and contains_phrase(
        normalized,
        [
            "highest completion",
            "highest completion rate",
            "most completed",
            "most approved projects"
        ]
    ):
        return "highest_completion_technology"

    if mentions_technology and contains_phrase(
        normalized,
        [
            "ranking",
            "rankings",
            "rank technologies",
            "compare technologies"
        ]
    ):
        return "technology_rankings"

    if mentions_technology and contains_phrase(
        normalized,
        [
            "weak",
            "weakest",
            "worst",
            "lowest performing",
            "underperforming"
        ]
    ):
        return "weakest_technology"

    if mentions_technology and contains_phrase(
        normalized,
        [
            "best",
            "strongest",
            "top",
            "highest performing"
        ]
    ):
        return "strongest_technology"

    if mentions_project and contains_phrase(
        normalized,
        [
            "ranking",
            "rankings",
            "compare projects",
            "rank projects"
        ]
    ):
        return "project_rankings"

    return None


def classify_intent_with_ai(
    question: str
) -> tuple[str, float]:
    allowed_intents = sorted(
        SUPPORTED_INTENTS
    )

    prompt = f"""
You are an intent classifier for an internship engineering
intelligence platform.

Classify the user's question into exactly one supported intent.

Supported intents:

{json.dumps(allowed_intents, indent=2)}

Intent meanings:

- top_students: highest-performing students or interns
- weak_students: weak or struggling students
- job_ready_students: students ready for hiring or jobs
- interview_ready_students: students ready for interviews
- students_needing_mentoring: students needing mentor support

- best_mentor: mentor with the strongest team
- weakest_mentor: mentor with the weakest team
- mentor_team_rankings: ranking or comparison of mentors
- mentors_needing_support: mentors requiring support

- strongest_technology: best-performing technology
- weakest_technology: weakest or underperforming technology
- technology_rankings: rank technologies
- highest_completion_technology: technology with most approved projects

- strongest_batch: best-performing batch
- weakest_batch: weakest batch
- batch_rankings: ranking or comparison of batches
- highest_attendance_batch: batch with highest attendance
- highest_project_batch: batch with best project results
- highest_placement_batch: batch with most placement-ready students
- batches_needing_support: batches requiring support

- highest_success_projects: highest project approval or success rate
- highest_failure_projects: highest project rejection or failure rate
- most_used_technology: most frequently used project technology
- project_rankings: project or project-technology rankings

- unsupported_query: question cannot be answered by available
  internship analytics functions

User question:

{question}

Rules:

- Return one intent only.
- Do not invent a new intent.
- Use unsupported_query when the question requires unavailable
  information, prediction, historical growth, GitHub data,
  communication data or document knowledge.
- Confidence must be between 0 and 100.
- Return valid JSON only.
- Do not include markdown.

Required JSON format:

{{
    "intent": "supported_intent",
    "confidence": 90
}}
"""

    try:
        completion = client.chat.completions.create(
            model=INTELLIGENCE_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ],

            temperature=0,

            response_format={
                "type": "json_object"
            }
        )

        content = (
            completion.choices[0]
            .message.content
        )

        if not content:
            return "unsupported_query", 0.0

        result = json.loads(content)

        intent = result.get(
            "intent",
            "unsupported_query"
        )

        confidence = float(
            result.get("confidence", 0)
        )

        if intent not in SUPPORTED_INTENTS:
            intent = "unsupported_query"

        confidence = max(
            0.0,
            min(confidence, 100.0)
        )

        return intent, confidence

    except Exception:
        logger.exception(
            "AI intent classification failed."
        )

        return "unsupported_query", 0.0


def build_unsupported_response(
    question: str
):
    return build_intelligence_response(
        question=question,
        intent="unsupported_query",
        answer=(
            "This question cannot currently be answered using "
            "the available internship analytics. You can ask "
            "about students, mentors, batches, technologies, "
            "project performance, interviews or job readiness."
        ),
        data={
            "supported_examples": [
                "Show me the top 10 interns.",
                "Which students are ready for jobs?",
                "Which mentor has the strongest team?",
                "Which technology is underperforming?",
                "Which batch has the highest attendance?",
                "Which project technology has the highest rejection rate?"
            ]
        },
        confidence_score=0.0
    )


def execute_intelligence_intent(
    intent: str,
    question: str,
    db: Session,
    limit: int
):
    handler = INTENT_HANDLERS.get(intent)

    if not handler:
        return build_unsupported_response(
            question=question
        )

    if intent in LIMIT_SUPPORTED_INTENTS:
        return handler(
            question=question,
            db=db,
            limit=limit
        )

    return handler(
        question=question,
        db=db
    )


def route_intelligence_query(
    question: str,
    db: Session,
    default_limit: int = 10
):
    if not question or not question.strip():
        return build_intelligence_response(
            question="",
            intent="invalid_question",
            answer="Question cannot be empty.",
            data=None,
            confidence_score=0.0
        )

    cleaned_question = question.strip()

    if len(cleaned_question) > 500:
        return build_intelligence_response(
            question=cleaned_question,
            intent="invalid_question",
            answer=(
                "Question is too long. Please keep it "
                "under 500 characters."
            ),
            data=None,
            confidence_score=0.0
        )

    limit = extract_requested_limit(
        question=cleaned_question,
        default_limit=default_limit
    )

    intent = classify_intent_with_rules(
        question=cleaned_question
    )

    routing_method = "keyword_rules"

    if intent is None:
        intent, ai_confidence = (
            classify_intent_with_ai(
                question=cleaned_question
            )
        )

        routing_method = "ai_classifier"

        if (
            intent == "unsupported_query"
            or ai_confidence < 50
        ):
            return build_unsupported_response(
                question=cleaned_question
            )

    try:
        result = execute_intelligence_intent(
            intent=intent,
            question=cleaned_question,
            db=db,
            limit=limit
        )

        if isinstance(result, dict):
            result["routing_method"] = (
                routing_method
            )

        return result

    except Exception:
        logger.exception(
            "Intelligence query execution failed. Intent: %s",
            intent
        )

        return build_intelligence_response(
            question=cleaned_question,
            intent="intelligence_error",
            answer=(
                "The intelligence engine could not process "
                "this question because the required analytics "
                "function encountered an error."
            ),
            data=None,
            confidence_score=0.0
        )