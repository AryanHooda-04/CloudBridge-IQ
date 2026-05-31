"""Target architecture generation for migration assessments."""

from __future__ import annotations

import re

from app.schemas import (
    ArchitectureComponent,
    ArchitectureRelationship,
    ServiceMapping,
    SourceArchitecture,
    TargetArchitecture,
)


def generate_target_architecture(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
    target_provider: str = "aws",
    goals: list[str] | None = None,
) -> TargetArchitecture:
    """Generate a production-oriented target architecture from service mappings."""

    target = target_provider.lower()
    if target != "aws":
        return _generate_generic_target(source_architecture, service_mappings, target)

    goals = goals or []
    source_text = _architecture_text(source_architecture)
    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    _add_component(
        components,
        "vpc",
        "Amazon VPC",
        "aws",
        "networking",
        0.95,
        "Network isolation boundary with routing, security groups, and subnets.",
    )
    _add_component(
        components,
        "private_subnets",
        "Private Subnets",
        "aws",
        "networking",
        0.9,
        "Application, data, and hybrid-routed subnet tier isolated from direct internet ingress.",
    )

    for mapping in service_mappings:
        category = _category_for_service(mapping.target_service)
        component_id = _component_id_for_mapping(mapping)
        component_name = _canonical_service_name_for_mapping(mapping)
        if component_id in {"vpc", "public_subnets", "private_subnets"}:
            continue
        _add_component(
            components,
            component_id,
            component_name,
            "aws",
            category,
            mapping.confidence,
            f"Target for {mapping.source_service}. {mapping.reasoning}",
        )

    has_device_ingestion = _mentions(source_text, ["iot device", "iot devices", "device telemetry", "standard devices"])
    has_streaming_ingestion = _mentions(source_text, ["stream", "streaming", "telemetry", "pub/sub", "pubsub", "dataflow"])
    has_bigquery = _mentions(source_text, ["bigquery"])
    has_dataflow = _mentions(source_text, ["dataflow"])
    has_logging = _mentions(source_text, ["logging", "monitoring"])

    if has_device_ingestion:
        _add_component(
            components,
            "aws_iot_core",
            "AWS IoT Core",
            "aws",
            "iot",
            0.82,
            "Device registry, MQTT/message broker, rules engine, and secure device ingestion for IoT workloads.",
        )
    if has_device_ingestion or has_streaming_ingestion:
        _add_component(
            components,
            "amazon_kinesis",
            "Amazon Kinesis Data Streams / Firehose",
            "aws",
            "messaging",
            0.78,
            "Optional high-volume streaming telemetry ingestion and delivery layer.",
        )
    if has_dataflow:
        _add_component(
            components,
            "amazon_managed_flink",
            "Amazon Managed Service for Apache Flink",
            "aws",
            "analytics",
            0.76,
            "Streaming analytics option for low-latency Dataflow-style pipelines.",
        )
    if has_bigquery:
        _add_component(
            components,
            "amazon_athena_glue_catalog",
            "Amazon Athena + AWS Glue Data Catalog",
            "aws",
            "analytics",
            0.78,
            "Serverless SQL and metadata catalog option for querying data directly in Amazon S3.",
        )
    if has_logging:
        _add_component(
            components,
            "aws_observability_stack",
            "CloudWatch / CloudTrail / OpenSearch",
            "aws",
            "observability",
            0.78,
            "Operational metrics, logs, audit events, and searchable log analytics for migrated workloads.",
        )

    has_hybrid_connectivity = _has_hybrid_connectivity(source_text, service_mappings, components)
    if has_hybrid_connectivity:
        _add_component(
            components,
            "on_premises_network",
            "On-premises network",
            "external",
            "external",
            0.9,
            "Existing customer network that remains connected to the migrated AWS environment.",
        )
        _add_component(
            components,
            "customer_gateway",
            "Customer Gateway routers (HA)",
            "external",
            "networking",
            0.84,
            "Redundant customer edge routers or AWS customer gateway representations for hybrid connectivity.",
        )

        if _mentions(source_text, ["expressroute", "direct connect"]) or _has_component(
            components, "aws_direct_connect"
        ):
            _add_component(
                components,
                "aws_direct_connect",
                "Redundant Direct Connect connections",
                "aws",
                "networking",
                0.86,
                "Redundant dedicated private connectivity replacing Azure ExpressRoute, ideally in separate Direct Connect locations.",
            )
            _add_component(
                components,
                "transit_vif",
                "Transit VIFs with BGP",
                "aws",
                "networking",
                0.84,
                "Transit virtual interfaces using BGP route exchange from on-premises routers toward AWS.",
            )
            _add_component(
                components,
                "aws_direct_connect_gateway",
                "AWS Direct Connect Gateway",
                "aws",
                "networking",
                0.82,
                "Gateway used to connect Direct Connect to AWS network routing domains.",
            )

        if _mentions(source_text, ["vpn gateway", "vpn"]) or _has_component(
            components, "aws_site_to_site_vpn"
        ):
            _add_component(
                components,
                "ipsec_vpn_tunnels",
                "IPsec VPN tunnels (2) with BGP",
                "aws",
                "networking",
                0.84,
                "Redundant IPsec tunnels using BGP for the Site-to-Site VPN backup path.",
            )
            _add_component(
                components,
                "aws_site_to_site_vpn",
                "AWS Site-to-Site VPN attachment",
                "aws",
                "networking",
                0.84,
                "Transit Gateway VPN attachment used as the encrypted backup path to Direct Connect.",
            )

        if _has_any_component(
            components,
            ["aws_direct_connect", "aws_site_to_site_vpn", "aws_direct_connect_gateway"],
        ) or _mentions(source_text, ["gateway subnet", "virtual network gateway"]):
            _add_component(
                components,
                "aws_transit_gateway",
                "AWS Transit Gateway",
                "aws",
                "networking",
                0.82,
                "Central routing hub for VPC and hybrid connectivity attachments.",
            )
            _add_component(
                components,
                "tgw_route_table",
                "Transit Gateway route table",
                "aws",
                "networking",
                0.84,
                "Routing policy table where Direct Connect, VPN, and VPC attachment routes are associated and propagated.",
            )
            _add_component(
                components,
                "tgw_vpc_attachment",
                "Transit Gateway VPC Attachment",
                "aws",
                "networking",
                0.84,
                "VPC attachment that connects the Amazon VPC to the regional Transit Gateway routing domain.",
            )
            _add_component(
                components,
                "private_route_tables",
                "Private subnet route tables",
                "aws",
                "networking",
                0.84,
                "Private subnet route tables that send on-premises CIDRs to the Transit Gateway.",
            )

    compute_ids = _component_ids_in_categories(components, {"compute"})
    if not compute_ids:
        compute_ids = _component_ids_in_categories(components, {"application"})
    data_ids = _component_ids_in_categories(components, {"database"})
    storage_ids = _component_ids_in_categories(components, {"storage"})
    messaging_ids = _component_ids_in_categories(components, {"messaging"})
    analytics_ids = _component_ids_in_categories(components, {"analytics", "ml", "iot"})
    has_data_platform = bool(analytics_ids or (messaging_ids and (data_ids or storage_ids)))
    ingress_ids = [
        component_id
        for component_id in ("application_load_balancer", "elastic_load_balancing", "aws_waf")
        if component_id in components
    ]

    has_public_workload = bool(compute_ids or ingress_ids)
    if has_public_workload:
        _add_component(
            components,
            "public_subnets",
            "Public Subnets",
            "aws",
            "networking",
            0.9,
            "Ingress-facing subnet tier for load balancers and NAT gateways.",
        )
        _add_component(
            components,
            "users",
            "Users",
            "external",
            "client",
            0.95,
            "End users or upstream systems consuming the application.",
        )
        _add_component(
            components,
            "route53",
            "Amazon Route 53",
            "aws",
            "networking",
            0.8,
            "DNS entry point for the migrated workload.",
        )
        if compute_ids and not ingress_ids:
            _add_component(
                components,
                "application_load_balancer",
                "Application Load Balancer",
                "aws",
                "networking",
                0.78,
                "Layer 7 ingress routing for production web or API workloads.",
            )
            ingress_ids.append("application_load_balancer")

    _add_component(
        components,
        "iam",
        "AWS IAM",
        "aws",
        "security",
        0.84,
        "Identity and access controls using least privilege.",
    )
    _add_component(
        components,
        "amazon_cloudwatch",
        "Amazon CloudWatch",
        "aws",
        "observability",
        0.84,
        "Metrics, logs, alarms, and operational dashboards.",
    )

    if compute_ids:
        _add_component(
            components,
            "aws_secrets_manager",
            "AWS Secrets Manager",
            "aws",
            "security",
            0.82,
            "Centralized secrets storage and rotation for application credentials.",
        )
    if compute_ids or data_ids or storage_ids:
        _add_component(
            components,
            "aws_kms",
            "AWS KMS",
            "aws",
            "security",
            0.82,
            "Managed encryption keys for data protection.",
        )
    if data_ids or storage_ids:
        _add_component(
            components,
            "aws_backup",
            "AWS Backup",
            "aws",
            "resilience",
            0.82,
            "Centralized backup policy and restore orchestration.",
        )

    _rel(relationships, "vpc", "public_subnets", "contains")
    _rel(relationships, "vpc", "private_subnets", "contains")

    if has_public_workload:
        first_ingress = ingress_ids[0] if ingress_ids else None
        if first_ingress:
            _rel(relationships, "users", "route53", "resolves")
            _rel(relationships, "route53", first_ingress, "routes_to")
            _rel(relationships, first_ingress, "public_subnets", "deployed_in")
            for compute_id in compute_ids:
                _rel(relationships, first_ingress, compute_id, "forwards_to")

    for compute_id in compute_ids:
        _rel(relationships, compute_id, "private_subnets", "deployed_in")
        if "aws_secrets_manager" in components:
            _rel(relationships, compute_id, "aws_secrets_manager", "retrieves_secrets")
        if "aws_kms" in components:
            _rel(relationships, compute_id, "aws_kms", "uses_encryption_keys")
        _rel(relationships, compute_id, "amazon_cloudwatch", "emits_telemetry")
        for data_id in data_ids:
            _rel(relationships, compute_id, data_id, "reads_writes")
        for storage_id in storage_ids:
            _rel(relationships, compute_id, storage_id, "uses_storage")
        for messaging_id in messaging_ids:
            _rel(relationships, compute_id, messaging_id, "publishes_or_consumes")

    if has_hybrid_connectivity:
        _rel(relationships, "on_premises_network", "customer_gateway", "connects_from")
        if "aws_direct_connect" in components:
            _rel(relationships, "customer_gateway", "aws_direct_connect", "redundant_dx")
            if "transit_vif" in components:
                _rel(relationships, "aws_direct_connect", "transit_vif", "transit_vif_bgp")
            if "aws_direct_connect_gateway" in components:
                source_id = "transit_vif" if "transit_vif" in components else "aws_direct_connect"
                _rel(relationships, source_id, "aws_direct_connect_gateway", "associated_with")
        if "aws_site_to_site_vpn" in components:
            if "ipsec_vpn_tunnels" in components:
                _rel(relationships, "customer_gateway", "ipsec_vpn_tunnels", "bgp_over_ipsec_vpn")
                _rel(relationships, "ipsec_vpn_tunnels", "aws_site_to_site_vpn", "two_ipsec_tunnels")
            else:
                _rel(relationships, "customer_gateway", "aws_site_to_site_vpn", "ipsec_backup")
        if "aws_transit_gateway" in components:
            if "aws_direct_connect_gateway" in components:
                _rel(relationships, "aws_direct_connect_gateway", "aws_transit_gateway", "tgw_association")
            if "aws_site_to_site_vpn" in components:
                _rel(relationships, "aws_site_to_site_vpn", "aws_transit_gateway", "vpn_attachment")
            if "tgw_route_table" in components:
                _rel(relationships, "aws_transit_gateway", "tgw_route_table", "route_association")
            if "tgw_vpc_attachment" in components:
                route_source = "tgw_route_table" if "tgw_route_table" in components else "aws_transit_gateway"
                _rel(relationships, route_source, "tgw_vpc_attachment", "propagates_routes")
                if "private_route_tables" in components:
                    _rel(relationships, "tgw_vpc_attachment", "private_route_tables", "vpc_attachment")
                    _rel(relationships, "private_route_tables", "private_subnets", "routes_to_workloads")
                    _rel(relationships, "vpc", "private_route_tables", "contains")
                else:
                    _rel(relationships, "tgw_vpc_attachment", "private_subnets", "routes_to")
                _rel(relationships, "vpc", "tgw_vpc_attachment", "contains")
            else:
                _rel(relationships, "aws_transit_gateway", "private_subnets", "routes_to")
            _rel(relationships, "aws_transit_gateway", "amazon_cloudwatch", "monitored_by")

    for data_id in data_ids:
        _rel(relationships, data_id, "private_subnets", "deployed_in")
        if "aws_kms" in components:
            _rel(relationships, data_id, "aws_kms", "encrypted_by")
        if "aws_backup" in components:
            _rel(relationships, data_id, "aws_backup", "backed_up_by")

    for storage_id in storage_ids:
        if "aws_kms" in components:
            _rel(relationships, storage_id, "aws_kms", "encrypted_by")
        if "aws_backup" in components:
            _rel(relationships, storage_id, "aws_backup", "protected_by")

    summary = _summary_for_architecture(
        has_hybrid_connectivity,
        has_public_workload,
        has_data_platform,
    )
    design_notes = [
        (
            "Keep application and data workloads in private subnets; expose only managed ingress endpoints publicly."
            if has_public_workload
            else "Keep hybrid-routed workloads in private subnets and avoid public ingress unless an application tier requires it."
        ),
        (
            "Use IAM roles and managed AWS network gateways instead of directly moving Azure gateway constructs one-to-one."
            if has_hybrid_connectivity
            else "Avoid blind one-to-one service substitution; validate event delivery, streaming, analytics, runtime, and operating-model semantics."
        ),
        "Validate connectivity, routing, DNS, firewall rules, and rollback procedures before cutover.",
        "Define CloudWatch dashboards and alarms before production migration.",
    ]
    if has_hybrid_connectivity:
        design_notes.extend(
            [
                "Use Transit VIFs with BGP from redundant customer routers to Direct Connect Gateway; prefer Direct Connect routes and keep VPN as backup.",
                "Use two IPsec VPN tunnels with BGP for the Site-to-Site VPN backup path, terminating as a Transit Gateway VPN attachment.",
                "Attach Site-to-Site VPN to Transit Gateway as a VPN attachment rather than treating it as a VPC gateway path.",
                "Connect Transit Gateway to workloads through Transit Gateway VPC attachments; Transit Gateway is regional and not inside the VPC.",
                "Model Transit Gateway route table associations and propagation explicitly for Direct Connect, VPN, and VPC attachments.",
                "Point private subnet route tables for on-premises CIDRs toward the Transit Gateway.",
                "Use redundant Direct Connect connections, ideally through separate devices and locations, when production resiliency requirements justify it.",
            ]
        )
    if data_ids or storage_ids:
        design_notes.append("Attach backup, restore, and encryption policies to migrated data services.")
    if has_data_platform:
        design_notes.extend(
            [
                "Model event ingestion, processing, storage, analytics, and operations as separate platform tiers rather than dense service-to-service links.",
                "Use AWS IoT Core and Kinesis for device telemetry only where device identity, MQTT/rules processing, or high-volume streaming requirements justify them.",
                "Validate App Engine workloads before selecting App Runner, ECS/Fargate, Lambda, Elastic Beanstalk, or EC2 as the final hosting target.",
                "Use Redshift for warehouse workloads and Athena with Glue Data Catalog for direct SQL over data in Amazon S3.",
            ]
        )
    if goals:
        design_notes.append(f"Architecture was shaped by stated goals: {', '.join(goals)}.")

    return TargetArchitecture(
        provider="aws",
        summary=summary,
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=design_notes,
    )


def _generate_generic_target(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
    target_provider: str,
) -> TargetArchitecture:
    provider = _provider_key(target_provider)
    if provider == "azure" and _is_graphrag_source(source_architecture, service_mappings):
        return _generate_azure_graphrag_target(source_architecture, service_mappings)
    if provider == "gcp" and _is_graphrag_source(source_architecture, service_mappings):
        return _generate_gcp_graphrag_target(source_architecture, service_mappings)
    if provider == "azure" and _is_data_platform_source(source_architecture, service_mappings):
        return _generate_azure_data_platform_target(source_architecture, service_mappings)
    if provider == "gcp" and _is_hybrid_connectivity_source(source_architecture, service_mappings):
        return _generate_gcp_hybrid_connectivity_target(source_architecture, service_mappings)

    profile = _provider_profile(provider)
    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    network_id = profile["network"][0]
    private_id = profile["private"][0]
    observability_id = profile["observability"][0]
    identity_id = profile["identity"][0]
    secrets_id = profile["secrets"][0]
    encryption_id = profile["encryption"][0]
    backup_id = profile["backup"][0]

    for key in ("network", "private", "identity", "observability"):
        component_id, name, category, description = profile[key]
        _add_component(
            components,
            component_id,
            name,
            provider,
            category,
            0.88,
            description,
        )

    for mapping in service_mappings:
        component_id = _slug(mapping.target_service)
        _add_component(
            components,
            component_id,
            mapping.target_service,
            provider,
            _category_for_service(mapping.target_service),
            mapping.confidence,
            f"Target for {mapping.source_service}. {mapping.reasoning}",
        )

    compute_ids = _component_ids_in_categories(components, {"compute", "application"})
    data_ids = _component_ids_in_categories(components, {"database"})
    storage_ids = _component_ids_in_categories(components, {"storage"})
    messaging_ids = _component_ids_in_categories(components, {"messaging"})
    analytics_ids = _component_ids_in_categories(components, {"analytics", "ml", "iot"})
    ingress_ids = _component_ids_in_categories(components, {"networking"})
    ingress_ids = [
        component_id
        for component_id in ingress_ids
        if component_id not in {network_id, private_id}
        and any(token in components[component_id].name.lower() for token in ["load", "gateway", "front door"])
    ]

    if compute_ids or ingress_ids:
        for key in ("public", "dns", "load_balancer"):
            component_id, name, category, description = profile[key]
            _add_component(
                components,
                component_id,
                name,
                provider,
                category,
                0.82,
                description,
            )
        _add_component(
            components,
            "users",
            "Users",
            "external",
            "client",
            0.95,
            "End users or upstream systems consuming the application.",
        )

    if compute_ids:
        for key in ("secrets", "encryption"):
            component_id, name, category, description = profile[key]
            _add_component(
                components,
                component_id,
                name,
                provider,
                category,
                0.82,
                description,
            )
    if data_ids or storage_ids:
        for key in ("encryption", "backup"):
            component_id, name, category, description = profile[key]
            _add_component(
                components,
                component_id,
                name,
                provider,
                category,
                0.82,
                description,
            )

    _rel(relationships, network_id, private_id, "contains")

    public_id = profile["public"][0]
    dns_id = profile["dns"][0]
    load_balancer_id = profile["load_balancer"][0]
    if "users" in components and dns_id in components and load_balancer_id in components:
        _rel(relationships, network_id, public_id, "contains")
        _rel(relationships, "users", dns_id, "resolves")
        _rel(relationships, dns_id, load_balancer_id, "routes_to")
        _rel(relationships, load_balancer_id, public_id, "deployed_in")
        for compute_id in compute_ids:
            _rel(relationships, load_balancer_id, compute_id, "forwards_to")

    for compute_id in compute_ids:
        _rel(relationships, compute_id, private_id, "deployed_in")
        _rel(relationships, identity_id, compute_id, "authorizes")
        _rel(relationships, compute_id, observability_id, "emits_telemetry")
        if secrets_id in components:
            _rel(relationships, compute_id, secrets_id, "retrieves_secrets")
        if encryption_id in components:
            _rel(relationships, compute_id, encryption_id, "uses_encryption_keys")
        for data_id in data_ids:
            _rel(relationships, compute_id, data_id, "reads_writes")
        for storage_id in storage_ids:
            _rel(relationships, compute_id, storage_id, "uses_storage")
        for messaging_id in messaging_ids:
            _rel(relationships, compute_id, messaging_id, "publishes_or_consumes")

    for messaging_id in messaging_ids:
        _rel(relationships, messaging_id, observability_id, "emits_telemetry")
        for analytics_id in analytics_ids:
            _rel(relationships, messaging_id, analytics_id, "feeds")

    for analytics_id in analytics_ids:
        _rel(relationships, analytics_id, private_id, "runs_in")
        _rel(relationships, analytics_id, observability_id, "emits_telemetry")
        for storage_id in storage_ids:
            _rel(relationships, analytics_id, storage_id, "reads_writes")

    for data_id in data_ids:
        _rel(relationships, data_id, private_id, "deployed_in")
        if encryption_id in components:
            _rel(relationships, data_id, encryption_id, "encrypted_by")
        if backup_id in components:
            _rel(relationships, data_id, backup_id, "backed_up_by")

    for storage_id in storage_ids:
        if encryption_id in components:
            _rel(relationships, storage_id, encryption_id, "encrypted_by")
        if backup_id in components:
            _rel(relationships, storage_id, backup_id, "protected_by")

    target_label = _provider_label(provider)
    return TargetArchitecture(
        provider=provider,
        summary=(
            f"Proposed {target_label} target architecture with provider-native networking, "
            "identity, observability, security, backup, and mapped application/data services."
        ),
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=[
            f"Use {target_label} landing-zone, identity, logging, encryption, and network guardrails before workload migration.",
            "Treat service mappings as architecture candidates; validate service limits, feature gaps, SLAs, and operational model before implementation.",
            "Keep application and data workloads in private network tiers where possible; expose only managed ingress endpoints.",
            "Define backup, monitoring, rollback, and cutover runbooks before production migration.",
        ],
    )


def _generate_azure_graphrag_target(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> TargetArchitecture:
    source_text = (
        _architecture_text(source_architecture)
        + " "
        + " ".join(f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings)
    ).lower()
    has_lambda = _mentions(source_text, ["lambda", "azure functions"])
    has_ec2 = _mentions(source_text, ["ec2", "virtual machines"])
    has_eks = _mentions(source_text, ["eks", "kubernetes", "aks"])

    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    def add(
        component_id: str,
        name: str,
        category: str,
        confidence: float,
        description: str,
        provider: str = "azure",
    ) -> None:
        _add_component(components, component_id, name, provider, category, confidence, description)

    add("data_sources", "Redshift / S3 / MSK / Glue inputs", "external", 0.88, "Existing AWS data sources feeding the GraphRAG workload.", "external")
    add("adls_gen2", "Azure Data Lake Storage Gen2", "storage", 0.88, "S3-style document, file, and graph ingestion landing zone.")
    add("azure_event_hubs_kafka", "Azure Event Hubs with Kafka support", "messaging", 0.84, "MSK-style Kafka-compatible streaming ingestion.")
    add("azure_data_factory", "Azure Data Factory / Fabric Data Factory", "analytics", 0.84, "Glue-style orchestration, ingestion, and ETL pipelines.")
    add("azure_synapse_fabric", "Synapse Analytics or Microsoft Fabric Warehouse", "database", 0.82, "Redshift-style warehouse and analytical source data.")

    add("extraction_jobs", "Azure Functions / Databricks extraction jobs", "compute", 0.82, "Parsing, chunking, entity extraction, and graph-ready transformation jobs.")
    add("azure_machine_learning", "Azure Machine Learning", "ml", 0.84, "SageMaker-style ML pipelines, notebooks, and model operations.")
    add("azure_openai_ai_foundry", "Azure OpenAI / Azure AI Foundry", "ml", 0.86, "Bedrock-style foundation model access and AI orchestration.")
    add("neo4j_cypher_ingestion", "Neo4j driver / Cypher ingestion service", "application", 0.82, "Application service that writes extracted entities and relationships into Neo4j.")

    add("neo4j_auradb", "Neo4j AuraDB on Azure / Neo4j on AKS or VMs", "database", 0.88, "Central graph database and knowledge graph store.")
    add("neo4j_bloom", "Neo4j Bloom", "application", 0.78, "Graph exploration and stakeholder visualization capability retained from the Neo4j ecosystem.")
    add("neo4j_graph_data_science", "Neo4j Graph Data Science", "analytics", 0.8, "Graph algorithms, embeddings, similarity, ranking, and graph analytics.")

    add("neo4j_graphrag_retriever", "Neo4j GraphRAG retriever / Neo4j driver", "application", 0.86, "Graph-aware retrieval layer that grounds LLM prompts with Cypher and graph context.")
    add("azure_ai_search_optional", "Optional Azure AI Search", "search", 0.72, "Optional hybrid, keyword, vector, or semantic retrieval alongside graph retrieval.")
    add("graphrag_api", "GraphRAG API + Azure OpenAI orchestration", "application", 0.84, "Application service coordinating retrieval, prompt construction, Azure OpenAI calls, grounding, and responses.")

    if has_lambda:
        add("azure_functions", "Azure Functions", "compute", 0.84, "Lambda-style serverless APIs, jobs, or event handlers.")
    if has_ec2:
        add("azure_virtual_machines", "Azure Virtual Machines", "compute", 0.78, "EC2-style lift-and-shift runtime where refactoring is not planned.")
    if has_eks:
        add("azure_kubernetes_service", "Azure Kubernetes Service", "compute", 0.84, "EKS-style container orchestration for GraphRAG services or self-managed Neo4j.")
    add("azure_app_hosting", "App Service / Container Apps", "compute", 0.8, "Managed application hosting for GraphRAG APIs and user-facing apps.")

    add("azure_virtual_network", "Azure Virtual Network", "networking", 0.86, "Private network boundary for graph, AI, app, and data services.")
    add("private_endpoints", "Private Endpoints / Private Link", "networking", 0.84, "Private access to storage, AI, search, and data services.")
    add("managed_identity", "Managed Identity + Entra ID / RBAC", "security", 0.84, "Workload identity and least-privilege access control.")
    add("azure_key_vault", "Azure Key Vault", "security", 0.84, "Secrets, connection strings, certificates, and key management.")
    add("azure_monitor", "Azure Monitor + Log Analytics + Application Insights", "observability", 0.86, "Metrics, logs, traces, application telemetry, alerts, and dashboards.")
    add("azure_policy_defender", "Azure Policy + Defender for Cloud", "security", 0.78, "Governance, posture management, compliance, and security recommendations.")

    _rel(relationships, "data_sources", "adls_gen2", "lands_files")
    _rel(relationships, "data_sources", "azure_event_hubs_kafka", "streams_events")
    _rel(relationships, "data_sources", "azure_synapse_fabric", "warehouse_data")
    _rel(relationships, "azure_data_factory", "adls_gen2", "orchestrates_ingestion")
    _rel(relationships, "adls_gen2", "extraction_jobs", "documents_for_parsing")
    _rel(relationships, "azure_event_hubs_kafka", "extraction_jobs", "stream_events")
    _rel(relationships, "azure_synapse_fabric", "extraction_jobs", "analytical_context")
    _rel(relationships, "azure_machine_learning", "extraction_jobs", "ml_enrichment")
    _rel(relationships, "azure_openai_ai_foundry", "extraction_jobs", "entity_extraction")
    _rel(relationships, "extraction_jobs", "neo4j_cypher_ingestion", "graph_ready_output")
    _rel(relationships, "neo4j_cypher_ingestion", "neo4j_auradb", "writes_graph")

    _rel(relationships, "neo4j_auradb", "neo4j_bloom", "visualizes")
    _rel(relationships, "neo4j_auradb", "neo4j_graph_data_science", "graph_algorithms")
    _rel(relationships, "neo4j_auradb", "neo4j_graphrag_retriever", "cypher_retrieval")
    _rel(relationships, "neo4j_graph_data_science", "neo4j_graphrag_retriever", "ranked_graph_context")
    _rel(relationships, "azure_ai_search_optional", "neo4j_graphrag_retriever", "optional_hybrid_retrieval")
    _rel(relationships, "neo4j_graphrag_retriever", "graphrag_api", "grounds_prompts")
    _rel(relationships, "azure_openai_ai_foundry", "graphrag_api", "generates_responses")

    for app_id in ["azure_functions", "azure_app_hosting", "azure_kubernetes_service", "azure_virtual_machines"]:
        if app_id in components:
            _rel(relationships, app_id, "graphrag_api", "hosts_or_calls")
            _rel(relationships, app_id, "managed_identity", "authorized_by")
            _rel(relationships, app_id, "azure_monitor", "emits_telemetry")

    for component_id in [
        "adls_gen2",
        "azure_event_hubs_kafka",
        "azure_data_factory",
        "azure_synapse_fabric",
        "extraction_jobs",
        "azure_machine_learning",
        "azure_openai_ai_foundry",
        "neo4j_cypher_ingestion",
        "neo4j_auradb",
        "neo4j_graphrag_retriever",
        "azure_ai_search_optional",
        "graphrag_api",
    ]:
        _rel(relationships, "azure_virtual_network", component_id, "network_boundary")
        _rel(relationships, component_id, "private_endpoints", "private_access")
        _rel(relationships, component_id, "azure_key_vault", "uses_secrets_or_keys")
        _rel(relationships, component_id, "azure_monitor", "emits_telemetry")

    _rel(relationships, "managed_identity", "azure_openai_ai_foundry", "authorizes")
    _rel(relationships, "azure_policy_defender", "azure_virtual_network", "governs")

    return TargetArchitecture(
        provider="azure",
        summary=(
            "Proposed Azure GraphRAG target preserving the AWS Neo4j architecture: Redshift/S3/MSK/Glue-style "
            "sources land in Synapse/Fabric, ADLS Gen2, Event Hubs with Kafka support, and Data Factory; parsing "
            "and extraction run through Azure Machine Learning, Azure OpenAI/Azure AI Foundry, Functions or Databricks; "
            "Neo4j AuraDB on Azure or Neo4j on AKS/VMs remains the knowledge graph; GraphRAG retrieval uses the "
            "Neo4j driver/retriever with optional Azure AI Search; application runtimes map to Azure Functions, "
            "App Service/Container Apps, AKS, or VMs under Azure platform controls."
        ),
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=[
            "Do not replace Neo4j with Cosmos DB unless the migration explicitly includes a graph database redesign away from Cypher, Bloom, Graph Data Science, and Neo4j drivers.",
            "Use Neo4j AuraDB on Azure for a managed graph database option, or deploy Neo4j on AKS/VMs when platform, licensing, or topology requirements demand self-management.",
            "Use Azure OpenAI / Azure AI Foundry as the Bedrock equivalent for LLM calls and AI orchestration.",
            "Use Azure AI Search only as an optional hybrid/vector retrieval layer; it complements but does not replace the Neo4j knowledge graph.",
            "Use Event Hubs with Kafka support for MSK-style streaming; IoT Hub is intentionally omitted unless device management is in scope.",
            "Validate Kafka client compatibility, retention, partitions, consumer groups, and unsupported broker-level features before replacing Amazon MSK with Event Hubs Kafka support.",
            "Map Lambda to Azure Functions, EKS to AKS, and EC2 to Azure VMs or managed app hosting based on runtime and modernization goals.",
        ],
    )


def _generate_gcp_graphrag_target(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> TargetArchitecture:
    source_text = (
        _architecture_text(source_architecture)
        + " "
        + " ".join(f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings)
    ).lower()
    has_lambda = _mentions(source_text, ["lambda", "cloud functions", "cloud run functions"])
    has_ec2 = _mentions(source_text, ["ec2", "compute engine", "virtual machines"])
    has_eks = _mentions(source_text, ["eks", "kubernetes", "gke"])

    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    def add(
        component_id: str,
        name: str,
        category: str,
        confidence: float,
        description: str,
        provider: str = "gcp",
    ) -> None:
        _add_component(components, component_id, name, provider, category, confidence, description)

    add("data_sources", "Redshift / S3 / MSK / Glue inputs", "external", 0.88, "Existing AWS data sources feeding the GraphRAG workload.", "external")
    add("bigquery", "BigQuery - Redshift replacement", "database", 0.86, "Redshift-style warehouse and analytical source data.")
    add("cloud_storage", "Cloud Storage - S3 landing zone", "storage", 0.88, "S3-style object, document, and graph ingestion landing zone.")
    add("managed_kafka", "Managed Service for Apache Kafka", "messaging", 0.82, "MSK-compatible streaming option when Kafka client compatibility is required.")
    add("cloud_data_fusion_dataflow", "Cloud Data Fusion / Dataflow / Dataproc", "analytics", 0.82, "Glue-style ETL, managed pipelines, Beam processing, or Spark processing options.")

    add("parsing_jobs", "Cloud Run jobs / Dataflow parsing", "compute", 0.82, "Parsing, chunking, entity extraction, and graph-ready transformation jobs.")
    add("vertex_ai", "Vertex AI", "ml", 0.84, "SageMaker-style ML pipelines, notebooks, embeddings, and model operations.")
    add("vertex_ai_gemini", "Vertex AI / Gemini", "ml", 0.86, "Bedrock-style foundation model access and AI orchestration.")
    add("neo4j_cypher_ingestion", "Neo4j driver / Cypher ingestion service", "application", 0.82, "Application service that writes extracted entities and relationships into Neo4j.")

    add("neo4j_auradb_gcp", "Neo4j AuraDB on Google Cloud", "database", 0.88, "Central graph database and knowledge graph store.")
    add("neo4j_bloom", "Neo4j Bloom", "application", 0.78, "Graph exploration and stakeholder visualization capability retained from the Neo4j ecosystem.")
    add("neo4j_graph_data_science", "Neo4j Graph Data Science / AuraDS", "analytics", 0.8, "Graph algorithms, embeddings, similarity, ranking, and graph analytics.")

    add("neo4j_graphrag_retriever", "Neo4j GraphRAG retriever / Cypher retrieval", "application", 0.86, "Graph-aware retrieval layer that grounds LLM prompts with Cypher and graph context.")
    add("vertex_ai_vector_search_optional", "Optional Vertex AI Vector Search", "search", 0.72, "Optional hybrid, keyword, or vector retrieval alongside graph retrieval.")
    add("graphrag_api", "GraphRAG API + Vertex AI orchestration", "application", 0.84, "Application service coordinating retrieval, prompt construction, Vertex AI calls, grounding, and responses.")

    if has_lambda:
        add("cloud_run_functions", "Cloud Run functions / Cloud Functions", "compute", 0.84, "Lambda-style serverless APIs, jobs, or event handlers.")
    if has_ec2:
        add("compute_engine", "Compute Engine", "compute", 0.78, "EC2-style lift-and-shift runtime where refactoring is not planned.")
    if has_eks:
        add("google_kubernetes_engine", "Google Kubernetes Engine", "compute", 0.84, "EKS-style container orchestration for GraphRAG services or self-managed Neo4j.")
    add("cloud_run_services", "Cloud Run services", "compute", 0.8, "Managed application hosting for GraphRAG APIs and user-facing services.")

    add("vpc_network", "VPC Network", "networking", 0.86, "Private network boundary for graph, AI, app, and data services.")
    add("private_service_connect", "Private Service Connect", "networking", 0.84, "Private access to managed services from inside the VPC.")
    add("cloud_iam", "Cloud IAM", "security", 0.84, "Workload identity and least-privilege access control.")
    add("secret_manager", "Secret Manager", "security", 0.84, "Application secrets, connection strings, and credentials.")
    add("cloud_kms", "Cloud KMS", "security", 0.82, "Managed encryption keys.")
    add("cloud_monitoring_logging", "Cloud Monitoring + Cloud Logging", "observability", 0.86, "Metrics, logs, traces, alerts, and dashboards.")
    add("cloud_armor_firewall", "Cloud Armor + firewall policies", "security", 0.78, "Edge protection, WAF policy, and VPC firewall guardrails.")
    add("vpc_service_controls", "VPC Service Controls", "security", 0.76, "Optional service perimeter controls for sensitive managed services.")

    _rel(relationships, "data_sources", "bigquery", "warehouse_data")
    _rel(relationships, "data_sources", "cloud_storage", "lands_files")
    _rel(relationships, "data_sources", "managed_kafka", "streams_events")
    _rel(relationships, "cloud_data_fusion_dataflow", "cloud_storage", "orchestrates_ingestion")
    _rel(relationships, "cloud_storage", "parsing_jobs", "documents_for_parsing")
    _rel(relationships, "managed_kafka", "parsing_jobs", "stream_events")
    _rel(relationships, "bigquery", "parsing_jobs", "analytical_context")
    _rel(relationships, "vertex_ai", "parsing_jobs", "ml_enrichment")
    _rel(relationships, "vertex_ai_gemini", "parsing_jobs", "entity_extraction")
    _rel(relationships, "parsing_jobs", "neo4j_cypher_ingestion", "graph_ready_output")
    _rel(relationships, "neo4j_cypher_ingestion", "neo4j_auradb_gcp", "writes_graph")

    _rel(relationships, "neo4j_auradb_gcp", "neo4j_bloom", "visualizes")
    _rel(relationships, "neo4j_auradb_gcp", "neo4j_graph_data_science", "graph_algorithms")
    _rel(relationships, "neo4j_auradb_gcp", "neo4j_graphrag_retriever", "cypher_retrieval")
    _rel(relationships, "neo4j_graph_data_science", "neo4j_graphrag_retriever", "ranked_graph_context")
    _rel(relationships, "vertex_ai_vector_search_optional", "neo4j_graphrag_retriever", "optional_hybrid_retrieval")
    _rel(relationships, "neo4j_graphrag_retriever", "graphrag_api", "grounds_prompts")
    _rel(relationships, "vertex_ai_gemini", "graphrag_api", "generates_responses")

    for app_id in ["cloud_run_functions", "cloud_run_services", "google_kubernetes_engine", "compute_engine"]:
        if app_id in components:
            _rel(relationships, app_id, "graphrag_api", "hosts_or_calls")
            _rel(relationships, app_id, "cloud_iam", "authorized_by")
            _rel(relationships, app_id, "cloud_monitoring_logging", "emits_telemetry")

    for component_id in [
        "bigquery",
        "cloud_storage",
        "managed_kafka",
        "cloud_data_fusion_dataflow",
        "parsing_jobs",
        "vertex_ai",
        "vertex_ai_gemini",
        "neo4j_cypher_ingestion",
        "neo4j_auradb_gcp",
        "neo4j_graphrag_retriever",
        "vertex_ai_vector_search_optional",
        "graphrag_api",
    ]:
        _rel(relationships, "vpc_network", component_id, "network_boundary")
        _rel(relationships, component_id, "private_service_connect", "private_access")
        _rel(relationships, component_id, "secret_manager", "uses_secrets")
        _rel(relationships, component_id, "cloud_kms", "uses_encryption_keys")
        _rel(relationships, component_id, "cloud_monitoring_logging", "emits_telemetry")

    _rel(relationships, "cloud_iam", "vertex_ai_gemini", "authorizes")
    _rel(relationships, "cloud_armor_firewall", "vpc_network", "protects")
    _rel(relationships, "vpc_service_controls", "private_service_connect", "service_perimeter")

    return TargetArchitecture(
        provider="gcp",
        summary=(
            "Proposed Google Cloud GraphRAG target preserving the AWS Neo4j architecture: Redshift/S3/MSK/Glue-style "
            "sources map to BigQuery, Cloud Storage, Managed Service for Apache Kafka, and Cloud Data Fusion/Dataflow; "
            "parsing and extraction run through Cloud Run jobs, Dataflow, Vertex AI, and Gemini; Neo4j AuraDB on "
            "Google Cloud remains the knowledge graph; GraphRAG retrieval uses Neo4j/Cypher with optional Vertex AI "
            "Vector Search; application runtimes map to Cloud Run functions, Cloud Run services, GKE, or Compute Engine "
            "under Google Cloud platform controls."
        ),
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=[
            "Do not replace Neo4j with Cloud SQL Auth Proxy or another relational access proxy; keep Neo4j AuraDB on Google Cloud unless the migration explicitly redesigns away from Cypher, Bloom, Graph Data Science, and Neo4j drivers.",
            "Preserve Neo4j Bloom and Neo4j Graph Data Science / AuraDS when user exploration, graph algorithms, graph embeddings, or graph analytics are part of the source workload.",
            "Use Vertex AI / Gemini as the Bedrock and SageMaker modernization target for foundation-model calls, embeddings, extraction, and AI orchestration.",
            "Use Vertex AI Vector Search only as an optional hybrid/vector retrieval layer; it complements but does not replace the Neo4j knowledge graph.",
            "Use Managed Service for Apache Kafka when MSK client/topic compatibility is required; consider Pub/Sub only when the migration accepts a cloud-native eventing redesign.",
            "Validate Kafka client compatibility, retention, partitions, consumer groups, and unsupported broker-level features before replacing Amazon MSK.",
            "Map Lambda to Cloud Run functions or Cloud Functions, EKS to GKE, and EC2 to Compute Engine or Cloud Run based on runtime and modernization goals.",
        ],
    )


def _generate_azure_data_platform_target(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> TargetArchitecture:
    source_text = _architecture_text(source_architecture)
    mapping_text = " ".join(
        f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings
    ).lower()
    combined_text = f"{source_text} {mapping_text}"
    has_iot = _mentions(combined_text, ["iot", "device", "telemetry"])
    has_app = _mentions(combined_text, ["app engine", "compute engine", "app service", "container", "virtual machines"])
    has_datastore = _mentions(combined_text, ["datastore", "cosmos", "firestore"])
    has_bigquery = _mentions(combined_text, ["bigquery", "synapse", "fabric", "warehouse"])
    has_dataproc = _mentions(combined_text, ["dataproc", "databricks", "spark"])
    has_datalab = _mentions(combined_text, ["datalab", "machine learning", "notebook"])

    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    def add(
        component_id: str,
        name: str,
        category: str,
        confidence: float,
        description: str,
    ) -> None:
        _add_component(
            components,
            component_id,
            name,
            "azure",
            category,
            confidence,
            description,
        )

    add("iot_devices", "IoT Devices", "external", 0.9, "Existing devices sending telemetry into the platform.")
    add("standard_devices", "Standard Devices / Users", "external", 0.9, "Users, edge systems, or standard clients that use the migrated applications.")
    add("azure_virtual_network", "Azure Virtual Network", "networking", 0.9, "Network isolation boundary for private endpoints and application/data subnets.")
    add("private_endpoints", "Private Endpoints / Private Link", "networking", 0.84, "Private PaaS connectivity for storage, data, and application dependencies.")
    add("nsg_firewall_waf", "NSGs + Azure Firewall / WAF", "security", 0.82, "Network filtering, segmentation, and edge application protection.")
    add("azure_iot_hub", "Azure IoT Hub", "iot", 0.84, "Secure device identity, ingestion, cloud-to-device messaging, and device management.")
    add("azure_event_hubs", "Azure Event Hubs", "messaging", 0.86, "High-throughput telemetry and event ingestion replacement for Pub/Sub streaming patterns.")
    add("azure_stream_analytics", "Azure Stream Analytics", "analytics", 0.84, "Real-time stream processing.")
    add("azure_functions", "Azure Functions", "compute", 0.78, "Lightweight event-triggered processing.")
    add("adls_gen2", "Azure Data Lake Storage Gen2", "storage", 0.88, "Raw and curated zones on Blob Storage.")
    add("azure_data_factory", "Azure Data Factory", "analytics", 0.8, "Batch orchestration and ETL pipelines.")
    add("azure_databricks", "Azure Databricks", "analytics", 0.84, "Spark processing and Dataproc replacement.")
    add("azure_synapse", "Synapse Analytics or Microsoft Fabric", "database", 0.84, "Warehouse and lakehouse analytics.")
    if has_datastore:
        add("azure_cosmos_db", "Azure Cosmos DB", "database", 0.86, "Operational NoSQL serving store for Datastore-style workloads.")
    if has_app:
        add("azure_app_hosting", "App Service / Container Apps / AKS", "compute", 0.84, "Application serving options selected after runtime and deployment validation.")
    if has_datalab:
        add("azure_machine_learning", "Azure Machine Learning", "ml", 0.82, "ML training, notebooks, and MLOps.")
    add("consumers_bi_apis", "Consumers / BI / APIs", "client", 0.8, "Power BI, APIs, reporting users, and downstream consumers.")

    add("managed_identity", "Managed Identity + Entra ID / RBAC", "security", 0.86, "Identity, workload identity, and least-privilege access controls.")
    add("azure_key_vault", "Azure Key Vault", "security", 0.84, "Secrets, certificates, and key management.")
    add("azure_monitor", "Azure Monitor + Log Analytics + Application Insights", "observability", 0.86, "Centralized metrics, logs, traces, application telemetry, alerts, and dashboards.")
    add("azure_policy", "Azure Policy + Tags", "security", 0.78, "Governance, compliance guardrails, resource standards, and cost allocation.")
    add("azure_backup", "Azure Backup / Recovery Services", "resilience", 0.78, "Backup, recovery, retention, and DR coordination.")

    # Main source-preserving data flow.
    _rel(relationships, "iot_devices", "azure_iot_hub", "secure_device_ingestion")
    _rel(relationships, "standard_devices", "azure_event_hubs", "telemetry_ingestion")
    _rel(relationships, "azure_iot_hub", "azure_event_hubs", "routes_events")
    _rel(relationships, "azure_event_hubs", "azure_stream_analytics", "stream_processing")
    _rel(relationships, "azure_event_hubs", "azure_functions", "event_handlers")
    _rel(relationships, "azure_stream_analytics", "adls_gen2", "writes_raw_curated_data")
    _rel(relationships, "azure_functions", "adls_gen2", "writes_events")
    _rel(relationships, "azure_data_factory", "adls_gen2", "orchestrates_batch_etl")
    _rel(relationships, "adls_gen2", "azure_databricks", "spark_processing")
    if has_dataproc:
        _rel(relationships, "azure_databricks", "adls_gen2", "writes_curated_data")
    if has_bigquery:
        _rel(relationships, "adls_gen2", "azure_synapse", "serves_analytics")
        _rel(relationships, "azure_databricks", "azure_synapse", "publishes_curated_sets")
        _rel(relationships, "azure_synapse", "consumers_bi_apis", "serves_bi_and_reporting")
    if "azure_cosmos_db" in components:
        _rel(relationships, "azure_stream_analytics", "azure_cosmos_db", "serving_updates")
        if "azure_app_hosting" in components:
            _rel(relationships, "azure_app_hosting", "azure_cosmos_db", "reads_writes")
    if "azure_app_hosting" in components:
        _rel(relationships, "standard_devices", "azure_app_hosting", "uses_application")
        _rel(relationships, "azure_app_hosting", "adls_gen2", "uses_storage")
        _rel(relationships, "azure_app_hosting", "managed_identity", "uses_identity")
        _rel(relationships, "azure_app_hosting", "consumers_bi_apis", "serves_apis")
    if "azure_machine_learning" in components:
        _rel(relationships, "adls_gen2", "azure_machine_learning", "notebook_training_data")

    # Platform/security/operations guardrails.
    for component_id in [
        "azure_iot_hub",
        "azure_event_hubs",
        "azure_stream_analytics",
        "azure_functions",
        "adls_gen2",
        "azure_data_factory",
        "azure_databricks",
        "azure_synapse",
        "azure_cosmos_db",
        "azure_app_hosting",
        "azure_machine_learning",
        "consumers_bi_apis",
    ]:
        if component_id not in components:
            continue
        _rel(relationships, "azure_virtual_network", component_id, "network_boundary")
        _rel(relationships, component_id, "managed_identity", "authorized_by")
        _rel(relationships, component_id, "azure_monitor", "emits_telemetry")
        _rel(relationships, component_id, "azure_key_vault", "uses_secrets_or_keys")

    for component_id in ["adls_gen2", "azure_synapse", "azure_cosmos_db"]:
        if component_id in components:
            _rel(relationships, component_id, "private_endpoints", "private_access")
            _rel(relationships, component_id, "azure_backup", "protected_by")

    _rel(relationships, "azure_virtual_network", "private_endpoints", "contains")
    _rel(relationships, "nsg_firewall_waf", "azure_virtual_network", "protects")
    _rel(relationships, "azure_policy", "azure_virtual_network", "governs")

    return TargetArchitecture(
        provider="azure",
        summary=(
            "Proposed Azure data-platform target preserving the GCP source flow: device and client telemetry "
            "enters through IoT Hub/Event Hubs, is processed by Stream Analytics, Functions, Data Factory, "
            "and Databricks, lands in Azure Data Lake Storage Gen2, serves analytics through Synapse/Fabric, "
            "serves operational applications through Cosmos DB and app hosting, and is governed by VNet, "
            "Private Link, Entra ID/RBAC, Key Vault, Monitor, and Policy."
        ),
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=[
            "Use Azure IoT Hub for device identity, secure ingestion, device management, and cloud-to-device messaging.",
            "Use Azure Event Hubs for high-throughput telemetry ingestion; reserve Service Bus for command, queue, and enterprise messaging semantics.",
            "Treat Dataflow replacement as a pattern decision: Stream Analytics for real-time transformations, Databricks for Spark/Beam-style processing, and Data Factory for orchestration/batch movement.",
            "Use Azure Data Lake Storage Gen2 on Blob Storage as the raw and curated data lake for analytics workloads.",
            "Use Synapse Analytics or Microsoft Fabric for BigQuery-style warehouse/lakehouse analytics after query, cost, and BI dependency review.",
            "Use Cosmos DB for Datastore-style operational NoSQL serving workloads.",
            "Use Azure Monitor, Log Analytics, Application Insights, Managed Identity, Key Vault, Private Endpoints, NSGs, Azure Firewall/WAF, Azure Policy, and Backup as cross-cutting production controls.",
        ],
    )


def _is_data_platform_source(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> bool:
    text = (
        _architecture_text(source_architecture)
        + " "
        + " ".join(f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings)
    ).lower()
    tokens = [
        "pub/sub",
        "pubsub",
        "dataflow",
        "bigquery",
        "dataproc",
        "datalab",
        "datastore",
        "cloud storage",
        "iot",
        "telemetry",
        "event hubs",
        "stream analytics",
        "synapse",
        "databricks",
    ]
    return sum(1 for token in tokens if token in text) >= 2


def _is_graphrag_source(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> bool:
    text = (
        _architecture_text(source_architecture)
        + " "
        + " ".join(f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings)
    ).lower()
    graph_tokens = [
        "neo4j",
        "graphrag",
        "graph rag",
        "knowledge graph",
        "graph database",
        "graph data science",
        "cypher",
        "bloom",
    ]
    ai_tokens = ["bedrock", "sagemaker", "openai", "ai foundry", "machine learning", "vertex ai", "gemini"]
    return any(token in text for token in graph_tokens) and any(token in text for token in ai_tokens)


def _generate_gcp_hybrid_connectivity_target(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> TargetArchitecture:
    components: dict[str, ArchitectureComponent] = {}
    relationships: list[ArchitectureRelationship] = []

    def add(
        component_id: str,
        name: str,
        category: str,
        confidence: float,
        description: str,
        provider: str = "gcp",
    ) -> None:
        _add_component(
            components,
            component_id,
            name,
            provider,
            category,
            confidence,
            description,
        )

    add("on_premises_network", "On-premises network", "external", 0.9, "Existing customer network that remains connected to the cloud environment.", "external")
    add("customer_edge_routers", "Customer edge routers (HA)", "networking", 0.86, "Redundant customer routers exchanging BGP routes with Google Cloud.", "external")
    add("colo_or_service_provider", "Colocation / service provider edge", "networking", 0.78, "Direct or provider-mediated handoff point for Interconnect.")
    add("google_edge", "Google edge", "networking", 0.78, "Google network edge receiving private connectivity.")
    add("dedicated_interconnect", "Dedicated Interconnect", "networking", 0.84, "Direct private connectivity option to Google Cloud.")
    add("partner_interconnect", "Partner Interconnect option", "networking", 0.78, "Provider-mediated private connectivity option when direct colocation is not preferred.")
    add("vlan_attachments", "VLAN attachments", "networking", 0.86, "Logical attachments connecting Interconnect to Cloud Router and the VPC.")
    add("cloud_router", "Cloud Router with BGP", "networking", 0.9, "Dynamic routing control plane for Interconnect and HA VPN.")
    add("ha_vpn_tunnels", "HA VPN tunnels (2) with BGP", "networking", 0.84, "Redundant IPsec VPN backup path.")
    add("ha_vpn_gateway", "HA VPN gateway", "networking", 0.84, "Production-grade Cloud VPN gateway for failover connectivity.")
    add("shared_vpc", "Shared VPC / VPC Network", "networking", 0.9, "Network boundary for regional subnets, routes, firewall policy, and shared services.")
    add("regional_private_subnets", "Regional private workload subnets", "networking", 0.86, "Regional subnet IP ranges for private workloads without direct external IPs.")
    add("public_lb_tier", "Public-facing load balancer tier", "networking", 0.78, "Public exposure through Cloud Load Balancing rather than public workload IPs.")
    add("cloud_nat", "Cloud NAT for private egress", "networking", 0.8, "Outbound internet access for private workloads without external IPs.")
    add("private_service_connect", "Private Service Connect", "networking", 0.82, "Private access to managed services from inside the VPC.")
    add("private_google_access", "Private Google Access", "networking", 0.8, "Private subnet access to Google APIs without public IPs.")
    add("firewall_policies", "Firewall policies", "security", 0.82, "VPC and hierarchical firewall policy enforcement.")
    add("vpc_service_controls", "VPC Service Controls", "security", 0.78, "Service perimeter controls to reduce data exfiltration risk for managed services.")
    add("cloud_dns", "Cloud DNS", "networking", 0.8, "Managed private and public DNS zones for the migrated environment.")
    add("cloud_iam", "Cloud IAM", "security", 0.84, "Identity and least-privilege access control.")
    add("cloud_kms", "Cloud KMS", "security", 0.82, "Managed encryption keys.")
    add("secret_manager", "Secret Manager", "security", 0.82, "Centralized application secrets.")
    add("cloud_monitoring_logging", "Cloud Monitoring + Cloud Logging", "observability", 0.84, "Metrics, logs, alerts, dashboards, and operational telemetry.")

    _rel(relationships, "on_premises_network", "customer_edge_routers", "connects_to")
    _rel(relationships, "customer_edge_routers", "colo_or_service_provider", "private_handoff")
    _rel(relationships, "colo_or_service_provider", "google_edge", "google_edge_handoff")
    _rel(relationships, "google_edge", "dedicated_interconnect", "direct_option")
    _rel(relationships, "google_edge", "partner_interconnect", "provider_option")
    _rel(relationships, "dedicated_interconnect", "vlan_attachments", "primary_vlan_attachments")
    _rel(relationships, "partner_interconnect", "vlan_attachments", "alternative_vlan_attachments")
    _rel(relationships, "vlan_attachments", "cloud_router", "bgp_sessions")
    _rel(relationships, "customer_edge_routers", "ha_vpn_tunnels", "backup_bgp_over_ipsec")
    _rel(relationships, "ha_vpn_tunnels", "ha_vpn_gateway", "two_ipsec_tunnels")
    _rel(relationships, "ha_vpn_gateway", "cloud_router", "backup_dynamic_routes")
    _rel(relationships, "cloud_router", "shared_vpc", "advertises_routes")
    _rel(relationships, "shared_vpc", "regional_private_subnets", "contains")
    _rel(relationships, "shared_vpc", "public_lb_tier", "contains")
    _rel(relationships, "public_lb_tier", "regional_private_subnets", "forwards_to")
    _rel(relationships, "regional_private_subnets", "cloud_nat", "private_egress")
    _rel(relationships, "regional_private_subnets", "private_service_connect", "private_access")
    _rel(relationships, "regional_private_subnets", "private_google_access", "google_api_access")
    _rel(relationships, "firewall_policies", "shared_vpc", "protects")
    _rel(relationships, "cloud_dns", "shared_vpc", "resolves")
    _rel(relationships, "vpc_service_controls", "private_service_connect", "service_perimeter")
    _rel(relationships, "cloud_iam", "cloud_router", "authorizes")
    _rel(relationships, "cloud_kms", "regional_private_subnets", "encrypts_workloads")
    _rel(relationships, "secret_manager", "regional_private_subnets", "provides_secrets")
    _rel(relationships, "cloud_monitoring_logging", "cloud_router", "monitors")
    _rel(relationships, "cloud_monitoring_logging", "shared_vpc", "observes")

    return TargetArchitecture(
        provider="gcp",
        summary=(
            "Proposed Google Cloud hybrid connectivity target preserving the Azure ExpressRoute and VPN gateway pattern: "
            "on-premises networks connect through customer edge routers to Dedicated or Partner Interconnect, use VLAN "
            "attachments and Cloud Router with BGP for primary private routing, use HA VPN with two IPsec tunnels as "
            "backup, and route into Shared VPC/regional private workload subnets with Cloud NAT, Private Service Connect, "
            "Private Google Access, firewall policies, Cloud DNS, IAM, KMS, Secret Manager, Monitoring, Logging, and VPC Service Controls."
        ),
        components=list(components.values()),
        relationships=_dedupe_relationships(relationships, components),
        design_notes=[
            "Use Cloud Router as the central dynamic BGP routing control plane for both Cloud Interconnect and HA VPN.",
            "Use VLAN attachments between Dedicated or Partner Interconnect and Cloud Router; do not model Interconnect as directly attached to workloads.",
            "Treat Dedicated Interconnect and Partner Interconnect as design alternatives; select based on colocation access, bandwidth, SLA, and provider requirements.",
            "Use HA VPN with two IPsec tunnels and BGP as the backup path to preserve the ExpressRoute plus VPN fallback pattern.",
            "In GCP, subnets are regional IP ranges; workloads are public or private based on external IPs, routes, Cloud NAT, firewall policies, and load balancers.",
            "Use Private Service Connect and Private Google Access for private managed-service access, and VPC Service Controls where sensitive managed services need exfiltration protection.",
        ],
    )


def _is_hybrid_connectivity_source(
    source_architecture: SourceArchitecture,
    service_mappings: list[ServiceMapping],
) -> bool:
    text = (
        _architecture_text(source_architecture)
        + " "
        + " ".join(f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings)
    ).lower()
    tokens = [
        "expressroute",
        "express route",
        "vpn gateway",
        "virtual network gateway",
        "gateway subnet",
        "on-premises",
        "on premises",
        "local edge router",
        "microsoft edge router",
        "cloud interconnect",
        "dedicated interconnect",
        "partner interconnect",
        "cloud router",
        "ha vpn",
        "vlan attachment",
    ]
    return any(token in text for token in tokens)


def _provider_profile(provider: str) -> dict[str, tuple[str, str, str, str]]:
    profiles = {
        "azure": {
            "network": (
                "azure_virtual_network",
                "Azure Virtual Network",
                "networking",
                "Network isolation boundary with subnets, route tables, and network security controls.",
            ),
            "public": (
                "azure_public_subnets",
                "Public subnets",
                "networking",
                "Ingress-facing subnet tier for application gateways, load balancers, or NAT.",
            ),
            "private": (
                "azure_private_subnets",
                "Private subnets",
                "networking",
                "Application and data subnet tier isolated from direct public ingress.",
            ),
            "dns": ("azure_dns", "Azure DNS", "networking", "DNS entry point for migrated workloads."),
            "load_balancer": (
                "azure_application_gateway",
                "Azure Application Gateway / Load Balancer",
                "networking",
                "Managed application or network load balancing for production ingress.",
            ),
            "identity": (
                "azure_identity",
                "Microsoft Entra ID / Azure RBAC",
                "security",
                "Identity, role assignment, and least-privilege access controls.",
            ),
            "secrets": (
                "azure_key_vault",
                "Azure Key Vault",
                "security",
                "Centralized secrets, certificates, and key management.",
            ),
            "encryption": (
                "azure_key_vault_keys",
                "Azure Key Vault keys",
                "security",
                "Managed encryption keys for data protection.",
            ),
            "observability": (
                "azure_monitor",
                "Azure Monitor + Log Analytics",
                "observability",
                "Metrics, logs, alerts, dashboards, and operational analytics.",
            ),
            "backup": (
                "azure_backup",
                "Azure Backup",
                "resilience",
                "Backup policy and restore orchestration.",
            ),
        },
        "gcp": {
            "network": (
                "gcp_vpc_network",
                "VPC Network",
                "networking",
                "Network isolation boundary with subnets, routes, and firewall controls.",
            ),
            "public": (
                "gcp_public_subnets",
                "Public subnets",
                "networking",
                "Ingress-facing subnet tier for load balancers or NAT.",
            ),
            "private": (
                "gcp_private_subnets",
                "Private subnets",
                "networking",
                "Application and data subnet tier isolated from direct public ingress.",
            ),
            "dns": ("cloud_dns", "Cloud DNS", "networking", "DNS entry point for migrated workloads."),
            "load_balancer": (
                "cloud_load_balancing",
                "Cloud Load Balancing",
                "networking",
                "Managed global or regional load balancing for production ingress.",
            ),
            "identity": (
                "cloud_iam",
                "Cloud IAM",
                "security",
                "Identity, role assignment, and least-privilege access controls.",
            ),
            "secrets": (
                "secret_manager",
                "Secret Manager",
                "security",
                "Centralized application secrets.",
            ),
            "encryption": (
                "cloud_kms",
                "Cloud KMS",
                "security",
                "Managed encryption keys for data protection.",
            ),
            "observability": (
                "cloud_monitoring_logging",
                "Cloud Monitoring + Cloud Logging",
                "observability",
                "Metrics, logs, alerting, and operational dashboards.",
            ),
            "backup": (
                "backup_dr",
                "Backup and DR Service",
                "resilience",
                "Backup policy and restore orchestration.",
            ),
        },
    }
    return profiles.get(provider, profiles["gcp"])


def _provider_key(provider: str | None) -> str:
    normalized = (provider or "unknown").strip().lower().replace("-", " ")
    if "azure" in normalized:
        return "azure"
    if "gcp" in normalized or "google cloud" in normalized:
        return "gcp"
    if "aws" in normalized or "amazon web services" in normalized:
        return "aws"
    return normalized.replace(" ", "_")


def _provider_label(provider: str | None) -> str:
    key = _provider_key(provider)
    if key == "azure":
        return "Azure"
    if key == "gcp":
        return "Google Cloud"
    if key == "aws":
        return "AWS"
    return (provider or "target provider").upper()


def _add_component(
    components: dict[str, ArchitectureComponent],
    component_id: str,
    name: str,
    provider: str,
    category: str,
    confidence: float,
    description: str,
) -> None:
    if component_id not in components:
        components[component_id] = ArchitectureComponent(
            id=component_id,
            name=name,
            provider=provider,
            service_type=name,
            category=category,
            confidence=confidence,
            description=description,
        )


def _rel(
    relationships: list[ArchitectureRelationship],
    source_id: str,
    target_id: str,
    relationship_type: str,
) -> None:
    relationships.append(
        ArchitectureRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
        )
    )


def _dedupe_relationships(
    relationships: list[ArchitectureRelationship],
    components: dict[str, ArchitectureComponent],
) -> list[ArchitectureRelationship]:
    known_ids = set(components)
    seen: set[tuple[str, str, str]] = set()
    deduped: list[ArchitectureRelationship] = []
    for relationship in relationships:
        key = (
            relationship.source_id,
            relationship.target_id,
            relationship.relationship_type,
        )
        if relationship.source_id not in known_ids or relationship.target_id not in known_ids:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(relationship)
    return deduped


def _category_for_service(service_name: str) -> str:
    lower = service_name.lower()
    if "iot core" in lower:
        return "iot"
    if any(
        token in lower
        for token in [
            "ecs",
            "ec2",
            "lambda",
            "beanstalk",
            "app runner",
            "application hosting",
            "app service",
            "azure functions",
            "virtual machines",
            "container apps",
            "kubernetes service",
            "aks",
            "compute engine",
            "app engine",
            "cloud run",
            "cloud functions",
            "google kubernetes engine",
            "gke",
            "azure functions",
            "azure virtual machines",
            "azure kubernetes service",
            "app service",
            "container apps",
        ]
    ):
        return "compute"
    if any(
        token in lower
        for token in [
            "rds",
            "aurora",
            "dynamodb",
            "documentdb",
            "redshift",
            "sql database",
            "database for postgresql",
            "cosmos db",
            "synapse",
            "fabric",
            "cloud sql",
            "alloydb",
            "firestore",
            "bigtable",
            "bigquery",
            "neo4j",
            "auradb",
            "graph database",
        ]
    ):
        return "database"
    if any(token in lower for token in ["s3", "blob storage", "cloud storage", "data lake storage", "adls"]):
        return "storage"
    if any(
        token in lower
        for token in [
            "secrets",
            "secret manager",
            "kms",
            "iam",
            "waf",
            "key vault",
            "entra",
            "rbac",
            "cloud armor",
            "vpc service controls",
        ]
    ):
        return "security"
    if any(token in lower for token in ["cloudwatch", "monitor", "logging", "log analytics", "opensearch"]):
        return "observability"
    if any(
        token in lower
        for token in [
            "sqs",
            "sns",
            "eventbridge",
            "kinesis",
            "service bus",
            "event grid",
            "event hubs",
            "pub/sub",
            "pubsub",
            "cloud tasks",
            "eventarc",
            "managed service for apache kafka",
            "apache kafka",
        ]
    ):
        return "messaging"
    if any(
        token in lower
        for token in [
            "glue",
            "emr",
            "athena",
            "flink",
            "data factory",
            "stream analytics",
            "databricks",
            "hdinsight",
            "dataflow",
            "dataproc",
            "graph data science",
            "fabric data factory",
            "cloud data fusion",
        ]
    ):
        return "analytics"
    if any(token in lower for token in ["sagemaker", "machine learning", "datalab", "bedrock", "openai", "ai foundry", "vertex ai", "gemini"]):
        return "ml"
    if any(token in lower for token in ["backup", "dr service"]):
        return "resilience"
    if any(
        token in lower
        for token in [
            "vpc",
            "subnet",
            "load balancer",
            "load balancing",
            "route 53",
            "direct connect",
            "ipsec",
            "tunnel",
            "transit vif",
            "transit gateway",
            "route table",
            "vpc attachment",
            "attachment",
            "site-to-site vpn",
            "site to site vpn",
            "vpn",
            "gateway",
            "cloudfront",
            "api gateway",
            "virtual network",
            "vnet",
            "application gateway",
            "azure load balancer",
            "front door",
            "vpc network",
            "cloud load balancing",
            "cloud dns",
            "cloud interconnect",
            "dedicated interconnect",
            "partner interconnect",
            "cloud router",
            "vlan attachment",
            "ha vpn",
            "cloud vpn",
            "cloud nat",
            "private service connect",
            "private google access",
            "firewall policies",
            "shared vpc",
        ]
    ):
        return "networking"
    return "application"


def _component_id_for_service(service_name: str) -> str:
    normalized = _normalize(service_name)
    canonical_ids = [
        ("amazon cloudwatch + aws cloudtrail + amazon opensearch service", "aws_observability_stack"),
        ("cloudwatch + cloudtrail + opensearch", "aws_observability_stack"),
        ("cloudwatch cloudtrail opensearch", "aws_observability_stack"),
        ("amazon cloudwatch aws cloudtrail amazon opensearch service", "aws_observability_stack"),
        ("amazon athena + aws glue data catalog", "amazon_athena_glue_catalog"),
        ("amazon athena aws glue data catalog", "amazon_athena_glue_catalog"),
        ("amazon athena", "amazon_athena_glue_catalog"),
        ("athena glue data catalog", "amazon_athena_glue_catalog"),
        ("amazon managed service for apache flink", "amazon_managed_flink"),
        ("managed service for apache flink", "amazon_managed_flink"),
        ("aws application hosting options", "aws_application_hosting_options"),
        ("application hosting options", "aws_application_hosting_options"),
        ("amazon sns + amazon sqs", "amazon_sns_sqs"),
        ("sns + sqs", "amazon_sns_sqs"),
        ("aws elastic beanstalk", "aws_elastic_beanstalk"),
        ("elastic beanstalk", "aws_elastic_beanstalk"),
        ("amazon ec2", "amazon_ec2"),
        ("amazon sns", "amazon_sns"),
        ("amazon sqs", "amazon_sqs"),
        ("amazon eventbridge", "amazon_eventbridge"),
        ("aws iot core", "aws_iot_core"),
        ("amazon kinesis", "amazon_kinesis"),
        ("aws glue", "aws_glue"),
        ("amazon emr", "amazon_emr"),
        ("amazon redshift", "amazon_redshift"),
        ("amazon sagemaker studio", "amazon_sagemaker_studio"),
        ("amazon sagemaker", "amazon_sagemaker_studio"),
        ("amazon s3", "amazon_s3"),
        ("amazon dynamodb", "amazon_dynamodb"),
        ("transit gateway vpc attachment", "tgw_vpc_attachment"),
        ("vpc attachment", "tgw_vpc_attachment"),
        ("direct connect gateway", "aws_direct_connect_gateway"),
        ("redundant direct connect", "aws_direct_connect"),
        ("direct connect connections", "aws_direct_connect"),
        ("direct connect", "aws_direct_connect"),
        ("ipsec vpn tunnels", "ipsec_vpn_tunnels"),
        ("vpn tunnels", "ipsec_vpn_tunnels"),
        ("transit vif", "transit_vif"),
        ("site to site vpn attachment", "aws_site_to_site_vpn"),
        ("site-to-site vpn attachment", "aws_site_to_site_vpn"),
        ("site to site vpn", "aws_site_to_site_vpn"),
        ("site-to-site vpn", "aws_site_to_site_vpn"),
        ("vpn gateway", "aws_site_to_site_vpn"),
        ("transit gateway route table", "tgw_route_table"),
        ("tgw route table", "tgw_route_table"),
        ("private subnet route tables", "private_route_tables"),
        ("private route tables", "private_route_tables"),
        ("transit gateway", "aws_transit_gateway"),
        ("vpc subnet", "private_subnets"),
        ("gateway subnet", "private_subnets"),
        ("public subnet", "public_subnets"),
        ("private subnet", "private_subnets"),
        ("application load balancer", "application_load_balancer"),
        ("elastic load balancing", "elastic_load_balancing"),
        ("elastic load balancer", "elastic_load_balancing"),
        ("amazon virtual private cloud", "vpc"),
        ("amazon vpc", "vpc"),
        ("virtual private cloud", "vpc"),
        ("route 53", "route53"),
        ("secrets manager", "aws_secrets_manager"),
        ("kms", "aws_kms"),
        ("iam", "iam"),
        ("cloudwatch", "amazon_cloudwatch"),
        ("backup", "aws_backup"),
        ("waf", "aws_waf"),
    ]
    for token, component_id in canonical_ids:
        if token in normalized:
            return component_id
    return _slug(service_name)


def _canonical_service_name(service_name: str) -> str:
    component_id = _component_id_for_service(service_name)
    canonical_names = {
        "aws_direct_connect_gateway": "AWS Direct Connect Gateway",
        "aws_direct_connect": "Redundant Direct Connect connections",
        "ipsec_vpn_tunnels": "IPsec VPN tunnels (2) with BGP",
        "transit_vif": "Transit VIFs with BGP",
        "aws_site_to_site_vpn": "AWS Site-to-Site VPN attachment",
        "aws_transit_gateway": "AWS Transit Gateway",
        "tgw_route_table": "Transit Gateway route table",
        "tgw_vpc_attachment": "Transit Gateway VPC Attachment",
        "private_route_tables": "Private subnet route tables",
        "application_load_balancer": "Application Load Balancer",
        "elastic_load_balancing": "Elastic Load Balancing",
        "vpc": "Amazon VPC",
        "public_subnets": "Public Subnets",
        "private_subnets": "Private Subnets",
        "route53": "Amazon Route 53",
        "aws_secrets_manager": "AWS Secrets Manager",
        "aws_kms": "AWS KMS",
        "iam": "AWS IAM",
        "amazon_cloudwatch": "Amazon CloudWatch",
        "aws_backup": "AWS Backup",
        "aws_waf": "AWS WAF",
        "amazon_sns_sqs": "EventBridge / SNS + SQS",
        "aws_application_hosting_options": "Application hosting options",
        "amazon_managed_flink": "Amazon Managed Service for Apache Flink",
        "amazon_athena_glue_catalog": "Amazon Athena + AWS Glue Data Catalog",
        "aws_observability_stack": "CloudWatch / CloudTrail / OpenSearch",
        "aws_elastic_beanstalk": "AWS Elastic Beanstalk",
        "amazon_ec2": "Amazon EC2",
        "amazon_sns": "Amazon SNS",
        "amazon_sqs": "Amazon SQS",
        "amazon_eventbridge": "Amazon EventBridge",
        "aws_iot_core": "AWS IoT Core",
        "amazon_kinesis": "Amazon Kinesis Data Streams / Firehose",
        "aws_glue": "AWS Glue",
        "amazon_emr": "Amazon EMR",
        "amazon_redshift": "Amazon Redshift",
        "amazon_sagemaker_studio": "Amazon SageMaker Studio",
        "amazon_s3": "Amazon S3",
        "amazon_dynamodb": "Amazon DynamoDB",
    }
    return canonical_names.get(component_id, service_name)


def _component_id_for_mapping(mapping: ServiceMapping) -> str:
    if "app engine" in _normalize(mapping.source_service):
        return "aws_application_hosting_options"
    return _component_id_for_service(mapping.target_service)


def _canonical_service_name_for_mapping(mapping: ServiceMapping) -> str:
    if "app engine" in _normalize(mapping.source_service):
        return "Application hosting options"
    return _canonical_service_name(mapping.target_service)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def _architecture_text(source_architecture: SourceArchitecture) -> str:
    parts = [source_architecture.provider, source_architecture.summary]
    for component in source_architecture.components:
        parts.extend(
            [
                component.id,
                component.name,
                component.service_type or "",
                component.category or "",
                component.description or "",
            ]
        )
    return " ".join(parts).lower()


def _mentions(text: str, tokens: list[str]) -> bool:
    return any(token.lower() in text for token in tokens)


def _has_component(
    components: dict[str, ArchitectureComponent],
    component_id: str,
) -> bool:
    return component_id in components


def _has_any_component(
    components: dict[str, ArchitectureComponent],
    component_ids: list[str],
) -> bool:
    return any(component_id in components for component_id in component_ids)


def _component_ids_in_categories(
    components: dict[str, ArchitectureComponent],
    categories: set[str],
) -> list[str]:
    excluded = {
        "users",
        "on_premises_network",
        "customer_gateway",
        "vpc",
        "public_subnets",
        "private_subnets",
        "route53",
        "application_load_balancer",
        "elastic_load_balancing",
        "aws_waf",
        "aws_direct_connect",
        "ipsec_vpn_tunnels",
        "transit_vif",
        "aws_direct_connect_gateway",
        "aws_site_to_site_vpn",
        "aws_transit_gateway",
        "tgw_route_table",
        "tgw_vpc_attachment",
        "private_route_tables",
        "iam",
        "aws_secrets_manager",
        "aws_kms",
        "amazon_cloudwatch",
        "aws_backup",
    }
    return [
        component_id
        for component_id, component in components.items()
        if component_id not in excluded and component.category in categories
    ]


def _has_hybrid_connectivity(
    source_text: str,
    service_mappings: list[ServiceMapping],
    components: dict[str, ArchitectureComponent],
) -> bool:
    mapping_text = " ".join(
        f"{mapping.source_service} {mapping.target_service}" for mapping in service_mappings
    ).lower()
    combined = f"{source_text} {mapping_text}"
    return _mentions(
        combined,
        [
            "expressroute",
            "direct connect",
            "vpn gateway",
            "site-to-site vpn",
            "site to site vpn",
            "on-premises",
            "on premises",
            "gateway subnet",
            "virtual network gateway",
            "transit gateway",
        ],
    ) or _has_any_component(
        components,
        ["aws_direct_connect", "aws_site_to_site_vpn", "aws_transit_gateway"],
    )


def _summary_for_architecture(
    has_hybrid_connectivity: bool,
    has_public_workload: bool,
    has_data_platform: bool,
) -> str:
    if has_hybrid_connectivity and not has_public_workload:
        return (
            "Proposed AWS architecture focuses on hybrid connectivity: on-premises networking "
            "connects to AWS through redundant Direct Connect connections with Transit VIF/BGP "
            "and Site-to-Site VPN backup, routes through Transit Gateway, and reaches workloads "
            "through Transit Gateway route tables, VPC attachments, and private subnet route tables."
        )
    if has_hybrid_connectivity:
        return (
            "Proposed AWS architecture combines production application ingress with hybrid "
            "connectivity, VPC isolation, private subnet placement, centralized routing, IAM, "
            "CloudWatch, and managed data protection controls."
        )
    if has_data_platform:
        return (
            "Proposed AWS architecture is a production data-platform target with client or device entry, "
            "event ingestion, managed processing, durable data stores, IAM/KMS security controls, "
            "CloudWatch observability, and backup guardrails."
        )
    return (
        "Proposed AWS architecture uses VPC isolation, public/private subnet tiers, managed "
        "ingress, least-privilege IAM, centralized secrets/encryption, CloudWatch observability, "
        "and backup controls."
    )
