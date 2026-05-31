"""Deterministic assessment insights for the migration console UI."""

from __future__ import annotations

from statistics import mean
from typing import Any

from app.schemas import MigrationAssessmentReport, MigrationRisk, ServiceMapping


def build_assessment_insights(
    report: MigrationAssessmentReport,
    goals: list[str] | None = None,
) -> dict[str, Any]:
    """Build dashboard-ready migration insights from the structured report.

    These values are intentionally deterministic. They give the UI a stable
    decision dashboard and can later be replaced or enriched with a formal
    rules engine, inventory data, or cloud cost APIs.
    """

    goals = goals or []
    target_label = _provider_label(report.target_architecture.provider)
    mappings = report.service_mappings
    risks = report.risks
    component_text = _report_text(report)
    source_components = len(report.source_architecture.components)
    target_components = len(report.target_architecture.components)
    avg_confidence = _average_mapping_confidence(mappings)
    low_confidence_count = sum(1 for mapping in mappings if mapping.confidence < 0.55)
    severity_counts = _severity_counts(risks)

    has_hybrid = _contains_any(
        component_text,
        [
            "direct connect",
            "expressroute",
            "site-to-site vpn",
            "transit gateway",
            "customer gateway",
            "vpn gateway",
        ],
    )
    has_data = _contains_any(
        component_text,
        [
            "database",
            "sql",
            "cosmos",
            "bigquery",
            "redshift",
            "dynamodb",
            "rds",
            "aurora",
            "datastore",
            "storage",
            "s3",
        ],
    )
    has_streaming = _contains_any(
        component_text,
        ["pub/sub", "pubsub", "eventbridge", "kinesis", "stream", "iot", "dataflow"],
    )
    has_compliance_goal = _contains_any(" ".join(goals), ["compliance", "audit", "regulated", "security"])
    unknowns = len(report.assumptions) + len(report.source_architecture.missing_information)

    complexity_points = (
        (source_components // 4)
        + (target_components // 6)
        + low_confidence_count
        + severity_counts["high"] * 2
        + severity_counts["critical"] * 3
        + (2 if has_hybrid else 0)
        + (2 if has_data else 0)
        + (1 if has_streaming else 0)
        + min(3, unknowns)
    )

    technical_score = _clamp_score(
        90
        - complexity_points * 3
        - low_confidence_count * 6
        - severity_counts["high"] * 5
        - severity_counts["critical"] * 10
        + int(avg_confidence * 8)
    )
    security_score = _clamp_score(
        78
        + _security_control_bonus(report) * 3
        - severity_counts["critical"] * 10
        - severity_counts["high"] * 4
        - (6 if has_compliance_goal and unknowns else 0)
    )
    operational_score = _clamp_score(
        82
        - complexity_points * 2
        - low_confidence_count * 5
        - unknowns * 2
        + _operations_control_bonus(report) * 2
    )
    cost_predictability_score = _clamp_score(
        76
        - complexity_points * 3
        - low_confidence_count * 6
        - (8 if has_data else 0)
        - (5 if has_hybrid else 0)
    )
    downtime_risk_score = _clamp_score(
        28
        + complexity_points * 3
        + (12 if has_data else 0)
        + (8 if has_hybrid else 0)
        + severity_counts["high"] * 4
        + severity_counts["critical"] * 8
    )
    compliance_score = _clamp_score(
        74
        + _security_control_bonus(report) * 2
        - unknowns * 3
        - (
            6
            if has_compliance_goal
            and not _contains_any(
                component_text,
                ["cloudtrail", "kms", "iam", "key vault", "entra", "cloud logging", "cloud audit"],
            )
            else 0
        )
    )
    overall_readiness = _clamp_score(
        round(
            mean(
                [
                    technical_score,
                    security_score,
                    operational_score,
                    cost_predictability_score,
                    compliance_score,
                    100 - downtime_risk_score,
                ]
            )
        )
    )

    return {
        "scores": {
            "overall_readiness": _score(
                overall_readiness,
                "Overall readiness",
                "Composite of feasibility, risk, cost certainty, and operational maturity.",
            ),
            "technical_feasibility": _score(
                technical_score,
                "Technical feasibility",
                f"How cleanly the source services and topology can be represented in {target_label}.",
            ),
            "security_readiness": _score(
                security_score,
                "Security readiness",
                "Coverage of IAM, encryption, secrets, logging, and review requirements.",
            ),
            "operational_readiness": _score(
                operational_score,
                "Operational readiness",
                "Maturity of monitoring, backup, runbooks, deployment, and ownership signals.",
            ),
            "cost_predictability": _score(
                cost_predictability_score,
                "Cost predictability",
                f"Confidence that {target_label} run-rate and migration costs can be estimated accurately.",
            ),
            "downtime_risk": _risk_score(
                downtime_risk_score,
                "Downtime risk",
                "Likelihood that cutover, data movement, or routing changes create service interruption.",
            ),
            "compliance_readiness": _score(
                compliance_score,
                "Compliance readiness",
                "Evidence that audit, identity, encryption, and traceability controls are covered.",
            ),
        },
        "effort": _effort(
            complexity_points=complexity_points,
            has_data=has_data,
            has_hybrid=has_hybrid,
            has_streaming=has_streaming,
            low_confidence_count=low_confidence_count,
            source_components=source_components,
            target_components=target_components,
            unknowns=unknowns,
            report=report,
            target_label=target_label,
        ),
        "cost": _cost_insights(
            report,
            has_data=has_data,
            has_hybrid=has_hybrid,
            has_streaming=has_streaming,
            target_label=target_label,
        ),
        "planning": _planning_insights(report, has_data=has_data, has_hybrid=has_hybrid, has_streaming=has_streaming),
        "review": _review_insights(
            report=report,
            overall_readiness=overall_readiness,
            has_data=has_data,
            has_hybrid=has_hybrid,
            unknowns=unknowns,
            low_confidence_count=low_confidence_count,
            target_label=target_label,
        ),
    }


def _effort(
    *,
    complexity_points: int,
    has_data: bool,
    has_hybrid: bool,
    has_streaming: bool,
    low_confidence_count: int,
    source_components: int,
    target_components: int,
    unknowns: int,
    report: MigrationAssessmentReport,
    target_label: str,
) -> dict[str, Any]:
    if complexity_points <= 4:
        size = "small"
        effort = "Focused migration with limited redesign."
    elif complexity_points <= 8:
        size = "medium"
        effort = "Moderate migration requiring validated planning and rehearsals."
    elif complexity_points <= 13:
        size = "large"
        effort = "Large migration with multiple workstreams and dependency management."
    else:
        size = "complex"
        effort = "Complex migration requiring formal program governance and staged cutover."

    drivers = []
    if source_components >= 8 or target_components >= 10:
        drivers.append("Multiple architecture components and service workstreams.")
    if has_hybrid:
        drivers.append("Hybrid network routing, failover, and BGP validation.")
    if has_data:
        drivers.append("Data migration, reconciliation, backup, and rollback planning.")
    if has_streaming:
        drivers.append("Event or streaming ingestion patterns with consumer behavior differences.")
    if low_confidence_count:
        drivers.append(f"{low_confidence_count} low-confidence service mapping item(s).")
    if unknowns:
        drivers.append(f"{unknowns} assumption or missing-information item(s) to close.")
    if not drivers:
        drivers.append("Scope appears contained based on the uploaded diagram.")

    return {
        "t_shirt_size": size,
        "migration_effort": effort,
        "complexity_drivers": drivers,
        "dual_run_warning": (
            "Plan for temporary dual-run costs during replication, test environments, parallel monitoring, "
            "and rollback windows."
        ),
        "skill_readiness_gaps": _skill_gaps(
            report,
            has_data=has_data,
            has_hybrid=has_hybrid,
            has_streaming=has_streaming,
            target_label=target_label,
        ),
    }


def _cost_insights(
    report: MigrationAssessmentReport,
    *,
    has_data: bool,
    has_hybrid: bool,
    has_streaming: bool,
    target_label: str,
) -> dict[str, Any]:
    text = _report_text(report)
    drivers = [f"{target_label} compute sizing, autoscaling policy, and environment count."]
    if _contains_any(text, ["s3", "storage", "blob", "cloud storage"]):
        drivers.append("Object storage volume, request patterns, lifecycle policy, and retrieval tier.")
    if has_data:
        drivers.append("Database or warehouse size, IOPS, replication duration, backup retention, and license model.")
    if has_hybrid:
        drivers.append("Direct Connect port speed, data transfer, VPN backup, and redundant connectivity.")
    if has_streaming:
        drivers.append("Streaming throughput, retention, delivery fanout, and replay requirements.")
    if _contains_any(text, ["cloudwatch", "opensearch", "logging"]):
        drivers.append("Log ingestion, metric cardinality, trace volume, and retention period.")

    return {
        "cost_drivers": _unique(drivers),
        "optimization_levers": [
            "Right-size after performance testing and enable autoscaling where workload patterns vary.",
            "Use storage lifecycle policies and retention rules before production data migration.",
            "Separate baseline run-rate from one-time migration, testing, and dual-run costs.",
            "Evaluate provider-native reservations, committed-use discounts, savings plans, or managed service commitments after the steady-state design is proven.",
        ],
        "estimation_notes": [
            "Treat this as a directional estimate until inventory, traffic, data size, and SLA inputs are confirmed.",
            "Include network egress, observability, backup, and cross-cloud parallel-run costs in the first model.",
        ],
    }


def _planning_insights(
    report: MigrationAssessmentReport,
    *,
    has_data: bool,
    has_hybrid: bool,
    has_streaming: bool,
) -> dict[str, Any]:
    target_label = _provider_label(report.target_architecture.provider)
    waves = [
        {
            "wave": "Wave 0 - Readiness",
            "scope": "Inventory validation, dependency discovery, landing zone readiness, and security baseline.",
            "dependencies": "Source inventory, owners, network ranges, compliance requirements.",
            "exit_criteria": "All critical unknowns have owners, evidence, and acceptance criteria.",
        },
        {
            "wave": "Wave 1 - Foundation",
            "scope": f"{target_label} accounts/projects/subscriptions, network, identity, key management, logging, monitoring, backup, and deployment pipelines.",
            "dependencies": "Landing zone decisions, naming/tagging standards, access model.",
            "exit_criteria": "Connectivity, guardrails, observability, and backup checks pass.",
        },
    ]
    if has_hybrid:
        waves.append(
            {
                "wave": "Wave 2 - Connectivity",
                "scope": "Direct Connect or VPN, BGP, Transit Gateway, route tables, and failover tests.",
                "dependencies": "Customer routers, ASN/IP plan, routing policy, Direct Connect/VPN readiness.",
                "exit_criteria": "Primary and backup routes fail over predictably without asymmetric routing.",
            }
        )
    if has_data:
        waves.append(
            {
                "wave": "Wave 3 - Data",
                "scope": "Data replication, validation, backup restore testing, and reconciliation.",
                "dependencies": "Schema inventory, data size, RPO/RTO, migration tooling, retention policy.",
                "exit_criteria": "Reconciliation thresholds and rollback checkpoints are approved.",
            }
        )
    if has_streaming:
        waves.append(
            {
                "wave": "Wave 4 - Event and Streaming",
                "scope": "Ingestion, queues/event buses, stream consumers, replay, retry, and DLQ behavior.",
                "dependencies": "Message contracts, throughput profile, consumer ownership, error policy.",
                "exit_criteria": "Consumer tests prove ordering, retries, replay, and failure handling.",
            }
        )
    waves.append(
        {
            "wave": "Final Wave - Cutover",
            "scope": "Traffic shift, smoke tests, hypercare, cost validation, and source decommission planning.",
            "dependencies": "Approved runbooks, rollback window, stakeholder signoff.",
            "exit_criteria": f"{target_label} service health and business KPIs meet the agreed acceptance window.",
        }
    )

    return {
        "waves": waves,
        "dependencies": _unique(
            [
                "Application owner approval and source-cloud inventory export.",
                "Network ranges, DNS/TLS ownership, identity model, and environment strategy.",
                f"Infrastructure-as-code and CI/CD access for repeatable {target_label} builds.",
                "Security, backup, monitoring, and incident response acceptance criteria.",
            ]
            + (["Data classification, schema inventory, and reconciliation thresholds."] if has_data else [])
            + (["Routing policy, BGP parameters, and failover test windows."] if has_hybrid else [])
        ),
        "cutover_plan": [
            "Freeze high-risk changes before cutover and verify rollback checkpoints.",
            "Run final data sync or configuration promotion using a rehearsed checklist.",
            "Shift traffic through DNS, load balancer, routing, or application release controls.",
            "Run smoke tests, synthetic checks, business transaction checks, and monitoring review.",
            "Hold a hypercare window with owners for application, network, data, and security.",
        ],
        "rollback_plan": [
            "Define a time-boxed rollback window before data divergence becomes hard to reverse.",
            "Keep source environment operational until acceptance criteria are met.",
            "Preserve DNS/routing rollback steps and application configuration snapshots.",
            "Document data rollback or compensating transaction approach for every stateful service.",
        ],
        "data_migration_approach": _data_migration_approach(report, has_data=has_data),
    }


def _review_insights(
    *,
    report: MigrationAssessmentReport,
    overall_readiness: int,
    has_data: bool,
    has_hybrid: bool,
    unknowns: int,
    low_confidence_count: int,
    target_label: str,
) -> dict[str, Any]:
    checklist = [
        _gate("Architecture inventory validated", unknowns == 0, "Close assumptions and missing information."),
        _gate("Service mappings architect-reviewed", low_confidence_count == 0, "Review low-confidence mappings and alternatives."),
        _gate("Security controls mapped", _security_control_bonus(report) >= 2, "Validate identity, key management, secrets, logging, and guardrails."),
        _gate("Cost model prepared", False, f"Attach a workload-based {target_label} estimate before approval."),
        _gate("Rollback plan documented", True, "Use the rollback checklist in the migration plan."),
    ]
    if has_data:
        checklist.append(
            _gate("Data migration rehearsed", False, "Run migration rehearsal and reconciliation before cutover.")
        )
    if has_hybrid:
        checklist.append(
            _gate("Network failover tested", False, "Test Direct Connect/VPN or route failover before production.")
        )

    warnings = []
    if overall_readiness < 65:
        warnings.append("Readiness score is below approval threshold; treat as pre-assessment until blockers are closed.")
    if unknowns:
        warnings.append("Assumptions and missing information materially reduce confidence.")
    if low_confidence_count:
        warnings.append("Low-confidence mappings require review before implementation planning.")
    if report.final_verdict.recommendation != "recommended":
        warnings.append("Final verdict is conditional or negative; run decision-gate review before signoff.")

    return {
        "decision_gate_checklist": checklist,
        "architect_notes": [
            "Review the generated target architecture as a starting point, not a final approved design.",
            "Confirm service limits, regional availability, identity boundaries, logging retention, and DR targets.",
            "Validate data gravity, latency, and egress assumptions before cost and schedule commitments.",
        ],
        "suggested_next_actions": [
            "Correct detected components if the AI missed or misnamed services.",
            "Pick an architecture variant and rerun the assessment for a cleaner target pattern.",
            "Attach inventory, traffic, data size, RPO/RTO, and compliance inputs to improve confidence.",
            "Run an architect review and mark the assessment reviewed before exporting the final PDF.",
        ],
        "warnings": warnings,
    }


def _score(value: int, label: str, description: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "status": _score_status(value),
        "description": description,
    }


def _risk_score(value: int, label: str, description: str) -> dict[str, Any]:
    if value <= 35:
        status = "good"
    elif value <= 60:
        status = "watch"
    else:
        status = "risk"
    return {
        "label": label,
        "value": value,
        "status": status,
        "description": description,
    }


def _score_status(value: int) -> str:
    if value >= 78:
        return "good"
    if value >= 60:
        return "watch"
    return "risk"


def _gate(item: str, ready: bool, evidence: str) -> dict[str, str]:
    return {
        "item": item,
        "status": "ready" if ready else "required",
        "evidence": evidence,
    }


def _average_mapping_confidence(mappings: list[ServiceMapping]) -> float:
    if not mappings:
        return 0.45
    return mean(mapping.confidence for mapping in mappings)


def _severity_counts(risks: list[MigrationRisk]) -> dict[str, int]:
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for risk in risks:
        counts[risk.severity] += 1
    return counts


def _security_control_bonus(report: MigrationAssessmentReport) -> int:
    text = _report_text(report)
    return sum(
        1
        for token in [
            "iam",
            "kms",
            "secrets manager",
            "cloudtrail",
            "waf",
            "entra",
            "rbac",
            "key vault",
            "cloud iam",
            "cloud kms",
            "secret manager",
            "cloud armor",
        ]
        if token in text
    )


def _operations_control_bonus(report: MigrationAssessmentReport) -> int:
    text = _report_text(report)
    return sum(
        1
        for token in [
            "cloudwatch",
            "cloud monitoring",
            "azure monitor",
            "log analytics",
            "cloud logging",
            "backup",
            "autoscaling",
            "auto scaling",
            "runbook",
        ]
        if token in text
    )


def _skill_gaps(
    report: MigrationAssessmentReport,
    *,
    has_data: bool,
    has_hybrid: bool,
    has_streaming: bool,
    target_label: str,
) -> list[str]:
    gaps = [f"{target_label} landing zone, identity, key management, observability, and infrastructure-as-code operations."]
    if has_hybrid:
        gaps.append(f"{target_label} networking, private connectivity, VPN, BGP, and route-table operations.")
    if has_data:
        gaps.append(f"{target_label} database, analytics, backup, migration tooling, and data reconciliation.")
    if has_streaming:
        gaps.append(f"Event-driven {target_label} services, retry semantics, dead-letter handling, and replay operations.")
    if any(mapping.confidence < 0.55 for mapping in report.service_mappings):
        gaps.append("Provider-specific service mapping review for low-confidence components.")
    return _unique(gaps)


def _data_migration_approach(report: MigrationAssessmentReport, *, has_data: bool) -> list[str]:
    if not has_data:
        return [
            "No major data platform was confidently detected. Validate configuration, secrets, and small state stores manually."
        ]
    text = _report_text(report)
    plan = [
        "Classify data by system of record, RPO/RTO, retention, and compliance requirements.",
        "Use incremental replication or staged export/import where possible, then reconcile record counts and business totals.",
        "Rehearse restore and rollback before production cutover.",
    ]
    if _contains_any(text, ["s3", "cloud storage", "blob"]):
        plan.append("Move object data with lifecycle, encryption, ownership, and access-policy validation.")
    if _contains_any(text, ["rds", "aurora", "sql", "database"]):
        plan.append("Use a database migration tool or native replication, then perform schema and query compatibility testing.")
    if _contains_any(text, ["redshift", "bigquery", "athena"]):
        plan.append("Validate warehouse semantics, partitioning, query performance, and dashboard/report dependencies.")
    return _unique(plan)


def _provider_label(provider: str | None) -> str:
    normalized = (provider or "").lower()
    if "azure" in normalized:
        return "Azure"
    if "gcp" in normalized or "google" in normalized:
        return "Google Cloud"
    if "aws" in normalized or "amazon" in normalized:
        return "AWS"
    return provider or "target cloud"


def _report_text(report: MigrationAssessmentReport) -> str:
    parts = [
        report.source_architecture.provider,
        report.source_architecture.summary,
        report.target_architecture.summary,
        *[component.name for component in report.source_architecture.components],
        *[component.service_type or "" for component in report.source_architecture.components],
        *[component.name for component in report.target_architecture.components],
        *[mapping.source_service for mapping in report.service_mappings],
        *[mapping.target_service for mapping in report.service_mappings],
        *report.required_changes,
        *report.target_architecture.design_notes,
    ]
    return " ".join(parts).lower()


def _contains_any(text: str, tokens: list[str]) -> bool:
    normalized = text.lower()
    return any(token in normalized for token in tokens)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _clamp_score(value: int | float) -> int:
    return max(0, min(100, int(round(value))))
