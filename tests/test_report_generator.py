from app.schemas import (
    ArchitectureComponent,
    FinalVerdict,
    MigrationPhase,
    MigrationRisk,
    ServiceMapping,
    SourceArchitecture,
    TargetArchitecture,
)
from app.services.report_generator import build_report


def test_report_contains_required_sections_and_mapping_table():
    source = SourceArchitecture(
        provider="azure",
        summary="Azure App Service backed by Azure SQL Database.",
        components=[
            ArchitectureComponent(
                id="app",
                name="Azure App Service",
                provider="azure",
                category="compute",
                confidence=0.9,
            )
        ],
        relationships=[],
    )
    mappings = [
        ServiceMapping(
            source_service="Azure App Service",
            target_service="AWS Elastic Beanstalk",
            reasoning="Managed app hosting fit.",
            confidence=0.86,
        )
    ]
    target = TargetArchitecture(
        provider="aws",
        summary="AWS target design.",
        components=[],
        relationships=[],
        design_notes=["Use private subnets."],
    )
    phase = MigrationPhase(
        phase="1. Discovery",
        goals=["Validate scope"],
        activities=["Review dependencies"],
        deliverables=["Inventory"],
        risks=["Hidden dependency"],
        success_criteria=["Inventory approved"],
    )
    risk = MigrationRisk(
        title="Data migration",
        severity="medium",
        description="Data consistency must be validated.",
        mitigation="Rehearse migration.",
    )
    verdict = FinalVerdict(
        recommendation="conditionally_recommended",
        reasoning="Proceed after validation.",
        confidence=0.78,
    )

    report = build_report(
        source_architecture=source,
        service_mappings=mappings,
        required_changes=["Rebuild networking."],
        target_architecture=target,
        mermaid_diagram="graph TD\n    A --> B",
        migration_strategy=[phase],
        benefits=["Managed operations."],
        drawbacks=["Migration complexity."],
        risks=[risk],
        assumptions=["Diagram lacks runtime telemetry."],
        final_verdict=verdict,
    )

    markdown = report.markdown_report
    assert "# Cloud Migration Assessment Report" in markdown
    assert "## 1. Executive Summary" in markdown
    assert "## 4. Source-to-Target Cloud Service Mapping" in markdown
    assert "## 7. AWS Architecture Diagram" in markdown
    assert "## 15. Final Verdict" in markdown
    assert "| Recommendation | Confidence | Source | Target | Scope |" in markdown
    assert "| Source Service | Target AWS Service | Reasoning | Confidence |" in markdown
    assert "| Azure App Service | AWS Elastic Beanstalk |" in markdown
    assert "```mermaid" in markdown
