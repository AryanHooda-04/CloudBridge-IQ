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
