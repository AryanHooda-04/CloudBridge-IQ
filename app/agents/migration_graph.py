"""LangGraph workflow for cloud migration assessment."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import FinalVerdict, MigrationAssessmentReport
from app.services.architecture_generator import generate_target_architecture
from app.services.cloud_mapping import map_services
from app.services.diagram_ingestion import ingest_diagram as ingest_diagram_file
from app.services.mermaid_generator import generate_mermaid_diagram
from app.services.migration_strategy import (
    generate_benefits,
    generate_drawbacks,
    generate_final_verdict as build_final_verdict,
    generate_migration_strategy as build_migration_strategy,
    generate_required_changes,
    generate_risks,
)
from app.services.report_generator import build_report
from app.services.service_detection import detect_source_architecture


class MigrationGraphState(TypedDict, total=False):
    file_bytes: bytes
    filename: str
    content_type: str | None
    source_provider: str
    target_provider: str
    migration_intent: str | None
    goals: list[str]
    diagram_ingestion: Any
    source_architecture: Any
    service_mappings: Any
    required_changes: list[str]
    target_architecture: Any
    mermaid_diagram: str
    migration_strategy: Any
    benefits: list[str]
    drawbacks: list[str]
    risks: Any
    assumptions: list[str]
    final_verdict: FinalVerdict
    report: MigrationAssessmentReport


def build_migration_graph():
    graph = StateGraph(MigrationGraphState)
    graph.add_node("ingest_diagram", ingest_diagram_node)
    graph.add_node("detect_source_architecture", detect_source_architecture_node)
    graph.add_node("map_services", map_services_node)
    graph.add_node("generate_target_architecture", generate_target_architecture_node)
    graph.add_node("generate_mermaid_diagram", generate_mermaid_diagram_node)
    graph.add_node("generate_migration_strategy", generate_migration_strategy_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("generate_final_verdict", generate_final_verdict_node)

    graph.add_edge(START, "ingest_diagram")
    graph.add_edge("ingest_diagram", "detect_source_architecture")
    graph.add_edge("detect_source_architecture", "map_services")
    graph.add_edge("map_services", "generate_target_architecture")
    graph.add_edge("generate_target_architecture", "generate_mermaid_diagram")
    graph.add_edge("generate_mermaid_diagram", "generate_migration_strategy")
    graph.add_edge("generate_migration_strategy", "generate_report")
    graph.add_edge("generate_report", "generate_final_verdict")
    graph.add_edge("generate_final_verdict", END)
    return graph.compile()


def ingest_diagram_node(state: MigrationGraphState) -> MigrationGraphState:
    ingestion = ingest_diagram_file(
        file_bytes=state["file_bytes"],
        filename=state.get("filename", "architecture-diagram"),
        content_type=state.get("content_type"),
    )
    return {"diagram_ingestion": ingestion}


async def detect_source_architecture_node(
    state: MigrationGraphState,
) -> MigrationGraphState:
    source_architecture = await detect_source_architecture(
        ingestion=state["diagram_ingestion"],
        source_provider=state.get("source_provider", "auto"),
        migration_intent=state.get("migration_intent"),
        goals=state.get("goals", []),
    )
    return {"source_architecture": source_architecture}


def map_services_node(state: MigrationGraphState) -> MigrationGraphState:
    service_mappings = map_services(
        source_architecture=state["source_architecture"],
        target_provider=state.get("target_provider", "aws"),
        migration_intent=state.get("migration_intent"),
        goals=state.get("goals", []),
    )
    return {"service_mappings": service_mappings}


def generate_target_architecture_node(state: MigrationGraphState) -> MigrationGraphState:
    target_architecture = generate_target_architecture(
        source_architecture=state["source_architecture"],
        service_mappings=state["service_mappings"],
        target_provider=state.get("target_provider", "aws"),
        goals=state.get("goals", []),
    )
    required_changes = generate_required_changes(
        source_architecture=state["source_architecture"],
        target_architecture=target_architecture,
        service_mappings=state["service_mappings"],
    )
    return {
        "target_architecture": target_architecture,
        "required_changes": required_changes,
    }


def generate_mermaid_diagram_node(state: MigrationGraphState) -> MigrationGraphState:
    mermaid_diagram = generate_mermaid_diagram(state["target_architecture"])
    return {"mermaid_diagram": mermaid_diagram}


def generate_migration_strategy_node(state: MigrationGraphState) -> MigrationGraphState:
    migration_strategy = build_migration_strategy(
        source_architecture=state["source_architecture"],
        target_architecture=state["target_architecture"],
        service_mappings=state["service_mappings"],
        goals=state.get("goals", []),
    )
    benefits = generate_benefits(
        target_architecture=state["target_architecture"],
        service_mappings=state["service_mappings"],
    )
    drawbacks = generate_drawbacks(
        source_architecture=state["source_architecture"],
        service_mappings=state["service_mappings"],
    )
    risks = generate_risks(
        source_architecture=state["source_architecture"],
        service_mappings=state["service_mappings"],
    )
    assumptions = [
        *state["source_architecture"].assumptions,
        *state["source_architecture"].missing_information,
    ]
    return {
        "migration_strategy": migration_strategy,
        "benefits": benefits,
        "drawbacks": drawbacks,
        "risks": risks,
        "assumptions": assumptions,
    }


def generate_report_node(state: MigrationGraphState) -> MigrationGraphState:
    provisional_verdict = FinalVerdict(
        recommendation="conditionally_recommended",
        reasoning=(
            "Initial report generated before final verdict scoring. "
            "The final workflow node will update this section."
        ),
        confidence=0.5,
    )
    report = _build_report_with_verdict(state, provisional_verdict)
    return {
        "final_verdict": provisional_verdict,
        "report": report,
    }


def generate_final_verdict_node(state: MigrationGraphState) -> MigrationGraphState:
    final_verdict = build_final_verdict(
        source_architecture=state["source_architecture"],
        service_mappings=state["service_mappings"],
        risks=state["risks"],
        benefits=state["benefits"],
        drawbacks=state["drawbacks"],
    )
    report = _build_report_with_verdict(state, final_verdict)
    return {
        "final_verdict": final_verdict,
        "report": report,
    }


async def run_migration_assessment(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
    source_provider: str = "auto",
    target_provider: str = "aws",
    migration_intent: str | None = None,
    goals: list[str] | None = None,
) -> MigrationAssessmentReport:
    graph = build_migration_graph()
    final_state = await graph.ainvoke(
        {
            "file_bytes": file_bytes,
            "filename": filename,
            "content_type": content_type,
            "source_provider": source_provider,
            "target_provider": target_provider,
            "migration_intent": migration_intent,
            "goals": goals or [],
        }
    )
    return final_state["report"]


def _build_report_with_verdict(
    state: MigrationGraphState,
    final_verdict: FinalVerdict,
) -> MigrationAssessmentReport:
    return build_report(
        source_architecture=state["source_architecture"],
        service_mappings=state["service_mappings"],
        required_changes=state["required_changes"],
        target_architecture=state["target_architecture"],
        mermaid_diagram=state["mermaid_diagram"],
        migration_strategy=state["migration_strategy"],
        benefits=state["benefits"],
        drawbacks=state["drawbacks"],
        risks=state["risks"],
        assumptions=state["assumptions"],
        final_verdict=final_verdict,
        analysis_metadata=state["diagram_ingestion"].metadata,
    )
