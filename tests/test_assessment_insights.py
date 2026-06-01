from app.schemas import (
    ArchitectureComponent,
    FinalVerdict,
    MigrationAssessmentReport,
    MigrationPhase,
    MigrationRisk,
    ServiceMapping,
    SourceArchitecture,
    TargetArchitecture,
)
from app.services.assessment_insights import build_assessment_insights


def test_assessment_insights_include_dashboard_planning_and_review_items():
    report = MigrationAssessmentReport(
        executive_summary="Azure hybrid network migration.",
        source_architecture=SourceArchitecture(
            provider="azure",
            summary="ExpressRoute and VPN gateway connected to an Azure virtual network.",
            components=[
                ArchitectureComponent(
                    id="er",
                    name="ExpressRoute circuit",
                    provider="azure",
                    service_type="Azure ExpressRoute",
                    category="networking",
                    confidence=0.9,
                ),
                ArchitectureComponent(
                    id="db",
                    name="Azure SQL Database",
                    provider="azure",
                    service_type="Azure SQL Database",
                    category="database",
                    confidence=0.85,
                ),
            ],
            relationships=[],
            missing_information=["No runtime dependency list provided."],
        ),
        service_mappings=[
            ServiceMapping(
                source_service="Azure ExpressRoute",
                target_service="AWS Direct Connect",
                reasoning="Dedicated private connectivity.",
                confidence=0.82,
            ),
            ServiceMapping(
                source_service="Azure SQL Database",
                target_service="Amazon RDS",
                reasoning="Managed relational database migration.",
                confidence=0.86,
            ),
        ],
        required_changes=["Rebuild hybrid routing with Transit Gateway."],
        target_architecture=TargetArchitecture(
            provider="aws",
            summary="AWS VPC with Direct Connect and RDS.",
            components=[
                ArchitectureComponent(
                    id="dx",
                    name="AWS Direct Connect",
                    provider="aws",
                    category="networking",
                    confidence=0.86,
                ),
                ArchitectureComponent(
                    id="rds",
                    name="Amazon RDS",
                    provider="aws",
                    category="database",
                    confidence=0.86,
                ),
            ],
            relationships=[],
            design_notes=["Use CloudWatch, IAM, KMS, and Backup."],
        ),
        mermaid_diagram="graph TD\nA-->B",
        migration_strategy=[
            MigrationPhase(
                phase="1. Discovery",
                goals=["Validate scope"],
                activities=["Review inventory"],
                deliverables=["Inventory"],
                risks=["Unknown dependency"],
                success_criteria=["Inventory approved"],
            )
        ],
        benefits=["Operational consistency."],
        drawbacks=["Migration complexity."],
        risks=[
            MigrationRisk(
                title="Data migration",
                severity="high",
                description="Data consistency risk.",
                mitigation="Rehearse migration.",
            )
        ],
        assumptions=["No dependency list provided."],
        final_verdict=FinalVerdict(
            recommendation="conditionally_recommended",
            reasoning="Proceed after validation.",
            confidence=0.78,
        ),
        markdown_report="# Report\n",
    )

    insights = build_assessment_insights(report, goals=["compliance"])

    assert insights["scores"]["overall_readiness"]["value"] > 0
    assert insights["effort"]["t_shirt_size"] in {"medium", "large", "complex"}
    assert insights["planning"]["rollback_plan"]
    assert insights["planning"]["cutover_plan"]
    assert insights["cost"]["cost_drivers"]
    assert insights["review"]["decision_gate_checklist"]


def test_assessment_insights_avoid_zero_score_cliffs_for_reviewable_assessments():
    missing = [
        "Runtime dependency list not provided.",
        "Traffic profile not provided.",
        "Data volume not provided.",
        "Rollback window not provided.",
    ]
    mappings = [
        ServiceMapping(
            source_service=f"Source service {index}",
            target_service=f"Target service {index}",
            reasoning="Requires architect validation.",
            confidence=0.42 if index < 10 else 0.82,
        )
        for index in range(13)
    ]
    risks = [
        MigrationRisk(
            title="Data cutover",
            severity="high",
            description="Stateful services need migration rehearsal.",
            mitigation="Run data sync and reconciliation tests.",
        ),
        MigrationRisk(
            title="Network routing",
            severity="high",
            description="Private routing and rollback behavior need validation.",
            mitigation="Test route failover before production.",
        ),
    ]
    report = MigrationAssessmentReport(
        executive_summary="Reviewable Azure migration with unresolved inputs.",
        source_architecture=SourceArchitecture(
            provider="azure",
            summary="Application, database, and storage services.",
            components=[
                ArchitectureComponent(
                    id=f"source_{index}",
                    name=f"Source component {index}",
                    provider="azure",
                    service_type=f"Source service {index}",
                    category="database" if index % 4 == 0 else "compute",
                    confidence=0.7,
                )
                for index in range(13)
            ],
            relationships=[],
            missing_information=missing,
        ),
        service_mappings=mappings,
        required_changes=["Validate service mappings and data migration runbooks."],
        target_architecture=TargetArchitecture(
            provider="azure",
            summary="Target Azure architecture.",
            components=[
                ArchitectureComponent(
                    id=f"target_{index}",
                    name=f"Target component {index}",
                    provider="azure",
                    category="database" if index % 4 == 0 else "compute",
                    confidence=0.7,
                )
                for index in range(16)
            ],
            relationships=[],
            design_notes=["Use Azure Monitor, Key Vault, and private networking."],
        ),
        mermaid_diagram="graph TD\nA-->B",
        migration_strategy=[],
        benefits=["Target platform consistency."],
        drawbacks=["Several mappings need validation."],
        risks=risks,
        assumptions=missing,
        final_verdict=FinalVerdict(
            recommendation="conditionally_recommended",
            reasoning="Proceed after validation.",
            confidence=0.72,
        ),
        markdown_report="# Report\n",
    )

    scores = build_assessment_insights(report, goals=["compliance"])["scores"]

    assert scores["technical_feasibility"]["value"] > 0
    assert scores["operational_readiness"]["value"] > 0
    assert scores["cost_predictability"]["value"] > 0
    assert scores["downtime_risk"]["value"] < 100
    assert scores["overall_readiness"]["value"] >= 35
