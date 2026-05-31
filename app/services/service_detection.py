"""Source architecture detection using OpenAI vision or deterministic fallbacks."""

from __future__ import annotations

import re

from app.agents.prompts import SOURCE_ARCHITECTURE_PROMPT
from app.config import get_settings
from app.schemas import (
    ArchitectureComponent,
    ArchitectureRelationship,
    DiagramIngestionResult,
    SourceArchitecture,
)
from app.services.llm_factory import build_chat_openai


KNOWN_SERVICE_PATTERNS: dict[str, tuple[str, str]] = {
    "Azure Virtual Machines": ("compute", r"\b(azure\s+)?virtual machines?\b|\bvm\b"),
    "Azure App Service": ("compute", r"\b(azure\s+)?app service\b"),
    "Azure Functions": ("compute", r"\b(azure\s+)?functions?\b"),
    "Azure Blob Storage": ("storage", r"\b(azure\s+)?blob storage\b"),
    "Azure SQL Database": ("database", r"\b(azure\s+)?sql database\b|\bazure sql\b"),
    "Azure Cosmos DB": ("database", r"\b(azure\s+)?cosmos\s*db\b"),
    "Azure Virtual Network": ("networking", r"\b(azure\s+)?virtual network\b|\bvnet\b"),
    "Azure Load Balancer": ("networking", r"\b(azure\s+)?load balancer\b"),
    "Azure Application Gateway": ("networking", r"\b(azure\s+)?application gateway\b"),
    "Azure Key Vault": ("security", r"\b(azure\s+)?key vault\b"),
    "Azure Monitor": ("observability", r"\b(azure\s+)?monitor\b"),
    "Azure Service Bus": ("messaging", r"\b(azure\s+)?service bus\b"),
}


async def detect_source_architecture(
    ingestion: DiagramIngestionResult,
    source_provider: str = "auto",
    migration_intent: str | None = None,
    goals: list[str] | None = None,
) -> SourceArchitecture:
    """Infer source architecture using structured LLM output when configured."""

    settings = get_settings()
    if settings.has_openai_key:
        ingestion.metadata["llm_detection_attempted"] = True
        try:
            source_architecture = await _detect_with_llm(
                ingestion=ingestion,
                source_provider=source_provider,
                migration_intent=migration_intent,
                goals=goals or [],
            )
            ingestion.metadata["detection_mode"] = (
                "openai_vision" if ingestion.image_base64 else "openai_text"
            )
            return source_architecture
        except Exception as exc:
            ingestion.metadata["detection_mode"] = "heuristic_fallback_after_llm_error"
            ingestion.metadata["llm_detection_error"] = str(exc)
            # Production services should log this exception. The fallback keeps
            # local development and tests usable without external model access.
            pass
    else:
        ingestion.metadata["llm_detection_attempted"] = False
        ingestion.metadata["detection_mode"] = "heuristic_fallback_no_api_key"

    return _detect_with_heuristics(ingestion, source_provider)


async def _detect_with_llm(
    ingestion: DiagramIngestionResult,
    source_provider: str,
    migration_intent: str | None,
    goals: list[str],
) -> SourceArchitecture:
    settings = get_settings()
    from langchain_core.messages import HumanMessage

    llm = build_chat_openai(
        model=settings.vision_model_name,
        temperature=0,
    ).with_structured_output(SourceArchitecture)

    context = (
        f"Source provider hint: {source_provider}\n"
        f"Migration intent: {migration_intent or 'Not provided'}\n"
        f"Goals: {', '.join(goals) if goals else 'Not provided'}\n"
        f"File: {ingestion.filename}\n"
    )

    if ingestion.image_base64:
        extracted_text = ingestion.text.strip()
        text_prompt = f"{SOURCE_ARCHITECTURE_PROMPT}\n\n{context}"
        if extracted_text:
            text_prompt += (
                "\nExtracted PDF text found the following content. "
                "Use it as supporting evidence, but trust the image when the two disagree:\n"
                f"{extracted_text}"
            )
        message_content = [
            {"type": "text", "text": text_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{ingestion.image_mime_type};base64,{ingestion.image_base64}"
                },
            },
        ]
    else:
        diagram_text = ingestion.text or "No extractable text was found."
        message_content = (
            f"{SOURCE_ARCHITECTURE_PROMPT}\n\n{context}\n"
            f"Extracted diagram text:\n{diagram_text}"
        )

    result = await llm.ainvoke([HumanMessage(content=message_content)])
    if not isinstance(result, SourceArchitecture):
        return SourceArchitecture.model_validate(result)
    return result


def _detect_with_heuristics(
    ingestion: DiagramIngestionResult,
    source_provider: str = "auto",
) -> SourceArchitecture:
    text = ingestion.text or ingestion.filename or ""
    provider = _provider_from_hint_or_text(source_provider, text)
    components: list[ArchitectureComponent] = []

    for service_name, (category, pattern) in KNOWN_SERVICE_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            components.append(
                ArchitectureComponent(
                    id=_slug(service_name),
                    name=service_name,
                    provider="azure",
                    service_type=service_name,
                    category=category,
                    confidence=0.72,
                    description=f"Detected from text or filename reference to {service_name}.",
                )
            )

    if not components:
        components.append(
            ArchitectureComponent(
                id="unknown_application",
                name="Unclear application workload",
                provider=None if provider == "unknown" else provider,
                service_type="unknown",
                category="application",
                confidence=0.25,
                description="The diagram requires vision model analysis for reliable service detection.",
            )
        )

    relationships = _infer_basic_relationships(components)
    assumptions = [
        "Heuristic detection was used because an OpenAI API key was not configured or model analysis failed."
    ]
    missing_information = []
    if ingestion.file_kind == "image" and not ingestion.text.strip():
        missing_information.append(
            "Image-only diagram details require the configured vision model for high-confidence extraction."
        )
    if ingestion.file_kind == "pdf" and not ingestion.text.strip():
        missing_information.append("PDF contained little or no extractable text.")

    return SourceArchitecture(
        provider=provider,
        summary=(
            f"Detected {len(components)} component(s) from the uploaded diagram. "
            "Confidence is limited without full vision analysis."
        ),
        components=components,
        relationships=relationships,
        assumptions=assumptions,
        missing_information=missing_information,
    )


def _provider_from_hint_or_text(source_provider: str, text: str) -> str:
    provider_hint = (source_provider or "auto").strip().lower()
    if provider_hint != "auto":
        return provider_hint
    lower_text = text.lower()
    if "azure" in lower_text:
        return "azure"
    if "aws" in lower_text or "amazon" in lower_text:
        return "aws"
    if "gcp" in lower_text or "google cloud" in lower_text:
        return "gcp"
    return "unknown"


def _infer_basic_relationships(
    components: list[ArchitectureComponent],
) -> list[ArchitectureRelationship]:
    by_category = {component.category: component for component in components}
    relationships: list[ArchitectureRelationship] = []

    network = by_category.get("networking")
    compute = by_category.get("compute") or by_category.get("application")
    database = by_category.get("database")
    storage = by_category.get("storage")
    messaging = by_category.get("messaging")
    security = by_category.get("security")
    observability = by_category.get("observability")

    if network and compute:
        relationships.append(
            ArchitectureRelationship(
                source_id=network.id,
                target_id=compute.id,
                relationship_type="routes_to",
                description="Network layer routes traffic to the application workload.",
            )
        )
    if compute and database:
        relationships.append(
            ArchitectureRelationship(
                source_id=compute.id,
                target_id=database.id,
                relationship_type="reads_writes",
                description="Application workload reads and writes relational or NoSQL data.",
            )
        )
    if compute and storage:
        relationships.append(
            ArchitectureRelationship(
                source_id=compute.id,
                target_id=storage.id,
                relationship_type="uses_storage",
                description="Application workload stores or retrieves object data.",
            )
        )
    if compute and messaging:
        relationships.append(
            ArchitectureRelationship(
                source_id=compute.id,
                target_id=messaging.id,
                relationship_type="publishes_or_consumes",
                description="Application workload exchanges asynchronous messages.",
            )
        )
    if compute and security:
        relationships.append(
            ArchitectureRelationship(
                source_id=compute.id,
                target_id=security.id,
                relationship_type="retrieves_secrets",
                description="Application workload retrieves secrets or keys.",
            )
        )
    if compute and observability:
        relationships.append(
            ArchitectureRelationship(
                source_id=compute.id,
                target_id=observability.id,
                relationship_type="emits_telemetry",
                description="Application workload emits logs and metrics.",
            )
        )

    return relationships


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
