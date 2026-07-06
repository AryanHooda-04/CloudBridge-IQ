"""LLM-backed comparison between two migration assessment runs."""

from __future__ import annotations

import json
import asyncio
import re
from datetime import UTC, datetime
from typing import Any

from app.config import get_settings
from app.schemas import (
    AssessmentComparisonDelta,
    AssessmentComparisonItem,
    AssessmentComparisonRequest,
    AssessmentComparisonResponse,
)
from app.services.llm_factory import build_chat_openai


SYSTEM_PROMPT = """You are CloudBridge IQ's enterprise architecture comparison analyst.

Compare two cloud migration assessments for an architecture review board.

Rules:
- Ground every conclusion in the supplied assessment data.
- Do not invent cloud services, costs, owners, dates, or compliance facts.
- Call out uncertainty and missing validation items.
- Prefer concise enterprise language suitable for project reviews.
- Return one strict JSON object only. No Markdown, code fences, comments, trailing commas, or commentary.
- Use double quoted JSON strings and keep arrays concise, usually 2-4 items.
"""

COMPARISON_PROMPT_CHAR_LIMIT = 9000
COMPARISON_CLIENT_TIMEOUT_SECONDS = 180
COMPARISON_CALL_TIMEOUT_SECONDS = 220
COMPARISON_MAX_TOKENS = 5000


async def generate_assessment_comparison(
    request: AssessmentComparisonRequest,
) -> AssessmentComparisonResponse:
    """Generate a structured comparison, using the LLM when configured."""

    settings = get_settings()
    fallback = _offline_comparison(request)
    if not settings.has_openai_key:
        return fallback

    llm = build_chat_openai(
        model=settings.model_name,
        temperature=0.15,
        timeout=COMPARISON_CLIENT_TIMEOUT_SECONDS,
        max_retries=0,
        max_tokens=COMPARISON_MAX_TOKENS,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    prompt = _comparison_prompt(request, fallback)
    try:
        response = await asyncio.wait_for(
            llm.ainvoke(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", prompt),
                ]
            ),
            timeout=COMPARISON_CALL_TIMEOUT_SECONDS,
        )
        content = getattr(response, "content", response)
        generated = _parse_llm_response(content, fallback=fallback)
    except (asyncio.TimeoutError, TimeoutError):
        return _llm_fallback(
            fallback,
            model_name=settings.model_name,
            reason="timeout",
            assumption=(
                f"{settings.model_name} did not return the structured comparison within "
                f"{COMPARISON_CALL_TIMEOUT_SECONDS} seconds, so CloudBridge IQ used the "
                "deterministic comparison to keep the review workflow moving."
            ),
        )
    except Exception as exc:
        return _llm_fallback(
            fallback,
            model_name=settings.model_name,
            reason=exc.__class__.__name__,
            assumption=(
                f"{settings.model_name} comparison failed with {exc.__class__.__name__}; "
                "CloudBridge IQ used the deterministic comparison from assessment metadata."
            ),
        )

    return generated.model_copy(
        update={
            "source": "llm",
            "model_used": settings.model_name,
            "generated_at": _utc_now(),
            "baseline_readiness": fallback.baseline_readiness,
            "current_readiness": fallback.current_readiness,
            "readiness_delta": fallback.readiness_delta,
            "verdict_delta": fallback.verdict_delta,
        }
    )


def _comparison_prompt(
    request: AssessmentComparisonRequest,
    fallback: AssessmentComparisonResponse,
) -> str:
    schema = {
        "executive_summary": "2-3 sentence business and architecture summary",
        "decision": "clear recommendation: promote current, keep baseline, merge learnings, or require review",
        "comparison_confidence": 0.0,
        "business_impact": ["concise bullet"],
        "architecture_deltas": [
            {
                "area": "Target design",
                "baseline": "what baseline says",
                "current": "what current says",
                "impact": "why it matters",
                "priority": "low|medium|high|critical",
                "owner": "Architecture review board",
            }
        ],
        "mapping_deltas": [],
        "risk_deltas": [],
        "governance_actions": ["specific decision or validation action"],
        "recommended_next_steps": ["specific next step"],
        "assumptions": ["known unknown or validation caveat"],
    }
    data = {
        "focus": request.focus or "Compare assessments for an enterprise architecture review.",
        "baseline": _assessment_digest(request.baseline),
        "current": _assessment_digest(request.current),
        "deterministic_metrics": {
            "baseline_readiness": fallback.baseline_readiness,
            "current_readiness": fallback.current_readiness,
            "readiness_delta": fallback.readiness_delta,
            "verdict_delta": fallback.verdict_delta,
        },
        "required_json_shape": schema,
        "json_contract": [
            "Return a single JSON object only.",
            "Do not wrap the object in Markdown or a code fence.",
            "Do not include comments or trailing commas.",
            "Use strings for narrative fields and arrays of strings/cards for list fields.",
            "Keep every delta field concise enough for dashboard rendering.",
        ],
    }
    return _truncate(json.dumps(data, indent=2), COMPARISON_PROMPT_CHAR_LIMIT)


def _llm_fallback(
    fallback: AssessmentComparisonResponse,
    *,
    model_name: str,
    reason: str,
    assumption: str,
) -> AssessmentComparisonResponse:
    return fallback.model_copy(
        update={
            "source": "llm_fallback",
            "model_used": f"{model_name} fallback ({reason})",
            "assumptions": [
                *fallback.assumptions,
                assumption,
            ],
        }
    )


def _parse_llm_response(
    content: Any,
    fallback: AssessmentComparisonResponse | None = None,
) -> AssessmentComparisonResponse:
    text = _coerce_llm_text(content)
    text = _extract_json_object(text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = json.loads(_repair_common_json_issues(text))
    payload = _normalize_llm_payload(payload, fallback)
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("source", "llm")
    payload.setdefault("model_used", None)
    payload.setdefault("baseline_readiness", 0)
    payload.setdefault("current_readiness", 0)
    payload.setdefault("readiness_delta", 0)
    payload.setdefault("verdict_delta", "No verdict change identified.")
    return AssessmentComparisonResponse.model_validate(payload)


def _coerce_llm_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        if isinstance(content.get("text"), str):
            return content["text"].strip()
        if isinstance(content.get("content"), str):
            return content["content"].strip()
        if "json" in content:
            return json.dumps(content["json"])
        return json.dumps(content)
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            item_text = _coerce_llm_text(item)
            if item_text:
                parts.append(item_text)
        return "\n".join(parts).strip()
    return str(content or "").strip()


def _extract_json_object(text: str) -> str:
    text = str(text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    if start < 0:
        return text

    in_string = False
    escaped = False
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1].strip()
    return text[start:].strip()


def _repair_common_json_issues(text: str) -> str:
    repaired = str(text or "").strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = repaired.replace("\u201c", '"').replace("\u201d", '"')
    repaired = repaired.replace("\u2018", "'").replace("\u2019", "'")
    return repaired


def _normalize_llm_payload(
    payload: Any,
    fallback: AssessmentComparisonResponse | None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {"executive_summary": _compact_text(payload)}

    normalized = dict(payload)
    fallback_data = fallback.model_dump(mode="json") if fallback else {}

    normalized["executive_summary"] = (
        _compact_text(normalized.get("executive_summary"))
        or _compact_text(normalized.get("summary"))
        or _compact_text(normalized.get("analysis_summary"))
        or str(fallback_data.get("executive_summary") or "")
    )
    normalized["decision"] = (
        _compact_text(_first_present(normalized, "decision", "recommendation", "final_recommendation"))
        or _compact_text(_first_present(normalized, "decision_signal", "verdict", "overall_recommendation"))
        or str(fallback_data.get("decision") or "Review comparison output before promotion.")
    )
    normalized["comparison_confidence"] = _confidence_value(
        normalized.get("comparison_confidence")
        if "comparison_confidence" in normalized
        else normalized.get("confidence"),
        fallback_data.get("comparison_confidence", 0.7),
    )
    normalized["business_impact"] = _string_list(
        normalized.get("business_impact")
        if "business_impact" in normalized
        else _first_present(normalized, "business_impacts", "impact", "business_summary"),
        fallback_data.get("business_impact", []),
    )
    normalized["architecture_deltas"] = _delta_list(
        normalized.get("architecture_deltas")
        if "architecture_deltas" in normalized
        else _first_present(normalized, "architecture_delta", "technical_deltas", "architecture_changes"),
        fallback_data.get("architecture_deltas", []),
        default_area="Architecture delta",
    )
    normalized["mapping_deltas"] = _delta_list(
        normalized.get("mapping_deltas")
        if "mapping_deltas" in normalized
        else _first_present(normalized, "mapping_delta", "service_mapping_deltas", "service_mappings"),
        fallback_data.get("mapping_deltas", []),
        default_area="Mapping delta",
    )
    normalized["risk_deltas"] = _delta_list(
        normalized.get("risk_deltas")
        if "risk_deltas" in normalized
        else _first_present(normalized, "risk_delta", "risk_changes", "risks"),
        fallback_data.get("risk_deltas", []),
        default_area="Risk delta",
    )
    normalized["governance_actions"] = _string_list(
        normalized.get("governance_actions")
        if "governance_actions" in normalized
        else _first_present(normalized, "governance", "controls", "decision_gates"),
        fallback_data.get("governance_actions", []),
    )
    normalized["recommended_next_steps"] = _string_list(
        normalized.get("recommended_next_steps")
        if "recommended_next_steps" in normalized
        else _first_present(normalized, "next_steps", "recommendations", "actions"),
        fallback_data.get("recommended_next_steps", []),
    )
    normalized["assumptions"] = _string_list(
        normalized.get("assumptions")
        if "assumptions" in normalized
        else _first_present(normalized, "notes", "caveats", "known_unknowns"),
        fallback_data.get("assumptions", []),
    )

    for key in ("baseline_readiness", "current_readiness", "readiness_delta", "verdict_delta"):
        if key not in normalized and key in fallback_data:
            normalized[key] = fallback_data[key]

    return normalized


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _confidence_value(value: Any, fallback: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        try:
            confidence = float(fallback)
        except (TypeError, ValueError):
            confidence = 0.7
    if confidence > 1:
        confidence = confidence / 100
    return max(0, min(1, round(confidence, 2)))


def _string_list(value: Any, fallback: Any) -> list[str]:
    items = _flatten_text_items(value)
    if not items:
        items = _flatten_text_items(fallback)
    return [_truncate(item, 700) for item in items if item][:8]


def _flatten_text_items(value: Any, *, prefix: str | None = None) -> list[str]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, str):
        text = _compact_text(value)
        return [f"{prefix}: {text}" if prefix and text else text] if text else []
    if isinstance(value, (int, float, bool)):
        text = str(value)
        return [f"{prefix}: {text}" if prefix else text]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_flatten_text_items(item, prefix=prefix))
        return result
    if isinstance(value, dict):
        preferred = _first_present(
            value,
            "summary",
            "impact",
            "detail",
            "description",
            "recommendation",
            "action",
            "decision",
            "rationale",
            "name",
            "title",
        )
        if isinstance(preferred, str):
            text = _compact_text(preferred)
            return [f"{prefix}: {text}" if prefix and text else text] if text else []

        result: list[str] = []
        for key, item in value.items():
            label = str(key).replace("_", " ").strip().title()
            result.extend(_flatten_text_items(item, prefix=label))
        return result
    return [_compact_text(value)]


def _compact_text(value: Any) -> str:
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = _flatten_text_items(value)
        return " ".join(parts[:4])
    if isinstance(value, dict):
        parts = _flatten_text_items(value)
        return " ".join(parts[:4])
    return " ".join(str(value).split())


def _delta_list(
    value: Any,
    fallback: Any,
    *,
    default_area: str,
) -> list[dict[str, Any]]:
    deltas = _coerce_delta_items(value, default_area=default_area)
    if not deltas:
        deltas = _coerce_delta_items(fallback, default_area=default_area)
    return deltas[:8]


def _coerce_delta_items(value: Any, *, default_area: str) -> list[dict[str, Any]]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, list):
        result: list[dict[str, Any]] = []
        for item in value:
            result.extend(_coerce_delta_items(item, default_area=default_area))
        return result
    if isinstance(value, str):
        text = _compact_text(value)
        if not text:
            return []
        return [
            _delta_payload(
                area=default_area,
                baseline="Baseline assessment",
                current=text,
                impact=text,
                priority="medium",
                owner="Architecture review board",
            )
        ]
    if isinstance(value, dict):
        if _looks_like_delta(value):
            return [
                _delta_payload(
                    area=_compact_text(
                        _first_present(value, "area", "theme", "title", "name", "category")
                    )
                    or default_area,
                    baseline=_compact_text(
                        _first_present(value, "baseline", "from", "previous", "before", "source")
                    )
                    or "Baseline assessment",
                    current=_compact_text(
                        _first_present(value, "current", "to", "after", "target", "proposed")
                    )
                    or _compact_text(_first_present(value, "change", "detail", "description"))
                    or "Current assessment",
                    impact=_compact_text(
                        _first_present(value, "impact", "rationale", "reasoning", "summary", "risk")
                    )
                    or _compact_text(_first_present(value, "detail", "description", "recommendation"))
                    or "Review the delta with architecture stakeholders.",
                    priority=_priority_value(value.get("priority") or value.get("risk_level") or "medium"),
                    owner=_compact_text(value.get("owner")) or "Architecture review board",
                )
            ]
        result: list[dict[str, Any]] = []
        for key, item in value.items():
            area = str(key).replace("_", " ").strip().title() or default_area
            nested = _coerce_delta_items(item, default_area=area)
            result.extend(nested)
        return result
    return []


def _looks_like_delta(value: dict[str, Any]) -> bool:
    keys = {
        "area",
        "theme",
        "title",
        "baseline",
        "current",
        "impact",
        "priority",
        "owner",
        "before",
        "after",
        "source",
        "target",
        "change",
        "risk_level",
    }
    return bool(keys & set(value))


def _delta_payload(
    *,
    area: str,
    baseline: str,
    current: str,
    impact: str,
    priority: str,
    owner: str,
) -> dict[str, Any]:
    return {
        "area": _truncate(area or "Assessment delta", 120),
        "baseline": _truncate(baseline or "Baseline assessment", 500),
        "current": _truncate(current or "Current assessment", 500),
        "impact": _truncate(impact or "Review this delta with the architecture owner.", 700),
        "priority": _priority_value(priority),
        "owner": _truncate(owner or "Architecture review board", 160),
    }


def _priority_value(value: Any) -> str:
    priority = str(value or "medium").strip().lower()
    if priority in {"critical", "high", "medium", "low"}:
        return priority
    if priority in {"severe", "blocker"}:
        return "critical"
    if priority in {"warning", "warn", "moderate"}:
        return "medium"
    return "medium"


def _offline_comparison(
    request: AssessmentComparisonRequest,
) -> AssessmentComparisonResponse:
    baseline = request.baseline
    current = request.current
    baseline_assessment = baseline.assessment
    current_assessment = current.assessment
    baseline_readiness = _readiness_score(baseline)
    current_readiness = _readiness_score(current)
    readiness_delta = current_readiness - baseline_readiness
    baseline_verdict = baseline_assessment.final_verdict.recommendation
    current_verdict = current_assessment.final_verdict.recommendation
    verdict_delta = (
        "Verdict is unchanged."
        if baseline_verdict == current_verdict
        else f"Verdict changed from {baseline_verdict.replace('_', ' ')} to {current_verdict.replace('_', ' ')}."
    )
    decision = _decision_label(readiness_delta, baseline_verdict, current_verdict)
    architecture_deltas = _architecture_deltas(baseline, current)
    mapping_deltas = _mapping_deltas(baseline, current)
    risk_deltas = _risk_deltas(baseline, current)
    business_impact = _business_impact(
        baseline_readiness=baseline_readiness,
        current_readiness=current_readiness,
        readiness_delta=readiness_delta,
        baseline=baseline,
        current=current,
    )
    confidence = _comparison_confidence(baseline, current)
    return AssessmentComparisonResponse(
        executive_summary=(
            f"{current.title} is being compared with {baseline.title}. "
            f"Readiness moved from {baseline_readiness}% to {current_readiness}% and {verdict_delta.lower()} "
            "Use this as an architecture review summary until stakeholder evidence, cost model, and implementation constraints are validated."
        ),
        decision=decision,
        model_used="offline",
        generated_at=_utc_now(),
        source="offline",
        comparison_confidence=confidence,
        baseline_readiness=baseline_readiness,
        current_readiness=current_readiness,
        readiness_delta=readiness_delta,
        verdict_delta=verdict_delta,
        business_impact=business_impact,
        architecture_deltas=architecture_deltas,
        mapping_deltas=mapping_deltas,
        risk_deltas=risk_deltas,
        governance_actions=_governance_actions(baseline, current, readiness_delta),
        recommended_next_steps=_recommended_next_steps(baseline, current, readiness_delta),
        assumptions=[
            "Comparison is based on generated assessment output and review metadata available in CloudBridge IQ.",
            "Validate runtime dependencies, data volumes, security controls, and cost model before final approval.",
        ],
    )


def _assessment_digest(item: AssessmentComparisonItem) -> dict[str, Any]:
    assessment = item.assessment
    insights = assessment.assessment_insights or {}
    return {
        "title": item.title,
        "status": item.status,
        "reviewer": item.reviewer,
        "updated_at": item.updated_at,
        "route": {
            "source": assessment.source_architecture.provider,
            "target": assessment.target_architecture.provider,
        },
        "readiness": _readiness_score(item),
        "verdict": assessment.final_verdict.model_dump(mode="json"),
        "source_summary": _truncate(assessment.source_architecture.summary, 900),
        "target_summary": _truncate(assessment.target_architecture.summary, 900),
        "component_counts": {
            "source": len(assessment.source_architecture.components),
            "target": len(assessment.target_architecture.components),
        },
        "target_components": [
            {
                "name": component.name,
                "category": component.category,
                "service_type": component.service_type,
                "confidence": component.confidence,
            }
            for component in assessment.target_architecture.components[:16]
        ],
        "service_mappings": [
            {
                "source_service": mapping.source_service,
                "target_service": mapping.target_service,
                "confidence": mapping.confidence,
                "reasoning": mapping.reasoning,
            }
            for mapping in assessment.service_mappings[:24]
        ],
        "risks": [
            {
                "title": risk.title,
                "severity": risk.severity,
                "description": risk.description,
                "mitigation": risk.mitigation,
            }
            for risk in assessment.risks[:12]
        ],
        "required_changes": assessment.required_changes[:10],
        "benefits": assessment.benefits[:8],
        "drawbacks": assessment.drawbacks[:8],
        "insight_scores": insights.get("scores", {}),
        "review_metadata": item.metadata,
    }


def _architecture_deltas(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
) -> list[AssessmentComparisonDelta]:
    baseline_assessment = baseline.assessment
    current_assessment = current.assessment
    deltas = [
        AssessmentComparisonDelta(
            area="Migration route",
            baseline=f"{baseline_assessment.source_architecture.provider} to {baseline_assessment.target_architecture.provider}",
            current=f"{current_assessment.source_architecture.provider} to {current_assessment.target_architecture.provider}",
            impact=(
                "Provider route changed; review identity, networking, data movement, support model, and operating model impacts."
                if baseline_assessment.target_architecture.provider != current_assessment.target_architecture.provider
                else "Provider route is consistent, so review can focus on design quality and implementation readiness."
            ),
            priority="high"
            if baseline_assessment.target_architecture.provider != current_assessment.target_architecture.provider
            else "medium",
        ),
        AssessmentComparisonDelta(
            area="Target architecture scope",
            baseline=f"{len(baseline_assessment.target_architecture.components)} target components",
            current=f"{len(current_assessment.target_architecture.components)} target components",
            impact="Component count changed; validate whether the new design simplifies operations or hides required platform services.",
            priority="medium",
        ),
    ]
    if baseline_assessment.target_architecture.summary != current_assessment.target_architecture.summary:
        deltas.append(
            AssessmentComparisonDelta(
                area="Target design narrative",
                baseline=_truncate(baseline_assessment.target_architecture.summary, 240),
                current=_truncate(current_assessment.target_architecture.summary, 240),
                impact="Architecture narrative changed; align stakeholders on the target operating model before approval.",
                priority="medium",
            )
        )
    return deltas


def _mapping_deltas(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
) -> list[AssessmentComparisonDelta]:
    baseline_mappings = baseline.assessment.service_mappings or []
    current_mappings = current.assessment.service_mappings or []
    baseline_by_source = {_key(mapping.source_service): mapping for mapping in baseline_mappings}
    current_by_source = {_key(mapping.source_service): mapping for mapping in current_mappings}
    changed = [
        source
        for source, mapping in current_by_source.items()
        if source in baseline_by_source
        and baseline_by_source[source].target_service != mapping.target_service
    ]
    low_confidence = [
        mapping
        for mapping in current_mappings
        if float(mapping.confidence or 0) < 0.75
    ]
    deltas = [
        AssessmentComparisonDelta(
            area="Service mapping coverage",
            baseline=f"{len(baseline_mappings)} mappings",
            current=f"{len(current_mappings)} mappings",
            impact="Mapping coverage changed; confirm each source capability has an explicit target service and migration approach.",
            priority="medium",
        )
    ]
    if changed:
        preview = ", ".join(changed[:4])
        deltas.append(
            AssessmentComparisonDelta(
                area="Changed target mappings",
                baseline=f"{len(changed)} service mappings changed",
                current=f"Changed sources include {preview}",
                impact="Changed mappings can affect cost, delivery skills, integration patterns, and runbooks.",
                priority="high",
            )
        )
    if low_confidence:
        deltas.append(
            AssessmentComparisonDelta(
                area="Low-confidence mappings",
                baseline=f"{len([m for m in baseline_mappings if float(m.confidence or 0) < 0.75])} below threshold",
                current=f"{len(low_confidence)} below threshold",
                impact="Architect review is required for mappings below the confidence threshold.",
                priority="high",
                owner="Solution architect",
            )
        )
    return deltas


def _risk_deltas(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
) -> list[AssessmentComparisonDelta]:
    baseline_risks = baseline.assessment.risks or []
    current_risks = current.assessment.risks or []
    baseline_high = {
        _key(risk.title): risk for risk in baseline_risks if risk.severity in {"high", "critical"}
    }
    current_high = {
        _key(risk.title): risk for risk in current_risks if risk.severity in {"high", "critical"}
    }
    new_high = [risk.title for key, risk in current_high.items() if key not in baseline_high]
    resolved_high = [risk.title for key, risk in baseline_high.items() if key not in current_high]
    deltas = [
        AssessmentComparisonDelta(
            area="High-severity risk posture",
            baseline=f"{len(baseline_high)} high or critical risks",
            current=f"{len(current_high)} high or critical risks",
            impact="Risk movement changes the approval threshold and evidence expected by the decision gate.",
            priority="critical" if len(current_high) > len(baseline_high) else "high",
            owner="Architecture review board",
        )
    ]
    if new_high:
        deltas.append(
            AssessmentComparisonDelta(
                area="New high-risk items",
                baseline="Not present in baseline high-risk list",
                current=", ".join(new_high[:5]),
                impact="New high-risk items need mitigation ownership before the assessment can be promoted.",
                priority="critical",
                owner="Risk owner",
            )
        )
    if resolved_high:
        deltas.append(
            AssessmentComparisonDelta(
                area="Resolved high-risk items",
                baseline=", ".join(resolved_high[:5]),
                current="No longer present in current high-risk list",
                impact="Confirm whether these risks were actually mitigated or only reclassified by the assessment.",
                priority="medium",
            )
        )
    return deltas


def _business_impact(
    *,
    baseline_readiness: int,
    current_readiness: int,
    readiness_delta: int,
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
) -> list[str]:
    movement = (
        "improved"
        if readiness_delta > 0
        else "declined"
        if readiness_delta < 0
        else "remained stable"
    )
    result = [
        f"Readiness {movement} from {baseline_readiness}% to {current_readiness}%.",
        f"Current route targets {current.assessment.target_architecture.provider}; baseline targeted {baseline.assessment.target_architecture.provider}.",
    ]
    if current.assessment.benefits:
        result.append(f"Current top benefit: {current.assessment.benefits[0]}")
    if current.assessment.drawbacks:
        result.append(f"Current top drawback: {current.assessment.drawbacks[0]}")
    return result


def _governance_actions(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
    readiness_delta: int,
) -> list[str]:
    actions = [
        "Review mapping changes and low-confidence mappings with a solution architect.",
        "Attach evidence for data migration, security controls, rollback, and operational readiness before approval.",
    ]
    if current.assessment.risks:
        actions.append("Assign owners to current high and medium risks and record mitigation evidence.")
    if readiness_delta < 0:
        actions.append("Hold promotion until the readiness decline is explained and accepted by the decision owner.")
    else:
        actions.append("Use the current assessment as the candidate version if open risks and validation evidence are accepted.")
    return actions


def _recommended_next_steps(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
    readiness_delta: int,
) -> list[str]:
    steps = [
        "Confirm the chosen target provider and architecture pattern with the architecture review board.",
        "Validate service mapping deltas against the application inventory and dependency map.",
        "Update cost model and cutover runbook using the current target architecture.",
    ]
    if readiness_delta >= 0:
        steps.append("Prepare the current assessment for reviewed or approved status after evidence attachment.")
    else:
        steps.append("Compare baseline controls against current gaps before continuing planning.")
    return steps


def _decision_label(readiness_delta: int, baseline_verdict: str, current_verdict: str) -> str:
    if current_verdict == "not_recommended":
        return "Do not promote current assessment until blockers are remediated."
    if readiness_delta >= 8 and current_verdict != "not_recommended":
        return "Promote current assessment as the candidate version, subject to architect evidence review."
    if readiness_delta <= -8:
        return "Keep baseline as the safer planning reference until the readiness decline is explained."
    if baseline_verdict != current_verdict:
        return "Run architecture review before promotion because verdict changed between assessments."
    return "Assessments are directionally similar; merge useful deltas and proceed through normal review gates."


def _readiness_score(item: AssessmentComparisonItem) -> int:
    scores = item.assessment.assessment_insights.get("scores", {})
    readiness = scores.get("overall_readiness", {}).get("value")
    if readiness is None:
        readiness = item.assessment.final_verdict.confidence * 100
    return max(0, min(100, round(float(readiness or 0))))


def _comparison_confidence(
    baseline: AssessmentComparisonItem,
    current: AssessmentComparisonItem,
) -> float:
    confidence = (
        float(baseline.assessment.final_verdict.confidence or 0)
        + float(current.assessment.final_verdict.confidence or 0)
    ) / 2
    has_mappings = bool(baseline.assessment.service_mappings and current.assessment.service_mappings)
    has_risks = bool(baseline.assessment.risks or current.assessment.risks)
    adjustment = 0.08 if has_mappings else -0.08
    adjustment += 0.04 if has_risks else -0.04
    return max(0.35, min(0.92, round(confidence + adjustment, 2)))


def _key(value: str | None) -> str:
    return " ".join(str(value or "").lower().split())


def _truncate(value: str | None, limit: int) -> str:
    text = value or ""
    if len(text) <= limit:
        return text
    return text[: limit - 24].rstrip() + "...[truncated]"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
