from app.schemas import ArchitectureComponent, ServiceMapping, SourceArchitecture
from app.services.architecture_generator import generate_target_architecture
from app.services.cloud_mapping import map_services


def test_hybrid_network_architecture_avoids_fake_application_path():
    source = SourceArchitecture(
        provider="azure",
        summary="On-premises network connects to Azure VNet through ExpressRoute and VPN Gateway.",
        components=[
            ArchitectureComponent(
                id="er",
                name="ExpressRoute circuit",
                service_type="ExpressRoute circuit",
                category="networking",
                confidence=0.95,
            ),
            ArchitectureComponent(
                id="vpn",
                name="VPN gateway",
                service_type="VPN gateway",
                category="networking",
                confidence=0.95,
            ),
        ],
        relationships=[],
    )
    mappings = [
        ServiceMapping(
            source_service="Azure ExpressRoute Circuit",
            target_service="AWS Direct Connect",
            reasoning="Private connectivity.",
            confidence=0.86,
        ),
        ServiceMapping(
            source_service="Azure VPN Gateway",
            target_service="AWS Site-to-Site VPN",
            reasoning="Encrypted backup path.",
            confidence=0.86,
        ),
    ]

    target = generate_target_architecture(source, mappings)
    component_ids = {component.id for component in target.components}
    relationship_pairs = {
        (relationship.source_id, relationship.target_id)
        for relationship in target.relationships
    }

    assert "aws_direct_connect" in component_ids
    assert "ipsec_vpn_tunnels" in component_ids
    assert "transit_vif" in component_ids
    assert "aws_direct_connect_gateway" in component_ids
    assert "aws_site_to_site_vpn" in component_ids
    assert "aws_transit_gateway" in component_ids
    assert "tgw_route_table" in component_ids
    assert "tgw_vpc_attachment" in component_ids
    assert "private_route_tables" in component_ids
    assert "route53" not in component_ids
    assert "application_load_balancer" not in component_ids
    assert any(
        component.name == "Redundant Direct Connect connections"
        for component in target.components
    )
    assert any(
        component.name == "AWS Site-to-Site VPN attachment"
        for component in target.components
    )
    assert ("aws_direct_connect", "transit_vif") in relationship_pairs
    assert ("transit_vif", "aws_direct_connect_gateway") in relationship_pairs
    assert ("customer_gateway", "ipsec_vpn_tunnels") in relationship_pairs
    assert ("ipsec_vpn_tunnels", "aws_site_to_site_vpn") in relationship_pairs
    assert ("aws_site_to_site_vpn", "aws_transit_gateway") in relationship_pairs
    assert ("aws_transit_gateway", "tgw_route_table") in relationship_pairs
    assert ("tgw_route_table", "tgw_vpc_attachment") in relationship_pairs
    assert ("tgw_vpc_attachment", "private_route_tables") in relationship_pairs
    assert ("private_route_tables", "private_subnets") in relationship_pairs
    assert any("BGP" in note for note in target.design_notes)
    assert any("route table" in note.lower() for note in target.design_notes)


def test_gcp_data_platform_target_adds_iot_streaming_and_query_options():
    source = SourceArchitecture(
        provider="Google Cloud",
        summary=(
            "IoT devices publish telemetry through Pub/Sub and Dataflow into Cloud Storage, "
            "BigQuery, App Engine, and Logging."
        ),
        components=[
            ArchitectureComponent(
                id="devices",
                name="IoT Devices",
                service_type="IoT Devices",
                category="external",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="pubsub",
                name="Pub/Sub",
                provider="gcp",
                service_type="Pub/Sub",
                category="messaging",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="dataflow",
                name="Dataflow",
                provider="gcp",
                service_type="Dataflow",
                category="analytics",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="storage",
                name="Cloud Storage",
                provider="gcp",
                service_type="Cloud Storage",
                category="storage",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="bigquery",
                name="BigQuery",
                provider="gcp",
                service_type="BigQuery",
                category="analytics",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="appengine",
                name="App Engine",
                provider="gcp",
                service_type="App Engine",
                category="compute",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="logging",
                name="Logging",
                provider="gcp",
                service_type="Logging",
                category="observability",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="aws"))
    component_ids = {component.id for component in target.components}
    component_names = {component.name for component in target.components}

    assert "aws_iot_core" in component_ids
    assert "amazon_kinesis" in component_ids
    assert "amazon_managed_flink" in component_ids
    assert "amazon_athena_glue_catalog" in component_ids
    assert "aws_application_hosting_options" in component_ids
    assert "aws_observability_stack" in component_ids
    assert "EventBridge / SNS + SQS" in component_names
    assert "Application hosting options" in component_names
    assert "data-platform" in target.summary or "data-platform" in " ".join(target.design_notes).lower()


def test_non_aws_target_gets_provider_native_foundation():
    source = SourceArchitecture(
        provider="azure",
        summary="Azure App Service backed by Azure SQL Database.",
        components=[
            ArchitectureComponent(
                id="app",
                name="Azure App Service",
                provider="azure",
                service_type="Azure App Service",
                category="compute",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="sql",
                name="Azure SQL Database",
                provider="azure",
                service_type="Azure SQL Database",
                category="database",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="gcp"), target_provider="gcp")
    component_ids = {component.id for component in target.components}
    component_names = {component.name for component in target.components}
    relationship_pairs = {(relationship.source_id, relationship.target_id) for relationship in target.relationships}

    assert target.provider == "gcp"
    assert "gcp_vpc_network" in component_ids
    assert "gcp_private_subnets" in component_ids
    assert "cloud_iam" in component_ids
    assert "cloud_monitoring_logging" in component_ids
    assert "App Engine" in component_names
    assert "Cloud SQL" in component_names
    assert ("cloud_load_balancing", "app_engine") in relationship_pairs


def test_gcp_data_platform_to_azure_preserves_ingestion_processing_data_flow():
    source = SourceArchitecture(
        provider="gcp",
        summary=(
            "IoT devices and standard devices publish through Pub/Sub. Dataflow processes events into "
            "Cloud Storage, Datastore, BigQuery, Dataproc, Datalab, App Engine, Compute Engine, Monitoring, and Logging."
        ),
        components=[
            ArchitectureComponent(
                id="devices",
                name="IoT Devices",
                provider=None,
                service_type="IoT Devices",
                category="external",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="pubsub",
                name="Pub/Sub",
                provider="gcp",
                service_type="Pub/Sub",
                category="messaging",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="dataflow",
                name="Dataflow",
                provider="gcp",
                service_type="Dataflow",
                category="analytics",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="storage",
                name="Cloud Storage",
                provider="gcp",
                service_type="Cloud Storage",
                category="storage",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="datastore",
                name="Datastore",
                provider="gcp",
                service_type="Datastore",
                category="database",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="bigquery",
                name="BigQuery",
                provider="gcp",
                service_type="BigQuery",
                category="analytics",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="appengine",
                name="App Engine",
                provider="gcp",
                service_type="App Engine",
                category="compute",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="azure"), target_provider="azure")
    component_ids = {component.id for component in target.components}
    relationship_pairs = {(relationship.source_id, relationship.target_id) for relationship in target.relationships}

    assert target.provider == "azure"
    assert "azure_iot_hub" in component_ids
    assert "azure_event_hubs" in component_ids
    assert "azure_stream_analytics" in component_ids
    assert "azure_databricks" in component_ids
    assert "adls_gen2" in component_ids
    assert "azure_synapse" in component_ids
    assert "azure_cosmos_db" in component_ids
    assert "azure_app_hosting" in component_ids
    assert "consumers_bi_apis" in component_ids
    assert "azure_monitor" in component_ids
    assert "private_endpoints" in component_ids
    assert ("iot_devices", "azure_iot_hub") in relationship_pairs
    assert ("azure_iot_hub", "azure_event_hubs") in relationship_pairs
    assert ("azure_event_hubs", "azure_stream_analytics") in relationship_pairs
    assert ("azure_stream_analytics", "adls_gen2") in relationship_pairs
    assert ("adls_gen2", "azure_synapse") in relationship_pairs
    assert ("azure_synapse", "consumers_bi_apis") in relationship_pairs
    assert any("IoT Hub" in note for note in target.design_notes)
    assert any("Service Bus" in note for note in target.design_notes)


def test_azure_hybrid_connectivity_to_gcp_preserves_interconnect_vpn_flow():
    source = SourceArchitecture(
        provider="azure",
        summary=(
            "On-premises network connects to Azure Virtual Network through an ExpressRoute circuit, "
            "ExpressRoute gateway, gateway subnet, and VPN gateway fallback."
        ),
        components=[
            ArchitectureComponent(
                id="onprem",
                name="On-premises network",
                service_type="On-premises network",
                category="networking",
                confidence=0.95,
            ),
            ArchitectureComponent(
                id="er",
                name="ExpressRoute circuit",
                provider="azure",
                service_type="ExpressRoute circuit",
                category="networking",
                confidence=0.95,
            ),
            ArchitectureComponent(
                id="ergw",
                name="ExpressRoute gateway",
                provider="azure",
                service_type="ExpressRoute gateway",
                category="networking",
                confidence=0.95,
            ),
            ArchitectureComponent(
                id="vpn",
                name="VPN gateway",
                provider="azure",
                service_type="VPN gateway",
                category="networking",
                confidence=0.95,
            ),
            ArchitectureComponent(
                id="subnet",
                name="Gateway subnet",
                provider="azure",
                service_type="Gateway subnet",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="vnet",
                name="Azure Virtual Network",
                provider="azure",
                service_type="Azure Virtual Network",
                category="networking",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="gcp"), target_provider="gcp")
    component_ids = {component.id for component in target.components}
    relationship_pairs = {(relationship.source_id, relationship.target_id) for relationship in target.relationships}

    assert target.provider == "gcp"
    assert {
        "on_premises_network",
        "customer_edge_routers",
        "dedicated_interconnect",
        "partner_interconnect",
        "vlan_attachments",
        "cloud_router",
        "ha_vpn_tunnels",
        "ha_vpn_gateway",
        "shared_vpc",
        "regional_private_subnets",
        "public_lb_tier",
        "cloud_nat",
        "private_service_connect",
        "private_google_access",
        "firewall_policies",
        "vpc_service_controls",
    }.issubset(component_ids)
    assert ("dedicated_interconnect", "vlan_attachments") in relationship_pairs
    assert ("vlan_attachments", "cloud_router") in relationship_pairs
    assert ("ha_vpn_tunnels", "ha_vpn_gateway") in relationship_pairs
    assert ("ha_vpn_gateway", "cloud_router") in relationship_pairs
    assert ("cloud_router", "shared_vpc") in relationship_pairs
    assert ("shared_vpc", "regional_private_subnets") in relationship_pairs
    assert any("Cloud Router" in note for note in target.design_notes)
    assert any("VLAN attachments" in note for note in target.design_notes)
    assert any("HA VPN" in note for note in target.design_notes)
    assert any("Private Service Connect" in note for note in target.design_notes)


def test_aws_neo4j_graphrag_to_azure_uses_graphrag_architecture_not_iot_template():
    source = SourceArchitecture(
        provider="aws",
        summary=(
            "AWS Neo4j knowledge graph and GraphRAG architecture with Amazon Redshift, Amazon S3, "
            "Amazon MSK, AWS Glue, Amazon SageMaker, Amazon Bedrock, Neo4j driver, Neo4j Bloom, "
            "Graph Data Science, AWS Lambda, Amazon EC2, and Amazon EKS."
        ),
        components=[
            ArchitectureComponent(id="redshift", name="Amazon Redshift", provider="aws", service_type="Amazon Redshift", category="database", confidence=0.9),
            ArchitectureComponent(id="s3", name="Amazon S3", provider="aws", service_type="Amazon S3", category="storage", confidence=0.9),
            ArchitectureComponent(id="msk", name="Amazon MSK", provider="aws", service_type="Amazon MSK", category="messaging", confidence=0.9),
            ArchitectureComponent(id="glue", name="AWS Glue", provider="aws", service_type="AWS Glue", category="analytics", confidence=0.9),
            ArchitectureComponent(id="sagemaker", name="Amazon SageMaker", provider="aws", service_type="Amazon SageMaker", category="ml", confidence=0.9),
            ArchitectureComponent(id="bedrock", name="Amazon Bedrock", provider="aws", service_type="Amazon Bedrock", category="ml", confidence=0.9),
            ArchitectureComponent(id="neo4j", name="Graph Database", provider=None, service_type="Neo4j", category="database", confidence=0.9),
            ArchitectureComponent(id="driver", name="Neo4j driver", provider=None, service_type="Neo4j driver", category="application", confidence=0.9),
            ArchitectureComponent(id="bloom", name="Neo4j Bloom", provider=None, service_type="Neo4j Bloom", category="application", confidence=0.86),
            ArchitectureComponent(id="gds", name="Neo4j Graph Data Science", provider=None, service_type="Neo4j Graph Data Science", category="analytics", confidence=0.86),
            ArchitectureComponent(id="lambda", name="AWS Lambda", provider="aws", service_type="AWS Lambda", category="compute", confidence=0.9),
            ArchitectureComponent(id="ec2", name="Amazon EC2", provider="aws", service_type="Amazon EC2", category="compute", confidence=0.9),
            ArchitectureComponent(id="eks", name="Amazon EKS", provider="aws", service_type="Amazon EKS", category="compute", confidence=0.9),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="azure"), target_provider="azure")
    component_ids = {component.id for component in target.components}
    component_names = {component.name for component in target.components}
    relationship_pairs = {(relationship.source_id, relationship.target_id) for relationship in target.relationships}

    assert target.provider == "azure"
    assert "azure_iot_hub" not in component_ids
    assert "Redshift / S3 / MSK / Glue inputs" in component_names
    assert "GraphRAG API + Azure OpenAI orchestration" in component_names
    assert "neo4j_auradb" in component_ids
    assert "neo4j_bloom" in component_ids
    assert "neo4j_graph_data_science" in component_ids
    assert "neo4j_graphrag_retriever" in component_ids
    assert "azure_openai_ai_foundry" in component_ids
    assert "azure_ai_search_optional" in component_ids
    assert "azure_event_hubs_kafka" in component_ids
    assert "azure_kubernetes_service" in component_ids
    assert "azure_virtual_machines" in component_ids
    assert ("neo4j_cypher_ingestion", "neo4j_auradb") in relationship_pairs
    assert ("neo4j_auradb", "neo4j_graphrag_retriever") in relationship_pairs
    assert ("azure_openai_ai_foundry", "graphrag_api") in relationship_pairs
    assert any("Cosmos DB" in note for note in target.design_notes)
    assert any("IoT Hub" in note for note in target.design_notes)
    assert any("Kafka client compatibility" in note for note in target.design_notes)


def test_aws_neo4j_graphrag_to_gcp_uses_graphrag_architecture_not_inventory():
    source = SourceArchitecture(
        provider="aws",
        summary=(
            "AWS Neo4j knowledge graph and GraphRAG architecture with Amazon Redshift, Amazon S3, "
            "Amazon MSK, AWS Glue, Amazon SageMaker, Amazon Bedrock, Neo4j driver, Neo4j Bloom, "
            "Graph Data Science, AWS Lambda, Amazon EC2, and Amazon EKS."
        ),
        components=[
            ArchitectureComponent(id="redshift", name="Amazon Redshift", provider="aws", service_type="Amazon Redshift", category="database", confidence=0.9),
            ArchitectureComponent(id="s3", name="Amazon S3", provider="aws", service_type="Amazon S3", category="storage", confidence=0.9),
            ArchitectureComponent(id="msk", name="Amazon MSK", provider="aws", service_type="Amazon MSK", category="messaging", confidence=0.9),
            ArchitectureComponent(id="glue", name="AWS Glue", provider="aws", service_type="AWS Glue", category="analytics", confidence=0.9),
            ArchitectureComponent(id="sagemaker", name="Amazon SageMaker", provider="aws", service_type="Amazon SageMaker", category="ml", confidence=0.9),
            ArchitectureComponent(id="bedrock", name="Amazon Bedrock", provider="aws", service_type="Amazon Bedrock", category="ml", confidence=0.9),
            ArchitectureComponent(id="neo4j", name="Graph Database", provider=None, service_type="Neo4j", category="database", confidence=0.9),
            ArchitectureComponent(id="driver", name="Neo4j driver", provider=None, service_type="Neo4j driver", category="application", confidence=0.9),
            ArchitectureComponent(id="bloom", name="Neo4j Bloom", provider=None, service_type="Neo4j Bloom", category="application", confidence=0.86),
            ArchitectureComponent(id="gds", name="Neo4j Graph Data Science", provider=None, service_type="Neo4j Graph Data Science", category="analytics", confidence=0.86),
            ArchitectureComponent(id="lambda", name="AWS Lambda", provider="aws", service_type="AWS Lambda", category="compute", confidence=0.9),
            ArchitectureComponent(id="ec2", name="Amazon EC2", provider="aws", service_type="Amazon EC2", category="compute", confidence=0.9),
            ArchitectureComponent(id="eks", name="Amazon EKS", provider="aws", service_type="Amazon EKS", category="compute", confidence=0.9),
        ],
        relationships=[],
    )

    target = generate_target_architecture(source, map_services(source, target_provider="gcp"), target_provider="gcp")
    component_ids = {component.id for component in target.components}
    component_names = {component.name for component in target.components}
    relationship_pairs = {(relationship.source_id, relationship.target_id) for relationship in target.relationships}

    assert target.provider == "gcp"
    assert "cloud_sql_auth_proxy" not in component_ids
    assert "Redshift / S3 / MSK / Glue inputs" in component_names
    assert "GraphRAG API + Vertex AI orchestration" in component_names
    assert {
        "bigquery",
        "cloud_storage",
        "managed_kafka",
        "cloud_data_fusion_dataflow",
        "vertex_ai",
        "vertex_ai_gemini",
        "neo4j_auradb_gcp",
        "neo4j_bloom",
        "neo4j_graph_data_science",
        "neo4j_graphrag_retriever",
        "vertex_ai_vector_search_optional",
        "cloud_run_functions",
        "compute_engine",
        "google_kubernetes_engine",
        "private_service_connect",
        "vpc_service_controls",
    }.issubset(component_ids)
    assert ("neo4j_cypher_ingestion", "neo4j_auradb_gcp") in relationship_pairs
    assert ("neo4j_auradb_gcp", "neo4j_graphrag_retriever") in relationship_pairs
    assert ("vertex_ai_gemini", "graphrag_api") in relationship_pairs
    assert any("Cloud SQL Auth Proxy" in note for note in target.design_notes)
    assert any("Kafka client compatibility" in note for note in target.design_notes)
    assert any("Pub/Sub" in note for note in target.design_notes)
