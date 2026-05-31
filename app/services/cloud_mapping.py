"""Cloud service equivalence and migration mapping logic."""

from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path
from typing import Any

import yaml

from app.agents.prompts import SERVICE_MAPPING_FALLBACK_PROMPT
from app.config import get_settings
from app.schemas import ServiceMapping, SourceArchitecture
from app.services.llm_factory import build_chat_openai


DEFAULT_MAPPING_PATH = Path(__file__).resolve().parents[1] / "data" / "service_mappings.yaml"
NON_MIGRATABLE_COMPONENT_PATTERNS = (
    "on-premises",
    "on premises",
    "onprem",
    "local edge router",
    "local edge routers",
    "microsoft edge router",
    "microsoft edge routers",
    "customer premises equipment",
    "client device",
    "user device",
    "iot devices",
    "standard devices",
    "workstation",
)


def load_service_mappings(mapping_path: Path | None = None) -> dict[str, Any]:
    """Load cloud service mapping data from YAML."""

    path = mapping_path or DEFAULT_MAPPING_PATH
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Service mappings file {path} must contain a YAML mapping.")
    return data


def map_services(
    source_architecture: SourceArchitecture,
    target_provider: str = "aws",
    migration_intent: str | None = None,
    goals: list[str] | None = None,
    mapping_path: Path | None = None,
) -> list[ServiceMapping]:
    """Map detected source services to target-provider services."""

    mappings = load_service_mappings(mapping_path)
    source_provider = _provider_key(source_architecture.provider)
    target = _provider_key(target_provider)
    mapping_key = f"{source_provider}_to_{target}"
    known_mappings: dict[str, Any] = mappings.get(mapping_key, {})
    same_provider = source_provider == target and target not in {"auto", "unknown", ""}

    results: list[ServiceMapping] = []
    seen_sources: set[str] = set()
    for component in source_architecture.components:
        source_service = component.service_type or component.name
        if _should_skip_component(source_service, component.name):
            continue
        if not source_service or source_service.lower() in seen_sources:
            continue
        seen_sources.add(source_service.lower())

        if same_provider:
            results.append(_same_provider_mapping(source_service, target_provider=target))
            continue

        known_key = _find_mapping_key(source_service, known_mappings)
        if known_key:
            results.append(
                _mapping_from_yaml(
                    source_service=known_key,
                    mapping_entry=known_mappings[known_key],
                    target_provider=target,
                    migration_intent=migration_intent,
                    goals=goals or [],
                )
            )
            continue

        results.append(
            _fallback_mapping(
                source_service=source_service,
                target_provider=target,
                source_provider=source_provider,
                migration_intent=migration_intent,
                goals=goals or [],
            )
        )

    return results


def _same_provider_mapping(source_service: str, target_provider: str) -> ServiceMapping:
    return ServiceMapping(
        source_service=source_service,
        target_service=source_service,
        target_provider=target_provider,
        reasoning=(
            "Source and target providers are the same. No service-equivalence migration is required, "
            "but configuration, region, account/project/subscription, and operating-model changes may still apply."
        ),
        confidence=0.92,
        alternatives=[],
    )


def _mapping_from_yaml(
    source_service: str,
    mapping_entry: dict[str, Any],
    target_provider: str,
    migration_intent: str | None,
    goals: list[str],
) -> ServiceMapping:
    candidates = mapping_entry.get("candidates", [])
    if not candidates:
        return ServiceMapping(
            source_service=source_service,
            target_service=f"{target_provider.upper()} equivalent service",
            target_provider=target_provider,
            reasoning="No candidate mapping was configured; manual validation is required.",
            confidence=0.35,
            alternatives=[],
        )

    selected = _select_candidate(candidates, migration_intent, goals)
    alternatives = [
        candidate["service"]
        for candidate in candidates
        if candidate.get("service") != selected.get("service")
    ]
    return ServiceMapping(
        source_service=source_service,
        target_service=selected["service"],
        target_provider=target_provider,
        reasoning=(
            f"{selected['service']} is a strong fit for {source_service}: "
            f"{selected.get('use_when', 'it matches the target workload pattern')}."
        ),
        confidence=0.86 if alternatives else 0.9,
        alternatives=alternatives,
    )


def _select_candidate(
    candidates: list[dict[str, Any]],
    migration_intent: str | None,
    goals: list[str],
) -> dict[str, Any]:
    if len(candidates) == 1:
        return candidates[0]

    decision_text = f"{migration_intent or ''} {' '.join(goals)}".lower()
    candidate_scores: list[tuple[int, dict[str, Any]]] = []
    for candidate in candidates:
        use_when = candidate.get("use_when", "").lower()
        service = candidate.get("service", "").lower()
        score = 0
        for keyword in _decision_keywords(decision_text):
            if keyword in use_when or keyword in service:
                score += 1
        candidate_scores.append((score, candidate))

    candidate_scores.sort(key=lambda item: item[0], reverse=True)
    return candidate_scores[0][1]


def _fallback_mapping(
    source_service: str,
    target_provider: str,
    source_provider: str,
    migration_intent: str | None,
    goals: list[str],
) -> ServiceMapping:
    settings = get_settings()
    if settings.has_openai_key:
        try:
            llm = build_chat_openai(
                model=settings.model_name,
                temperature=0,
            ).with_structured_output(ServiceMapping)
            result = llm.invoke(
                (
                    f"{SERVICE_MAPPING_FALLBACK_PROMPT}\n\n"
                    f"Source provider: {source_provider}\n"
                    f"Target provider: {target_provider}\n"
                    f"Source service: {source_service}\n"
                    f"Migration intent: {migration_intent or 'Not provided'}\n"
                    f"Goals: {', '.join(goals) if goals else 'Not provided'}"
                )
            )
            if isinstance(result, ServiceMapping):
                return result
            return ServiceMapping.model_validate(result)
        except Exception:
            pass

    return ServiceMapping(
        source_service=source_service,
        target_service=f"{target_provider.upper()} managed equivalent for {source_service}",
        target_provider=target_provider,
        reasoning=(
            "No direct YAML mapping was found. This placeholder requires architect review "
            "or LLM fallback with an API key configured."
        ),
        confidence=0.3,
        alternatives=[],
    )


def _find_mapping_key(source_service: str, known_mappings: dict[str, Any]) -> str | None:
    normalized_source = _normalize(source_service)
    normalized_keys = {_normalize(key): key for key in known_mappings}

    if normalized_source in normalized_keys:
        return normalized_keys[normalized_source]

    for normalized_key, original_key in normalized_keys.items():
        if normalized_key in normalized_source or normalized_source in normalized_key:
            return original_key

    close_matches = get_close_matches(normalized_source, normalized_keys.keys(), n=1, cutoff=0.78)
    if close_matches:
        return normalized_keys[close_matches[0]]

    return None


def _decision_keywords(text: str) -> set[str]:
    keywords = {
        "containerized",
        "container",
        "modernization",
        "modernize",
        "serverless",
        "event",
        "managed",
        "lift-and-shift",
        "database",
        "relational",
        "document",
        "queue",
        "pub/sub",
        "routing",
        "waf",
    }
    return {keyword for keyword in keywords if keyword in text}


def _provider_key(provider: str | None) -> str:
    normalized = (provider or "unknown").strip().lower().replace("-", " ")
    if "azure" in normalized:
        return "azure"
    if "aws" in normalized or "amazon web services" in normalized:
        return "aws"
    if "gcp" in normalized or "google cloud" in normalized:
        return "gcp"
    return normalized.replace(" ", "_")


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def _should_skip_component(source_service: str | None, component_name: str | None) -> bool:
    """Skip diagram artifacts that are not cloud services to be migrated."""

    text = f"{source_service or ''} {component_name or ''}".lower()
    if not text.strip():
        return True
    return any(pattern in text for pattern in NON_MIGRATABLE_COMPONENT_PATTERNS)
