"""Migration strategy, risk, and verdict generation."""

from __future__ import annotations

from app.schemas import (
    FinalVerdict,
    MigrationPhase,
    MigrationRisk,
    ServiceMapping,
    SourceArchitecture,
    TargetArchitecture,
)


def generate_required_changes(
    source_architecture: SourceArchitecture,
    target_architecture: TargetArchitecture,
    service_mappings: list[ServiceMapping],
) -> list[str]:
    target_label = _provider_label(target_architecture.provider)
    identity, keys, secrets, observability, network = _control_labels(target_architecture.provider)
    changes = [
        f"Rebuild network topology around {target_label} {network}, public/private subnets, route tables, firewall/security rules, and ingress controls.",
        f"Replace provider-native identity, secret, logging, and monitoring integrations with {identity}, {secrets}/{keys}, and {observability} patterns.",
        f"Validate application configuration, connection strings, DNS, TLS certificates, and deployment automation for {target_label} environments.",
        "Create tested backup, disaster recovery, rollback, and cutover runbooks before production migration.",
    ]
    target_component_ids = {component.id for component in target_architecture.components}
    if "aws_transit_gateway" in target_component_ids:
        changes.extend(
            [
                "Define the hybrid routing model: customer routers to Direct Connect connections, Transit VIFs with BGP, Direct Connect Gateway, Transit Gateway, and VPC attachments.",
                "Configure Site-to-Site VPN as a Transit Gateway VPN attachment with two IPsec tunnels and BGP for backup routing rather than as a direct VPC gateway path.",
                "Design Transit Gateway route table association and propagation for Direct Connect, VPN, and VPC attachments.",
                "Point private subnet route tables for on-premises CIDRs toward the Transit Gateway.",
                "Set route preference so Direct Connect is primary and VPN routes are used only during Direct Connect failover.",
            ]
        )
    if "aws_direct_connect" in target_component_ids:
        changes.append(
            "Choose a Direct Connect resiliency model, including redundant connections and diverse Direct Connect locations where production SLA requires it."
        )
    for mapping in service_mappings:
        changes.append(
            f"Assess migration path from {mapping.source_service} to {mapping.target_service}, including feature gaps and operational model changes."
        )
    if source_architecture.missing_information:
        changes.append("Resolve missing architecture details before final sizing, cost modeling, and implementation planning.")
    return changes


def generate_migration_strategy(
    source_architecture: SourceArchitecture,
    target_architecture: TargetArchitecture,
    service_mappings: list[ServiceMapping],
    goals: list[str] | None = None,
) -> list[MigrationPhase]:
    goals_text = goals or ["reduce migration risk", "preserve service reliability"]
    target_label = _provider_label(target_architecture.provider)
    identity, keys, _secrets, observability, network = _control_labels(target_architecture.provider)
    return [
        MigrationPhase(
            phase="1. Discovery and Readiness",
            goals=["Validate architecture inventory", "Confirm business drivers", *goals_text],
            activities=[
                "Review source diagram, subscriptions/accounts, dependencies, traffic patterns, and data classification.",
                "Identify service owners, SLAs, compliance obligations, and downtime tolerance.",
                f"Create a {target_label} landing zone baseline with accounts/projects/subscriptions, networking, identity, logging, and guardrails.",
            ],
            deliverables=[
                "Validated application inventory",
                "Migration readiness checklist",
                f"{target_label} landing zone design",
            ],
            risks=["Hidden dependencies may be missed without runtime telemetry."],
            success_criteria=[
                "All critical components have owners, dependencies, target services, and rollback expectations documented."
            ],
        ),
        MigrationPhase(
            phase="2. Foundation Build",
            goals=[f"Build secure {target_label} target foundation", "Prepare deployment and observability"],
            activities=[
                f"Provision {network}, subnet tiers, routing, firewall/security rules, {identity}, {keys}, and logging.",
                "Create CI/CD pipelines, infrastructure-as-code modules, and environment promotion controls.",
                f"Configure {observability} dashboards, alarms, backup policies, and security monitoring.",
            ],
            deliverables=[
                f"{target_label} infrastructure baseline",
                "Deployment pipelines",
                "Operational runbooks",
            ],
            risks=["Security or network assumptions can cause late-stage connectivity failures."],
            success_criteria=[
                "Target environment passes connectivity, security, backup, and observability validation."
            ],
        ),
        MigrationPhase(
            phase="3. Workload and Data Migration",
            goals=["Migrate application services", "Move data with controlled downtime"],
            activities=[
                "Deploy target compute services and migrate configuration/secrets.",
                "Migrate databases and object storage using rehearsed replication, export/import, or managed migration tooling.",
                f"Run functional, performance, failover, and security tests against the {target_label} environment.",
            ],
            deliverables=[
                f"Migrated workload in {target_label}",
                "Data migration evidence",
                "Test results and defect list",
            ],
            risks=["Data consistency, latency changes, or incompatible service features may affect cutover readiness."],
            success_criteria=[
                f"{target_label} workload meets functional, performance, security, and data reconciliation thresholds."
            ],
        ),
        MigrationPhase(
            phase="4. Cutover and Optimization",
            goals=["Execute controlled production cutover", "Optimize cost and operations"],
            activities=[
                "Perform final data sync, DNS/traffic shift, smoke tests, and rollback checkpoint validation.",
                "Monitor service health, user impact, cost, and security signals after cutover.",
                "Right-size resources, tune autoscaling, and finalize decommissioning of source services.",
            ],
            deliverables=[
                "Production cutover record",
                "Post-migration optimization backlog",
                "Source-cloud decommission plan",
            ],
            risks=["Rollback windows may be constrained by data divergence after cutover."],
            success_criteria=[
                f"Production traffic runs on {target_label} within agreed SLA, cost, and incident thresholds."
            ],
        ),
    ]


def generate_benefits(
    target_architecture: TargetArchitecture,
    service_mappings: list[ServiceMapping],
) -> list[str]:
    target_label = _provider_label(target_architecture.provider)
    return [
        f"Opportunity to standardize on {target_label} networking, identity, encryption, observability, and backup controls.",
        f"Managed {target_label} services can reduce undifferentiated infrastructure operations when chosen appropriately.",
        "Migration can create a modernization path for compute, data, and event-driven components.",
        "A well-designed landing zone can improve account separation, security guardrails, and operational consistency.",
    ]


def generate_drawbacks(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> list[str]:
    drawbacks = [
        "Cross-cloud service differences may require application, deployment, and operational changes.",
        "Data migration and cutover planning can introduce downtime, synchronization, and rollback complexity.",
        "Teams may need target-cloud operational maturity before the migration can deliver reliable production outcomes.",
        "Actual costs may rise without workload sizing, traffic modeling, right-sizing, and commitment planning.",
    ]
    if any(mapping.confidence < 0.5 for mapping in service_mappings):
        drawbacks.append("Several service mappings have low confidence and need architect validation.")
    if source_architecture.missing_information:
        drawbacks.append("Missing architecture details reduce confidence in scope, effort, and risk estimates.")
    return drawbacks


def generate_risks(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> list[MigrationRisk]:
    risks = [
        MigrationRisk(
            title="Incomplete Architecture Discovery",
            severity="medium",
            description="The provided diagram may omit runtime dependencies, private endpoints, identity flows, or integration systems.",
            mitigation="Validate with source-cloud inventory, logs, flow records, CMDB data, and application owner interviews.",
        ),
        MigrationRisk(
            title="Data Migration and Cutover Risk",
            severity="high",
            description="Database and object storage migration can create consistency, downtime, and rollback challenges.",
            mitigation="Use migration rehearsals, data reconciliation, incremental replication where possible, and a tested rollback plan.",
        ),
        MigrationRisk(
            title="Security Control Drift",
            severity="medium",
            description="Identity, secret, key, network, and logging controls differ between cloud providers.",
            mitigation="Map controls explicitly and test identity, key management, secrets, network policy, and logging before production cutover.",
        ),
        MigrationRisk(
            title="Cost Model Uncertainty",
            severity="medium",
            description="Cloud pricing, data transfer, managed service sizing, and operational costs may differ materially from the source platform.",
            mitigation="Create a workload-based target-cloud cost estimate and review it after performance testing and right-sizing.",
        ),
    ]
    if any(mapping.confidence < 0.5 for mapping in service_mappings):
        risks.append(
            MigrationRisk(
                title="Low-Confidence Service Mapping",
                severity="high",
                description="One or more source services did not have a direct mapping and may require redesign.",
                mitigation="Run a provider-specific architecture review before committing to implementation timelines.",
            )
        )
    if any(
        token in f"{mapping.source_service} {mapping.target_service}".lower()
        for mapping in service_mappings
        for token in ["expressroute", "direct connect", "vpn", "transit gateway"]
    ):
        risks.append(
            MigrationRisk(
                title="Hybrid Routing and Failover Risk",
                severity="high",
                description="Direct Connect, BGP route advertisements, Transit Gateway attachments, and VPN backup behavior can cause asymmetric routing or unexpected failover if not tested.",
                mitigation="Validate BGP advertisements, route priorities, VPN backup behavior, and failure scenarios in a non-production connectivity test before cutover.",
            )
        )
    if source_architecture.provider == "unknown":
        risks.append(
            MigrationRisk(
                title="Unknown Source Provider",
                severity="critical",
                description="The source provider could not be confidently identified from the uploaded material.",
                mitigation="Provide a clearer diagram, source inventory export, or provider hint before planning migration.",
            )
        )
    return risks


def generate_final_verdict(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
    risks: list[MigrationRisk],
    benefits: list[str],
    drawbacks: list[str],
) -> FinalVerdict:
    high_or_critical = sum(1 for risk in risks if risk.severity in {"high", "critical"})
    low_confidence_mappings = sum(1 for mapping in service_mappings if mapping.confidence < 0.5)
    unknown_provider = source_architecture.provider == "unknown"

    if unknown_provider or high_or_critical >= 4 or low_confidence_mappings >= 3:
        return FinalVerdict(
            recommendation="not_recommended",
            reasoning=(
                "The migration is not ready to proceed based on current information. "
                "Critical unknowns or multiple high-risk areas must be resolved before a reliable plan can be approved."
            ),
            confidence=0.68,
        )

    if high_or_critical == 0 and low_confidence_mappings == 0 and len(benefits) > len(drawbacks):
        return FinalVerdict(
            recommendation="recommended",
            reasoning=(
                "The migration appears technically feasible with clear target-cloud service targets and manageable risk, "
                "provided normal discovery, testing, security, and cutover controls are executed."
            ),
            confidence=0.72,
        )

    return FinalVerdict(
        recommendation="conditionally_recommended",
        reasoning=(
            "The migration is feasible, but it should proceed only after discovery validation, detailed cost modeling, "
            "security control mapping, migration rehearsals, and a tested rollback plan. This is the default posture for "
            "most production cloud-to-cloud migrations."
        ),
        confidence=0.78,
    )


def _provider_label(provider: str | None) -> str:
    normalized = (provider or "").lower()
    if "azure" in normalized:
        return "Azure"
    if "gcp" in normalized or "google" in normalized:
        return "Google Cloud"
    if "aws" in normalized or "amazon" in normalized:
        return "AWS"
    return provider or "target cloud"


def _control_labels(provider: str | None) -> tuple[str, str, str, str, str]:
    normalized = (provider or "").lower()
    if "azure" in normalized:
        return (
            "Microsoft Entra ID and Azure RBAC",
            "Azure Key Vault keys",
            "Azure Key Vault",
            "Azure Monitor + Log Analytics",
            "Virtual Network",
        )
    if "gcp" in normalized or "google" in normalized:
        return (
            "Cloud IAM",
            "Cloud KMS",
            "Secret Manager",
            "Cloud Monitoring + Cloud Logging",
            "VPC Network",
        )
    return ("IAM roles", "KMS keys", "Secrets Manager", "CloudWatch", "VPC")
