"""Markdown report generation for migration assessments."""

from __future__ import annotations

import re

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


def build_report(
    *,
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
    required_changes: list[str],
    target_architecture: TargetArchitecture,
    mermaid_diagram: str,
    migration_strategy: list[MigrationPhase],
    benefits: list[str],
    drawbacks: list[str],
    risks: list[MigrationRisk],
    assumptions: list[str],
    final_verdict: FinalVerdict,
    analysis_metadata: dict | None = None,
) -> MigrationAssessmentReport:
    executive_summary = _executive_summary(
        source_architecture=source_architecture,
        target_architecture=target_architecture,
        final_verdict=final_verdict,
    )
    report = MigrationAssessmentReport(
        executive_summary=executive_summary,
        source_architecture=source_architecture,
        service_mappings=service_mappings,
        required_changes=required_changes,
        target_architecture=target_architecture,
        mermaid_diagram=mermaid_diagram,
        migration_strategy=migration_strategy,
        benefits=benefits,
        drawbacks=drawbacks,
        risks=risks,
        assumptions=assumptions,
        final_verdict=final_verdict,
        markdown_report="",
        analysis_metadata=analysis_metadata or {},
    )
    report.markdown_report = render_markdown_report(report)
    return report


def render_markdown_report(report: MigrationAssessmentReport) -> str:
    """Render a compact, enterprise-oriented assessment report."""

    target_label = _pretty_provider(report.target_architecture.provider)
    target_service_header = f"Target {target_label} Service"
    lines: list[str] = [
        "# Cloud Migration Assessment Report",
        "",
        "## 1. Executive Summary",
        "",
        "| Recommendation | Confidence | Source | Target | Scope |",
        "|---|---:|---|---|---:|",
        (
            f"| **{_pretty_verdict(report.final_verdict.recommendation)}** "
            f"| {report.final_verdict.confidence:.0%} "
            f"| {_pretty_provider(report.source_architecture.provider)} "
            f"| {report.target_architecture.provider.upper()} "
            f"| {_scope_summary(report)} |"
        ),
        "",
        f"**Bottom line:** {report.final_verdict.reasoning}",
        "",
        report.executive_summary,
        "",
        "## 2. Source Architecture Understanding",
        "",
        f"- **Provider:** {_pretty_provider(report.source_architecture.provider)}",
        f"- **Architecture summary:** {report.source_architecture.summary}",
        f"- **Detected components:** {len(report.source_architecture.components)}",
        f"- **Detected relationships:** {len(report.source_architecture.relationships)}",
        "",
        "## 3. Detected Services and Components",
        "",
        "| Component | Category | Confidence | Notes |",
        "|---|---|---:|---|",
        *_component_rows(report.source_architecture.components, limit=12),
        "",
        "## 4. Source-to-Target Cloud Service Mapping",
        "",
        f"| Source Service | {target_service_header} | Reasoning | Confidence |",
        "|---|---|---|---|",
        *_mapping_rows(report.service_mappings),
        "",
        "## 5. Required Architecture Changes",
        "",
        *_bullet_lines(_limit_list(report.required_changes, 8)),
        "",
        f"## 6. Proposed {target_label} Architecture",
        "",
        f"**Target pattern:** {report.target_architecture.summary}",
        "",
        *_bullet_lines(_limit_list(report.target_architecture.design_notes, 8)),
        "",
        f"## 7. {target_label} Architecture Diagram",
        "",
        "```mermaid",
        _clean_mermaid(report.mermaid_diagram),
        "```",
        "",
        "## 8. Migration Strategy",
        "",
        "| Phase | Focus | Key Deliverables | Success Criteria |",
        "|---|---|---|---|",
        *_phase_table_rows(report.migration_strategy),
        "",
        "## 9. Data Migration Plan",
        "",
        *_bullet_lines(_limit_list(_data_migration_plan(report.service_mappings), 6)),
        "",
        "## 10. Security and Compliance Considerations",
        "",
        *_bullet_lines(_security_considerations(report.target_architecture.provider)),
        "",
        "## 11. Cost and Operational Impact",
        "",
        *_bullet_lines(_cost_and_operational_impact(report.target_architecture.provider)),
        "",
        "## 12. Benefits of Migration",
        "",
        *_bullet_lines(_limit_list(report.benefits, 6)),
        "",
        "## 13. Drawbacks and Risks",
        "",
        "**Drawbacks**",
        "",
        *_bullet_lines(_limit_list(report.drawbacks, 5)),
        "",
        "**Risks**",
        "",
        "| Risk | Severity | Mitigation |",
        "|---|---|---|",
        *_risk_table_rows(report.risks),
        "",
        "## 14. Assumptions and Missing Information",
        "",
        *_assumption_lines(report),
        "",
        "## 15. Final Verdict",
        "",
        f"**Recommendation:** {_pretty_verdict(report.final_verdict.recommendation)}",
        "",
        f"**Confidence:** {report.final_verdict.confidence:.0%}",
        "",
        f"**Reasoning:** {report.final_verdict.reasoning}",
        "",
        f"**Decision gate:** {_decision_gate(report.final_verdict)}",
        "",
    ]
    return "\n".join(lines).strip() + "\n"


def _executive_summary(
    source_architecture: SourceArchitecture,
    target_architecture: TargetArchitecture,
    final_verdict: FinalVerdict,
) -> str:
    return (
        f"The uploaded architecture appears to describe a "
        f"{_pretty_provider(source_architecture.provider)} environment. "
        f"The proposed target is {_pretty_provider(target_architecture.provider)} with a production-oriented design. "
        f"Current recommendation: {_pretty_verdict(final_verdict.recommendation)}."
    )


def _component_rows(components: list[ArchitectureComponent], limit: int = 12) -> list[str]:
    if not components:
        return ["| No components detected | Unknown | 0% | Manual architecture validation required |"]

    selected_components = components[:limit]
    rows = [
        (
            f"| {_table_cell(component.name)} "
            f"| {_table_cell(component.category or component.service_type or 'Uncategorized')} "
            f"| {component.confidence:.0%} "
            f"| {_table_cell(_compact_text(component.description or 'Detected from uploaded diagram.', 120))} |"
        )
        for component in selected_components
    ]
    remaining = len(components) - len(selected_components)
    if remaining > 0:
        rows.append(
            f"| Additional components | Mixed | - | {remaining} more detected; see JSON for full detail |"
        )
    return rows


def _mapping_rows(service_mappings: list[ServiceMapping]) -> list[str]:
    if not service_mappings:
        return ["| No services detected | Manual assessment required | No mapping available | 0% |"]
    return [
        (
            f"| {_table_cell(mapping.source_service)} "
            f"| {_table_cell(mapping.target_service)} "
            f"| {_table_cell(_compact_text(mapping.reasoning, 190))} "
            f"| {mapping.confidence:.0%} |"
        )
        for mapping in service_mappings
    ]


def _phase_table_rows(phases: list[MigrationPhase]) -> list[str]:
    if not phases:
        return ["| Migration planning | Validate scope | Migration plan | Architecture owner approval |"]

    rows: list[str] = []
    for phase in phases:
        clean_phase = re.sub(r"^\d+\.\s*", "", phase.phase)
        rows.append(
            "| "
            + " | ".join(
                [
                    _table_cell(clean_phase),
                    _table_cell(_compact_text("; ".join(phase.goals[:2]), 120)),
                    _table_cell(_compact_text("; ".join(phase.deliverables[:2]), 120)),
                    _table_cell(_compact_text("; ".join(phase.success_criteria[:1]), 140)),
                ]
            )
            + " |"
        )
    return rows


def _risk_table_rows(risks: list[MigrationRisk]) -> list[str]:
    if not risks:
        return ["| No major risks identified | Low | Continue architecture validation |"]
    return [
        (
            f"| {_table_cell(risk.title)} "
            f"| {risk.severity.title()} "
            f"| {_table_cell(_compact_text(risk.mitigation, 170))} |"
        )
        for risk in risks[:6]
    ]


def _assumption_lines(report: MigrationAssessmentReport) -> list[str]:
    items: list[str] = []
    items.extend(report.assumptions)
    items.extend(report.source_architecture.assumptions)
    items.extend(f"Missing information: {item}" for item in report.source_architecture.missing_information)
    if not items:
        return ["- No major assumptions or missing information were captured."]
    return _bullet_lines(_limit_list(items, 10))


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None identified."]


def _limit_list(items: list[str], limit: int) -> list[str]:
    if len(items) <= limit:
        return items
    return [*items[:limit], f"{len(items) - limit} additional item(s) available in JSON output."]


def _data_migration_plan(service_mappings: list[ServiceMapping]) -> list[str]:
    plan = [
        "Classify data by owner, sensitivity, size, RPO/RTO, retention, and acceptable downtime.",
        "Select migration tooling per data platform; rehearse in non-production before cutover.",
        "Use incremental replication or staged export/import where downtime tolerance is limited.",
        "Define freeze windows, rollback checkpoints, reconciliation checks, and post-cutover validation.",
    ]
    for mapping in service_mappings:
        if any(
            token in mapping.target_service.lower()
            for token in ["rds", "aurora", "dynamodb", "documentdb", "s3"]
        ):
            plan.append(
                f"Create a service-specific runbook for {mapping.source_service} to {mapping.target_service}."
            )
    return plan


def _security_considerations(target_provider: str) -> list[str]:
    identity, keys, secrets, network = _control_labels(target_provider)
    return [
        f"Map source roles and policies to least-privilege {identity}, permission boundaries, and break-glass access.",
        f"Use {keys} for encryption keys and {secrets} for application secrets and rotation.",
        f"Recreate segmentation with {network}, subnets, route tables, firewall/security rules, private endpoints, and controlled ingress.",
        "Validate audit logging, compliance evidence, vulnerability management, and incident response integrations.",
    ]


def _cost_and_operational_impact(target_provider: str) -> list[str]:
    target = _pretty_provider(target_provider)
    return [
        f"Estimate {target} cost from measured utilization, traffic, data transfer, storage growth, backup retention, and support needs.",
        "Expect temporary dual-run cost during migration waves until source resources are decommissioned.",
        "Right-size after performance testing; evaluate provider-native commitments, reservations, and storage lifecycle policies.",
        f"Plan team readiness for {target} operations, deployment, observability, incident response, and security controls.",
    ]


def _control_labels(target_provider: str) -> tuple[str, str, str, str]:
    provider = (target_provider or "").lower()
    if "azure" in provider:
        return (
            "Microsoft Entra ID and Azure RBAC",
            "Azure Key Vault keys",
            "Azure Key Vault",
            "Azure Virtual Network",
        )
    if "gcp" in provider or "google" in provider:
        return ("Cloud IAM", "Cloud KMS", "Secret Manager", "VPC Network")
    return ("AWS IAM roles", "AWS KMS", "AWS Secrets Manager", "VPCs")


def _decision_gate(final_verdict: FinalVerdict) -> str:
    if final_verdict.recommendation == "recommended":
        return "Proceed to detailed design, cost validation, and migration wave planning."
    if final_verdict.recommendation == "not_recommended":
        return "Do not proceed until the blocking business, security, cost, or technical issues are resolved."
    return "Proceed only after architecture validation, cost modeling, security review, and cutover rehearsal."


def _scope_summary(report: MigrationAssessmentReport) -> str:
    component_count = len(report.source_architecture.components)
    mapping_count = len(report.service_mappings)
    return f"{component_count} {_plural('component', component_count)} / {mapping_count} {_plural('mapping', mapping_count)}"


def _plural(noun: str, count: int) -> str:
    return noun if count == 1 else f"{noun}s"


def _clean_mermaid(mermaid_diagram: str) -> str:
    diagram = mermaid_diagram.strip()
    if diagram.startswith("```"):
        diagram = re.sub(r"^```(?:mermaid)?\s*", "", diagram, flags=re.IGNORECASE)
        diagram = re.sub(r"\s*```$", "", diagram)
    return diagram


def _pretty_verdict(value: str) -> str:
    return value.replace("_", " ").title()


def _pretty_provider(provider: str) -> str:
    aliases = {
        "aws": "AWS",
        "azure": "Microsoft Azure",
        "gcp": "Google Cloud",
        "unknown": "Unknown",
    }
    return aliases.get(provider.lower(), provider)


def _compact_text(value: str, limit: int) -> str:
    compact = " ".join(str(value or "Not specified.").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _table_cell(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()
