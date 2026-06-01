# CloudBridge IQ Sample Architecture Diagrams

Use these PNGs to exercise different assessment paths. Upload one diagram in the UI, then set the suggested source/target route and intent.

| File | Best Route | Pattern To Expect | Suggested Intent |
|---|---|---|---|
| `01-azure-enterprise-webapp.png` | Azure to AWS | Web application modernization | `We are migrating this Azure web application to AWS.` |
| `02-gcp-iot-data-platform.png` | GCP to Azure or GCP to AWS | IoT data platform | `We are migrating this GCP IoT data platform to Azure.` |
| `03-aws-neo4j-graphrag.png` | AWS to Azure or AWS to GCP | GraphRAG / knowledge graph | `We are migrating this AWS Neo4j GraphRAG workload to Azure.` |
| `04-azure-hybrid-connectivity.png` | Azure to AWS or Azure to GCP | Hybrid connectivity | `We are migrating Azure ExpressRoute and VPN connectivity to AWS.` |
| `05-aws-event-microservices.png` | AWS to Azure or AWS to GCP | Event-driven microservices | `We are migrating this AWS event-driven microservices architecture to Azure.` |

Useful goal presets:

- Web app: `modernization, reduce operations, improve availability`
- IoT/data: `analytics modernization, improve scalability, reduce operations`
- GraphRAG: `AI modernization, preserve graph database capabilities, improve governance`
- Hybrid connectivity: `improve DR, network resiliency, data center exit`
- Microservices: `modernization, event-driven redesign, operational consistency`

If the output still looks repetitive, set **Architecture options** explicitly before running the assessment. The model uses the visible diagram, migration intent, goals, and selected architecture pattern together.
