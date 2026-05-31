from app.schemas import ArchitectureComponent, ArchitectureRelationship, TargetArchitecture
from app.services.mermaid_generator import generate_mermaid_diagram


def test_generates_mermaid_graph_from_target_architecture():
    architecture = TargetArchitecture(
        provider="aws",
        summary="AWS target",
        components=[
            ArchitectureComponent(
                id="users",
                name="Users",
                provider="external",
                category="external",
                confidence=0.9,
            ),
            ArchitectureComponent(
                id="amazon_rds",
                name="Amazon RDS",
                provider="aws",
                category="database",
                confidence=0.9,
            ),
        ],
        relationships=[
            ArchitectureRelationship(
                source_id="users",
                target_id="amazon_rds",
                relationship_type="reads_writes",
            )
        ],
    )

    mermaid = generate_mermaid_diagram(architecture)

    assert mermaid.startswith("graph TD")
    assert 'users["Users"]' in mermaid
    assert 'amazon_rds[("Amazon RDS")]' in mermaid
    assert "users -->|reads writes| amazon_rds" in mermaid

