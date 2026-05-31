from app.schemas import ArchitectureComponent, SourceArchitecture
from app.services.cloud_mapping import map_services


def test_maps_known_azure_service_to_aws():
    source = SourceArchitecture(
        provider="Microsoft Azure",
        summary="Azure web app with SQL database.",
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

    mappings = map_services(source, target_provider="aws", goals=["managed application hosting"])

    assert [mapping.source_service for mapping in mappings] == [
        "Azure App Service",
        "Azure SQL Database",
    ]
    assert mappings[0].target_service == "AWS Elastic Beanstalk"
    assert mappings[1].target_service == "Amazon RDS"
    assert mappings[0].alternatives


def test_unknown_service_uses_low_confidence_fallback():
    source = SourceArchitecture(
        provider="azure",
        summary="Custom platform service.",
        components=[
            ArchitectureComponent(
                id="custom",
                name="Custom Azure Appliance",
                provider="azure",
                service_type="Custom Azure Appliance",
                category="application",
                confidence=0.4,
            )
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="aws")

    assert len(mappings) == 1
    assert "AWS managed equivalent" in mappings[0].target_service
    assert mappings[0].confidence == 0.3


def test_skips_non_cloud_artifacts_and_maps_hybrid_connectivity():
    source = SourceArchitecture(
        provider="azure",
        summary="Hybrid Azure network with ExpressRoute and VPN.",
        components=[
            ArchitectureComponent(
                id="onprem",
                name="On-premises network",
                provider=None,
                service_type="On-premises network",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="routers",
                name="Local edge routers",
                provider=None,
                service_type="Local edge routers",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="er",
                name="ExpressRoute circuit",
                provider="azure",
                service_type="ExpressRoute circuit",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="vpn",
                name="VPN gateway",
                provider="azure",
                service_type="VPN gateway",
                category="networking",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="aws")

    assert [mapping.source_service for mapping in mappings] == [
        "Azure ExpressRoute Circuit",
        "Azure VPN Gateway",
    ]
    assert [mapping.target_service for mapping in mappings] == [
        "AWS Direct Connect",
        "AWS Site-to-Site VPN",
    ]


def test_maps_known_gcp_data_platform_services_to_aws():
    source = SourceArchitecture(
        provider="Google Cloud",
        summary="GCP data platform with Pub/Sub, Dataflow, Cloud Storage, BigQuery, Dataproc, App Engine, and Logging.",
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
                id="bigquery",
                name="BigQuery",
                provider="gcp",
                service_type="BigQuery",
                category="analytics",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="dataproc",
                name="Dataproc",
                provider="gcp",
                service_type="Dataproc",
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

    mappings = map_services(source, target_provider="aws")

    assert [mapping.source_service for mapping in mappings] == [
        "Pub/Sub",
        "Dataflow",
        "Cloud Storage",
        "BigQuery",
        "Dataproc",
        "App Engine",
        "Logging",
    ]
    assert [mapping.target_service for mapping in mappings] == [
        "Amazon SNS + Amazon SQS",
        "AWS Glue",
        "Amazon S3",
        "Amazon Redshift",
        "Amazon EMR",
        "AWS Application Hosting Options",
        "Amazon CloudWatch + AWS CloudTrail + Amazon OpenSearch Service",
    ]


def test_maps_azure_services_to_gcp():
    source = SourceArchitecture(
        provider="azure",
        summary="Azure App Service backed by Blob Storage and SQL.",
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
                id="blob",
                name="Azure Blob Storage",
                provider="azure",
                service_type="Azure Blob Storage",
                category="storage",
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

    mappings = map_services(source, target_provider="gcp", goals=["managed"])

    assert [mapping.target_service for mapping in mappings] == [
        "App Engine",
        "Cloud Storage",
        "Cloud SQL",
    ]


def test_maps_azure_hybrid_connectivity_services_to_gcp():
    source = SourceArchitecture(
        provider="azure",
        summary="Azure ExpressRoute private connectivity with VPN gateway fallback.",
        components=[
            ArchitectureComponent(
                id="er",
                name="ExpressRoute circuit",
                provider="azure",
                service_type="ExpressRoute circuit",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="ergw",
                name="ExpressRoute gateway",
                provider="azure",
                service_type="ExpressRoute gateway",
                category="networking",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="vpn",
                name="VPN gateway",
                provider="azure",
                service_type="VPN gateway",
                category="networking",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="gcp")

    assert [mapping.target_service for mapping in mappings] == [
        "Dedicated Interconnect",
        "Cloud Router + VLAN attachments",
        "HA VPN",
    ]


def test_maps_gcp_services_to_azure():
    source = SourceArchitecture(
        provider="gcp",
        summary="GCP App Engine with Pub/Sub and BigQuery.",
        components=[
            ArchitectureComponent(
                id="app",
                name="App Engine",
                provider="gcp",
                service_type="App Engine",
                category="compute",
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
                id="bq",
                name="BigQuery",
                provider="gcp",
                service_type="BigQuery",
                category="analytics",
                confidence=0.9,
            ),
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="azure")

    assert [mapping.target_service for mapping in mappings] == [
        "Azure App Service",
        "Azure Event Hubs",
        "Azure Synapse Analytics",
    ]


def test_maps_aws_graphrag_services_to_azure():
    source = SourceArchitecture(
        provider="aws",
        summary="AWS Neo4j GraphRAG architecture.",
        components=[
            ArchitectureComponent(id="s3", name="Amazon S3", provider="aws", service_type="Amazon S3", category="storage", confidence=0.9),
            ArchitectureComponent(id="msk", name="Amazon MSK", provider="aws", service_type="Amazon MSK", category="messaging", confidence=0.9),
            ArchitectureComponent(id="glue", name="AWS Glue", provider="aws", service_type="AWS Glue", category="analytics", confidence=0.9),
            ArchitectureComponent(id="sagemaker", name="Amazon SageMaker", provider="aws", service_type="Amazon SageMaker", category="ml", confidence=0.9),
            ArchitectureComponent(id="bedrock", name="Amazon Bedrock", provider="aws", service_type="Amazon Bedrock", category="ml", confidence=0.9),
            ArchitectureComponent(id="neo4j", name="Neo4j", provider=None, service_type="Neo4j", category="database", confidence=0.9),
            ArchitectureComponent(id="driver", name="Neo4j driver", provider=None, service_type="Neo4j driver", category="application", confidence=0.9),
            ArchitectureComponent(id="eks", name="Amazon EKS", provider="aws", service_type="Amazon EKS", category="compute", confidence=0.9),
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="azure")

    assert [mapping.target_service for mapping in mappings] == [
        "Azure Data Lake Storage Gen2",
        "Azure Event Hubs with Kafka support",
        "Azure Data Factory / Fabric Data Factory",
        "Azure Machine Learning",
        "Azure OpenAI / Azure AI Foundry",
        "Neo4j AuraDB on Azure",
        "Neo4j driver / Cypher ingestion service",
        "Azure Kubernetes Service",
    ]


def test_maps_aws_graphrag_services_to_gcp():
    source = SourceArchitecture(
        provider="aws",
        summary="AWS Neo4j GraphRAG architecture.",
        components=[
            ArchitectureComponent(id="s3", name="Amazon S3", provider="aws", service_type="Amazon S3", category="storage", confidence=0.9),
            ArchitectureComponent(id="msk", name="Amazon MSK", provider="aws", service_type="Amazon MSK", category="messaging", confidence=0.9),
            ArchitectureComponent(id="glue", name="AWS Glue", provider="aws", service_type="AWS Glue", category="analytics", confidence=0.9),
            ArchitectureComponent(id="sagemaker", name="Amazon SageMaker", provider="aws", service_type="Amazon SageMaker", category="ml", confidence=0.9),
            ArchitectureComponent(id="bedrock", name="Amazon Bedrock", provider="aws", service_type="Amazon Bedrock", category="ml", confidence=0.9),
            ArchitectureComponent(id="neo4j", name="Neo4j", provider=None, service_type="Neo4j", category="database", confidence=0.9),
            ArchitectureComponent(id="driver", name="Neo4j driver", provider=None, service_type="Neo4j driver", category="application", confidence=0.9),
            ArchitectureComponent(id="eks", name="Amazon EKS", provider="aws", service_type="Amazon EKS", category="compute", confidence=0.9),
        ],
        relationships=[],
    )

    mappings = map_services(source, target_provider="gcp")

    assert [mapping.target_service for mapping in mappings] == [
        "Cloud Storage",
        "Managed Service for Apache Kafka",
        "Cloud Data Fusion",
        "Vertex AI",
        "Vertex AI / Gemini",
        "Neo4j AuraDB on Google Cloud",
        "Neo4j driver / Cypher ingestion service",
        "Google Kubernetes Engine",
    ]
