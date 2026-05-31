"""Mermaid architecture diagram generation."""

from __future__ import annotations

import re

from app.schemas import ArchitectureComponent, ArchitectureRelationship, TargetArchitecture


def generate_mermaid_diagram(target_architecture: TargetArchitecture) -> str:
    """Generate a Mermaid graph from the target architecture model."""

    lines = ["graph TD"]
    component_ids = {component.id for component in target_architecture.components}

    for component in target_architecture.components:
        lines.append(f"    {safe_node_id(component.id)}{_shape_for_component(component)}")

    for relationship in target_architecture.relationships:
        if (
            relationship.source_id not in component_ids
            or relationship.target_id not in component_ids
        ):
            continue
        lines.append(_relationship_line(relationship))

    return "\n".join(lines)


def safe_node_id(value: str) -> str:
    node_id = re.sub(r"[^a-zA-Z0-9_]", "_", value)
    if not node_id:
        node_id = "node"
    if node_id[0].isdigit():
        node_id = f"n_{node_id}"
    return node_id


def safe_label(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ").strip()


def _shape_for_component(component: ArchitectureComponent) -> str:
    label = safe_label(component.name)
    if component.category == "database":
        return f'[("{label}")]'
    if component.category == "storage":
        return f'[/"{label}"/]'
    if component.category == "external":
        return f'["{label}"]'
    return f'["{label}"]'


def _relationship_line(relationship: ArchitectureRelationship) -> str:
    source_id = safe_node_id(relationship.source_id)
    target_id = safe_node_id(relationship.target_id)
    label = safe_label(relationship.relationship_type.replace("_", " "))
    if label:
        return f"    {source_id} -->|{label}| {target_id}"
    return f"    {source_id} --> {target_id}"

