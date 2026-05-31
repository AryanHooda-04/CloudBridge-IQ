from app.schemas import ArchitectureComponent, ArchitectureRelationship, TargetArchitecture
from app.services.aws_diagram_generator import generate_aws_diagram_png


def test_generate_aws_diagram_png_returns_png_bytes():
    architecture = TargetArchitecture(
        provider="aws",
        summary="Test AWS architecture.",
        components=[
            ArchitectureComponent(
                id="route53",
                name="Amazon Route 53",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="alb",
                name="Application Load Balancer",
                category="networking",
                confidence=0.9,
            ),
        ],
        relationships=[
            ArchitectureRelationship(
                source_id="route53",
                target_id="alb",
                relationship_type="routes_to",
            )
        ],
    )

    png_bytes = generate_aws_diagram_png(architecture)

    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1000


def test_generate_azure_data_platform_diagram_png_returns_png_bytes():
    architecture = TargetArchitecture(
        provider="azure",
        summary="Azure data platform target.",
        components=[
            ArchitectureComponent(
                id="iot_devices",
                name="IoT Devices",
                category="external",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="azure_iot_hub",
                name="Azure IoT Hub",
                category="iot",
                confidence=0.84,
            ),
            ArchitectureComponent(
                id="azure_event_hubs",
                name="Azure Event Hubs",
                category="messaging",
                confidence=0.86,
            ),
            ArchitectureComponent(
                id="azure_stream_analytics",
                name="Azure Stream Analytics",
                category="analytics",
                confidence=0.84,
            ),
            ArchitectureComponent(
                id="adls_gen2",
                name="Azure Data Lake Storage Gen2",
                category="storage",
                confidence=0.88,
            ),
            ArchitectureComponent(
                id="azure_synapse",
                name="Synapse Analytics or Microsoft Fabric",
                category="database",
                confidence=0.84,
            ),
            ArchitectureComponent(
                id="consumers_bi_apis",
                name="Consumers / BI / APIs",
                category="client",
                confidence=0.8,
            ),
            ArchitectureComponent(
                id="azure_monitor",
                name="Azure Monitor + Log Analytics + Application Insights",
                category="observability",
                confidence=0.86,
            ),
        ],
        relationships=[
            ArchitectureRelationship(
                source_id="azure_iot_hub",
                target_id="azure_event_hubs",
                relationship_type="routes_events",
            )
        ],
    )

    png_bytes = generate_aws_diagram_png(architecture)

    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1000


def test_generate_gcp_hybrid_connectivity_diagram_png_returns_png_bytes():
    architecture = TargetArchitecture(
        provider="gcp",
        summary="GCP hybrid connectivity target.",
        components=[
            ArchitectureComponent(
                id="on_premises_network",
                name="On-premises network",
                category="external",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="customer_edge_routers",
                name="Customer edge routers (HA)",
                category="networking",
                confidence=0.86,
            ),
            ArchitectureComponent(
                id="dedicated_interconnect",
                name="Dedicated Interconnect",
                category="networking",
                confidence=0.84,
            ),
            ArchitectureComponent(
                id="vlan_attachments",
                name="VLAN attachments",
                category="networking",
                confidence=0.86,
            ),
            ArchitectureComponent(
                id="cloud_router",
                name="Cloud Router with BGP",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="ha_vpn_gateway",
                name="HA VPN gateway",
                category="networking",
                confidence=0.84,
            ),
            ArchitectureComponent(
                id="shared_vpc",
                name="Shared VPC / VPC Network",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="private_service_connect",
                name="Private Service Connect",
                category="networking",
                confidence=0.82,
            ),
        ],
        relationships=[],
    )

    png_bytes = generate_aws_diagram_png(architecture)

    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1000


def test_generate_azure_graphrag_diagram_png_returns_png_bytes():
    architecture = TargetArchitecture(
        provider="azure",
        summary="Azure GraphRAG target.",
        components=[
            ArchitectureComponent(id="data_sources", name="Redshift / S3 / MSK / Glue inputs", category="external", confidence=0.88),
            ArchitectureComponent(id="adls_gen2", name="Azure Data Lake Storage Gen2", category="storage", confidence=0.88),
            ArchitectureComponent(id="azure_event_hubs_kafka", name="Azure Event Hubs with Kafka support", category="messaging", confidence=0.84),
            ArchitectureComponent(id="azure_openai_ai_foundry", name="Azure OpenAI / Azure AI Foundry", category="ml", confidence=0.86),
            ArchitectureComponent(id="neo4j_auradb", name="Neo4j AuraDB on Azure / Neo4j on AKS or VMs", category="database", confidence=0.88),
            ArchitectureComponent(id="neo4j_graph_data_science", name="Neo4j Graph Data Science", category="analytics", confidence=0.8),
            ArchitectureComponent(id="neo4j_graphrag_retriever", name="Neo4j GraphRAG retriever / Neo4j driver", category="application", confidence=0.86),
            ArchitectureComponent(id="graphrag_api", name="GraphRAG API + Azure OpenAI orchestration", category="application", confidence=0.84),
            ArchitectureComponent(id="azure_app_hosting", name="App Service / Container Apps", category="compute", confidence=0.8),
            ArchitectureComponent(id="azure_monitor", name="Azure Monitor + Log Analytics + Application Insights", category="observability", confidence=0.86),
        ],
        relationships=[],
    )

    png_bytes = generate_aws_diagram_png(architecture)

    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1000


def test_generate_gcp_graphrag_diagram_png_returns_png_bytes():
    architecture = TargetArchitecture(
        provider="gcp",
        summary="Google Cloud GraphRAG target.",
        components=[
            ArchitectureComponent(id="data_sources", name="Redshift / S3 / MSK / Glue inputs", category="external", confidence=0.88),
            ArchitectureComponent(id="bigquery", name="BigQuery - Redshift replacement", category="database", confidence=0.86),
            ArchitectureComponent(id="cloud_storage", name="Cloud Storage - S3 landing zone", category="storage", confidence=0.88),
            ArchitectureComponent(id="managed_kafka", name="Managed Service for Apache Kafka", category="messaging", confidence=0.82),
            ArchitectureComponent(id="vertex_ai", name="Vertex AI", category="ml", confidence=0.84),
            ArchitectureComponent(id="vertex_ai_gemini", name="Vertex AI / Gemini", category="ml", confidence=0.86),
            ArchitectureComponent(id="neo4j_auradb_gcp", name="Neo4j AuraDB on Google Cloud", category="database", confidence=0.88),
            ArchitectureComponent(id="neo4j_graph_data_science", name="Neo4j Graph Data Science / AuraDS", category="analytics", confidence=0.8),
            ArchitectureComponent(id="neo4j_graphrag_retriever", name="Neo4j GraphRAG retriever / Cypher retrieval", category="application", confidence=0.86),
            ArchitectureComponent(id="graphrag_api", name="GraphRAG API + Vertex AI orchestration", category="application", confidence=0.84),
            ArchitectureComponent(id="cloud_run_services", name="Cloud Run services", category="compute", confidence=0.8),
            ArchitectureComponent(id="cloud_monitoring_logging", name="Cloud Monitoring + Cloud Logging", category="observability", confidence=0.86),
        ],
        relationships=[],
    )

    png_bytes = generate_aws_diagram_png(architecture)

    assert png_bytes.startswith(b"\x89PNG")
    assert len(png_bytes) > 1000
