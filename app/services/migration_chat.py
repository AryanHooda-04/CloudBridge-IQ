"""Conversational migration assistant grounded in an assessment result."""

from __future__ import annotations

import json
from typing import Any

from app.config import get_settings
from app.schemas import (
    AnalyzeMigrationResponse,
    MigrationAgentChatRequest,
    MigrationAgentChatResponse,
)
from app.services.llm_factory import build_chat_openai


SYSTEM_PROMPT = """You are CloudBridge IQ's migration assessment agent.

You answer questions about the uploaded architecture assessment, target architecture,
service mappings, migration flow, risks, cost/effort signals, and decision gates.

Rules:
- Ground answers in the supplied assessment context.
- If the context is missing or uncertain, say what is unknown and what should be validated.
- Be concise, practical, and architecture-review oriented.
- Do not invent cloud services, costs, or dependencies that are not supported by the context.
- Explain tradeoffs and next actions when useful.
- Use short Markdown bullets for multi-part answers.
"""


async def answer_migration_question(
    request: MigrationAgentChatRequest,
) -> MigrationAgentChatResponse:
    """Answer a user question using assessment context and recent chat history."""

    settings = get_settings()
    context = _assessment_context(request.assessment)
    used_context = bool(request.assessment)

    if not settings.has_openai_key:
        return MigrationAgentChatResponse(
            answer=_offline_answer(request.question, request.assessment),
            suggested_questions=_suggested_questions(request.assessment),
            used_assessment_context=used_context,
            model_used="offline",
        )

    llm = build_chat_openai(model=settings.model_name, temperature=0.2)
    history_text = _history_text(request.chat_history)
    reviewer_notes = (request.reviewer_notes or "").strip()
    active_tab = (request.active_tab or "overview").strip()
    human_prompt = f"""Current UI section: {active_tab}

Reviewer notes:
{reviewer_notes or "None"}

Recent conversation:
{history_text or "No previous messages."}

Assessment context:
{context or "No assessment has been run yet."}

User question:
{request.question}
"""

    try:
        response = await llm.ainvoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", human_prompt),
            ]
        )
    except Exception as exc:
        return MigrationAgentChatResponse(
            answer=(
                "I could not reach the LLM for this chat response. "
                f"Local context fallback: {_offline_answer(request.question, request.assessment)}"
            ),
            suggested_questions=_suggested_questions(request.assessment),
            used_assessment_context=used_context,
            model_used=f"{settings.model_name} unavailable: {exc.__class__.__name__}",
        )

    answer = getattr(response, "content", str(response)).strip()
    return MigrationAgentChatResponse(
        answer=answer or _offline_answer(request.question, request.assessment),
        suggested_questions=_suggested_questions(request.assessment),
        used_assessment_context=used_context,
        model_used=settings.model_name,
    )


def _assessment_context(assessment: AnalyzeMigrationResponse | None) -> str:
    if assessment is None:
        return ""

    source = assessment.source_architecture
    target = assessment.target_architecture
    data: dict[str, Any] = {
        "source": {
            "provider": source.provider,
            "summary": source.summary,
            "components": [
                {
                    "name": item.name,
                    "category": item.category,
                    "service_type": item.service_type,
                    "confidence": item.confidence,
                    "description": item.description,
                }
                for item in source.components[:30]
            ],
            "relationships": [
                item.model_dump(mode="json") for item in source.relationships[:30]
            ],
            "assumptions": source.assumptions[:12],
            "missing_information": source.missing_information[:12],
        },
        "target": {
            "provider": target.provider,
            "summary": target.summary,
            "components": [
                {
                    "name": item.name,
                    "category": item.category,
                    "service_type": item.service_type,
                    "confidence": item.confidence,
                    "description": item.description,
                }
                for item in target.components[:35]
            ],
            "relationships": [
                item.model_dump(mode="json") for item in target.relationships[:35]
            ],
            "design_notes": target.design_notes[:16],
        },
        "service_mappings": [
            {
                "source_service": item.source_service,
                "target_service": item.target_service,
                "reasoning": item.reasoning,
                "confidence": item.confidence,
                "alternatives": item.alternatives[:4],
            }
            for item in assessment.service_mappings[:35]
        ],
        "required_changes": assessment.required_changes[:20],
        "migration_strategy": [
            {
                "phase": item.phase,
                "goals": item.goals,
                "activities": item.activities[:6],
                "risks": item.risks[:5],
                "success_criteria": item.success_criteria[:5],
            }
            for item in assessment.migration_strategy[:8]
        ],
        "benefits": assessment.benefits[:15],
        "drawbacks": assessment.drawbacks[:15],
        "risks": [
            {
                "title": item.title,
                "severity": item.severity,
                "description": item.description,
                "mitigation": item.mitigation,
            }
            for item in assessment.risks[:20]
        ],
        "final_verdict": assessment.final_verdict.model_dump(mode="json"),
        "assessment_insights": assessment.assessment_insights,
        "analysis_metadata": assessment.analysis_metadata,
        "report_excerpt": _truncate(assessment.markdown_report, 7000),
    }
    return _truncate(json.dumps(data, indent=2), 18000)


def _history_text(history: list) -> str:
    lines = []
    for message in history[-8:]:
        role = getattr(message, "role", "user")
        content = getattr(message, "content", "")
        lines.append(f"{role}: {_truncate(content, 900)}")
    return "\n".join(lines)


def _offline_answer(
    question: str,
    assessment: AnalyzeMigrationResponse | None,
) -> str:
    if assessment is None:
        return (
            "Run an assessment first, then I can answer questions about detected services, "
            "service mappings, architecture flow, migration risks, cost signals, and the final verdict."
        )

    verdict = assessment.final_verdict
    high_risks = [
        risk for risk in assessment.risks if risk.severity in {"high", "critical"}
    ][:3]
    top_mappings = assessment.service_mappings[:5]
    parts = [
        f"This assessment migrates **{assessment.source_architecture.provider}** to "
        f"**{assessment.target_architecture.provider}**.",
        f"Current verdict: **{verdict.recommendation.replace('_', ' ')}** "
        f"({round(verdict.confidence * 100)}% confidence).",
    ]
    if top_mappings:
        mapping_text = "; ".join(
            f"{item.source_service} -> {item.target_service}" for item in top_mappings
        )
        parts.append(f"Key mappings: {mapping_text}.")
    if high_risks:
        risk_text = "; ".join(f"{item.title} ({item.severity})" for item in high_risks)
        parts.append(f"Highest risks to review: {risk_text}.")
    parts.append(
        "The LLM chat is unavailable, so this is a local summary. Ask a more specific question "
        "after confirming the OpenAI configuration if you need detailed reasoning."
    )
    return "\n\n".join(parts)


def _suggested_questions(assessment: AnalyzeMigrationResponse | None) -> list[str]:
    if assessment is None:
        return [
            "What can you explain after I run an assessment?",
            "What information should I include in the diagram?",
            "How should I review the migration output?",
        ]
    return [
        "Explain the target architecture flow.",
        "Which mappings need architect review?",
        "What are the top migration risks?",
        "What should we validate before approval?",
    ]


def _truncate(value: str | None, limit: int) -> str:
    text = value or ""
    if len(text) <= limit:
        return text
    return text[: limit - 40].rstrip() + "\n...[truncated for chat context]"
