"""Optional image-based AWS architecture rendering with diagrams + Graphviz."""

from __future__ import annotations

import math
import tempfile
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.schemas import ArchitectureComponent, TargetArchitecture


def generate_aws_diagram_png(target_architecture: TargetArchitecture) -> bytes:
    """Render a target architecture to PNG using the diagrams package."""

    if _provider_key(target_architecture.provider) == "azure" and _is_azure_graphrag_architecture(
        target_architecture
    ):
        return _generate_azure_graphrag_png(target_architecture)
    if _provider_key(target_architecture.provider) == "azure" and _is_azure_data_platform_architecture(
        target_architecture
    ):
        return _generate_azure_data_platform_png(target_architecture)
    if _provider_key(target_architecture.provider) == "gcp" and _is_gcp_graphrag_architecture(
        target_architecture
    ):
        return _generate_gcp_graphrag_png(target_architecture)
    if _provider_key(target_architecture.provider) == "gcp" and _is_gcp_hybrid_connectivity_architecture(
        target_architecture
    ):
        return _generate_gcp_hybrid_connectivity_png(target_architecture)
    if _provider_key(target_architecture.provider) != "aws":
        return _generate_fallback_png(
            target_architecture,
            f"Provider-neutral renderer for {_provider_label(target_architecture.provider)}",
        )
    if _is_hybrid_connectivity_architecture(target_architecture):
        return _generate_hybrid_connectivity_png(target_architecture)
    if _is_data_platform_architecture(target_architecture):
        return _generate_data_platform_png(target_architecture)

    try:
        from diagrams import Cluster, Diagram, Edge
        from diagrams.aws.compute import AppRunner, EC2, ECS, ElasticBeanstalk, Lambda
        from diagrams.aws.database import Aurora, DocumentDB, Dynamodb, RDS
        from diagrams.aws.integration import Eventbridge, SNS, SQS
        from diagrams.aws.management import Cloudwatch
        from diagrams.aws.network import (
            ALB,
            DirectConnect,
            ELB,
            PrivateSubnet,
            PublicSubnet,
            Route53,
            RouteTable,
            SiteToSiteVpn,
            TransitGatewayAttachment,
            TransitGateway,
            VPC,
            VPCCustomerGateway,
        )
        from diagrams.aws.security import IAM, KMS, SecretsManager, WAF
        from diagrams.aws.storage import Backup, S3
        from diagrams.generic.blank import Blank
        from diagrams.onprem.client import Users
        from diagrams.onprem.network import CiscoRouter
    except ImportError:
        return _generate_fallback_png(target_architecture, "Pillow fallback renderer")

    node_classes: dict[str, Any] = {
        "app runner": AppRunner,
        "ec2": EC2,
        "ecs": ECS,
        "elastic beanstalk": ElasticBeanstalk,
        "lambda": Lambda,
        "aurora": Aurora,
        "documentdb": DocumentDB,
        "dynamodb": Dynamodb,
        "rds": RDS,
        "eventbridge": Eventbridge,
        "sns": SNS,
        "sqs": SQS,
        "cloudwatch": Cloudwatch,
        "application load balancer": ALB,
        "elastic load balancing": ELB,
        "route 53": Route53,
        "route table": RouteTable,
        "vpc": VPC,
        "iam": IAM,
        "kms": KMS,
        "secrets manager": SecretsManager,
        "waf": WAF,
        "s3": S3,
        "backup": Backup,
        "direct connect": DirectConnect,
        "site-to-site vpn": SiteToSiteVpn,
        "transit gateway attachment": TransitGatewayAttachment,
        "vpc attachment": TransitGatewayAttachment,
        "transit gateway": TransitGateway,
    }

    try:
        _configure_graphviz_executable()
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_base = Path(tmp_dir) / "aws_architecture"
            graph_attr = {
                "bgcolor": "white",
                "pad": "0.35",
                "ranksep": "1.05",
                "nodesep": "0.7",
                "splines": "spline",
            }
            edge_attr = {
                "color": "#62748a",
                "fontcolor": "#334155",
                "fontsize": "10",
                "arrowsize": "0.75",
            }
            with Diagram(
                "Proposed AWS Architecture",
                filename=str(output_base),
                outformat="png",
                show=False,
                direction="LR",
                graph_attr=graph_attr,
                edge_attr=edge_attr,
            ):
                _render_curated_diagram(
                    target_architecture=target_architecture,
                    node_classes=node_classes,
                    blank_class=Blank,
                    cluster_class=Cluster,
                    edge_class=Edge,
                    users_class=Users,
                    onprem_router_class=CiscoRouter,
                    customer_gateway_class=VPCCustomerGateway,
                    vpc_class=VPC,
                    public_subnet_class=PublicSubnet,
                    private_subnet_class=PrivateSubnet,
                )

            output_path = output_base.with_suffix(".png")
            return output_path.read_bytes()
    except Exception as exc:
        return _generate_fallback_png(target_architecture, f"Pillow fallback renderer: {exc}")


def _is_hybrid_connectivity_architecture(target_architecture: TargetArchitecture) -> bool:
    component_ids = {component.id for component in target_architecture.components}
    hybrid_ids = {
        "customer_gateway",
        "aws_direct_connect",
        "transit_vif",
        "ipsec_vpn_tunnels",
        "aws_site_to_site_vpn",
        "aws_transit_gateway",
        "tgw_route_table",
        "tgw_vpc_attachment",
        "private_route_tables",
    }
    return bool(component_ids & hybrid_ids)


def _is_data_platform_architecture(target_architecture: TargetArchitecture) -> bool:
    text = " ".join(
        f"{component.id} {component.name} {component.category or ''}"
        for component in target_architecture.components
    ).lower()
    data_platform_tokens = [
        "iot",
        "sns",
        "sqs",
        "eventbridge",
        "kinesis",
        "pub/sub",
        "glue",
        "emr",
        "redshift",
        "sagemaker",
        "athena",
        "flink",
        "dynamodb",
        "s3",
        "dataflow",
        "dataproc",
        "bigquery",
    ]
    matches = sum(1 for token in data_platform_tokens if token in text)
    return matches >= 2


def _is_azure_data_platform_architecture(target_architecture: TargetArchitecture) -> bool:
    component_ids = {component.id for component in target_architecture.components}
    data_platform_ids = {
        "azure_iot_hub",
        "azure_event_hubs",
        "azure_stream_analytics",
        "azure_functions",
        "adls_gen2",
        "azure_data_factory",
        "azure_databricks",
        "azure_synapse",
        "azure_cosmos_db",
    }
    return len(component_ids & data_platform_ids) >= 3


def _is_azure_graphrag_architecture(target_architecture: TargetArchitecture) -> bool:
    component_ids = {component.id for component in target_architecture.components}
    graphrag_ids = {
        "neo4j_auradb",
        "neo4j_graphrag_retriever",
        "azure_openai_ai_foundry",
        "neo4j_graph_data_science",
        "neo4j_bloom",
        "graphrag_api",
    }
    return len(component_ids & graphrag_ids) >= 3


def _is_gcp_graphrag_architecture(target_architecture: TargetArchitecture) -> bool:
    component_ids = {component.id for component in target_architecture.components}
    graphrag_ids = {
        "neo4j_auradb_gcp",
        "neo4j_graphrag_retriever",
        "vertex_ai_gemini",
        "neo4j_graph_data_science",
        "neo4j_bloom",
        "graphrag_api",
        "vertex_ai",
    }
    return len(component_ids & graphrag_ids) >= 3


def _is_gcp_hybrid_connectivity_architecture(target_architecture: TargetArchitecture) -> bool:
    component_ids = {component.id for component in target_architecture.components}
    hybrid_ids = {
        "on_premises_network",
        "customer_edge_routers",
        "dedicated_interconnect",
        "partner_interconnect",
        "vlan_attachments",
        "cloud_router",
        "ha_vpn_gateway",
        "ha_vpn_tunnels",
        "shared_vpc",
        "private_service_connect",
    }
    return len(component_ids & hybrid_ids) >= 4


def _generate_hybrid_connectivity_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2800
    height = 1450
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(24, bold=True)
    body_font = _font(18)
    small_font = _font(16)
    label_font = _font(17, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "aws_orange": "#ff9900",
        "aws_blue": "#eef7ff",
        "aws_border": "#97b7d5",
        "onprem": "#eef2f7",
        "primary": "#eaf7ef",
        "backup": "#fff4e5",
        "vpc": "#eef8f0",
        "ops": "#f1f5f9",
        "node": "#ffffff",
        "node_border": "#9db2c8",
        "purple": "#6d43d9",
        "blue": "#1677b8",
        "green": "#168a55",
        "red": "#d43131",
    }

    # Header
    draw.rectangle((0, 0, width, 118), fill="#111827")
    draw.text((56, 26), "Proposed AWS Hybrid Connectivity Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "Production-oriented Azure ExpressRoute + VPN Gateway migration pattern for AWS",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    # Section backgrounds
    _rounded_rect(draw, (56, 155, 2544, 525), radius=20, fill=colors["primary"], outline="#b7d7c3", width=3)
    _rounded_rect(draw, (56, 565, 1540, 905), radius=20, fill=colors["backup"], outline="#e7c58d", width=3)
    _rounded_rect(draw, (56, 950, 2544, 1305), radius=20, fill=colors["ops"], outline="#cbd5e1", width=3)

    draw.text((86, 178), "Primary path: Direct Connect", fill=colors["green"], font=section_font)
    draw.text((86, 588), "Backup path: Site-to-Site VPN", fill="#a16207", font=section_font)
    draw.text((86, 973), "Routing controls and operational guardrails", fill=colors["ink"], font=section_font)

    node_w = 250
    node_h = 155
    gap = 40
    primary_y = 278
    start_x = 120

    primary_specs = [
        ("Customer\nrouters (HA)", "Redundant on-premises edge", colors["node_border"]),
        ("Redundant\nDirect Connect", "Two connections", colors["green"]),
        ("Transit VIFs", "BGP over Transit VIF", colors["green"]),
        ("Direct Connect\nGateway", "Associated with Transit Gateway", colors["purple"]),
        ("Transit\nGateway", "Regional routing hub", colors["purple"]),
        ("TGW route\ntable", "Association and propagation", colors["purple"]),
        ("TGW VPC\nattachment", "Connects TGW to VPC", colors["purple"]),
        ("Private\nworkloads", "Private subnets, no public ingress", colors["blue"]),
    ]
    primary_nodes = []
    for index, (title, subtitle, accent) in enumerate(primary_specs):
        x = start_x + index * (node_w + gap)
        primary_nodes.append(
            _node(draw, (x, primary_y, x + node_w, primary_y + node_h), title, subtitle, colors["node"], accent, node_font, body_font)
        )

    for left, right in zip(primary_nodes, primary_nodes[1:]):
        _arrow(draw, _right(left), _left(right), colors["line"])

    backup_y = 688
    backup_specs = [
        ("Customer\nrouters (HA)", "Same redundant edge", colors["node_border"]),
        ("IPsec VPN\ntunnels", "Two tunnels with BGP", "#d97706"),
        ("AWS Site-to-Site\nVPN attachment", "Terminates on Transit Gateway", "#d97706"),
        ("Transit\nGateway", "Same regional routing hub", colors["purple"]),
    ]
    backup_nodes = []
    for index, (title, subtitle, accent) in enumerate(backup_specs):
        x = start_x + index * (node_w + gap)
        backup_nodes.append(
            _node(draw, (x, backup_y, x + node_w, backup_y + node_h), title, subtitle, colors["node"], accent, node_font, body_font)
        )

    for left, right in zip(backup_nodes, backup_nodes[1:]):
        _arrow(draw, _right(left), _left(right), "#8a5a00")

    control_specs = [
        ("Route preference", "Direct Connect is preferred. VPN is failover."),
        ("Transit Gateway route table", "Associates and propagates DX, VPN, and VPC attachment routes."),
        ("Private route tables", "On-premises CIDRs point to the Transit Gateway."),
        ("Operations", "CloudWatch monitoring and IAM least-privilege controls."),
    ]
    control_w = 560
    control_h = 125
    for index, (title, body) in enumerate(control_specs):
        x = 120 + index * (control_w + 40)
        _node(
            draw,
            (x, 1080, x + control_w, 1080 + control_h),
            title,
            body,
            colors["node"],
            colors["blue"] if index in {1, 2} else colors["red"],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _generate_data_platform_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2600
    height = 1500
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(22, bold=True)
    body_font = _font(16)
    label_font = _font(16, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "edge": "#eef7ff",
        "ingest": "#fff7ed",
        "process": "#eef8f0",
        "data": "#f4f0ff",
        "ops": "#eef2f7",
        "node": "#ffffff",
        "node_border": "#9db2c8",
        "blue": "#1677b8",
        "orange": "#d97706",
        "green": "#168a55",
        "purple": "#6d43d9",
        "red": "#d43131",
        "slate": "#64748b",
    }

    draw.rectangle((0, 0, width, 118), fill="#111827")
    draw.text((56, 26), "Proposed AWS Data Platform Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "Clean target pattern for GCP data, analytics, application, and operations services",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    _rounded_rect(draw, (56, 150, width - 56, 1270), radius=20, fill="#eaf4ff", outline="#b8d2ea", width=3)
    draw.text((86, 178), "AWS target environment", fill=colors["ink"], font=section_font)

    columns = _data_platform_columns(target_architecture)
    column_specs = [
        ("Entry & devices", "Client, DNS, public ingress", colors["edge"], colors["blue"], columns["entry"]),
        ("Ingestion", "IoT and event decoupling", colors["ingest"], colors["orange"], columns["ingestion"]),
        ("Processing", "Applications, ETL, ML, analytics", colors["process"], colors["green"], columns["processing"]),
        ("Data stores", "Object, NoSQL, warehouse", colors["data"], colors["purple"], columns["data"]),
        ("Security & operations", "Shared platform controls", colors["ops"], colors["red"], columns["ops"]),
    ]

    col_w = 440
    col_h = 855
    col_gap = 40
    start_x = 110
    col_y = 300
    column_boxes: list[tuple[int, int, int, int]] = []

    for index, (title, subtitle, fill, accent, components) in enumerate(column_specs):
        x = start_x + index * (col_w + col_gap)
        box = (x, col_y, x + col_w, col_y + col_h)
        column_boxes.append(box)
        _rounded_rect(draw, box, radius=18, fill=fill, outline="#c3cfdd", width=2)
        draw.text((x + 24, col_y + 22), title, fill=colors["ink"], font=section_font)
        draw.text((x + 24, col_y + 54), subtitle, fill=colors["muted"], font=body_font)
        _draw_component_stack(
            draw=draw,
            components=components,
            box=(x + 26, col_y + 105, x + col_w - 26, col_y + col_h - 28),
            accent=accent,
            node_font=node_font,
            body_font=body_font,
            placeholder="No dedicated service detected",
        )

    flow_labels = ["route", "ingest", "process", "store/query"]
    for index, (left_box, right_box) in enumerate(zip(column_boxes, column_boxes[1:])):
        y = col_y + 92
        _arrow(
            draw,
            (left_box[2] - 10, y),
            (right_box[0] + 10, y),
            colors["line"],
            label=flow_labels[index],
            font=label_font,
        )

    _rounded_rect(draw, (110, 1195, 2490, 1430), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.text((140, 1223), "Production guardrails", fill=colors["ink"], font=section_font)
    guardrails = [
        ("Network", "Public ingress is isolated from private processing and data services."),
        ("Security", "IAM, KMS, and Secrets Manager are shared controls, not point-to-point app dependencies."),
        ("Operations", "CloudWatch monitors the platform; Backup protects durable data stores."),
    ]
    card_w = 710
    for index, (title, body) in enumerate(guardrails):
        x = 145 + index * (card_w + 55)
        _node(
            draw,
            (x, 1280, x + card_w, 1405),
            title,
            body,
            colors["node"],
            [colors["blue"], colors["red"], colors["green"]][index],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _generate_gcp_hybrid_connectivity_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2800
    height = 1450
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(21, bold=True)
    body_font = _font(16)
    label_font = _font(16, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "entry": "#eef4ff",
        "primary": "#eef8f0",
        "backup": "#fff7ed",
        "routing": "#f4f0ff",
        "vpc": "#eaf7ef",
        "controls": "#eef2f7",
        "blue": "#1677b8",
        "green": "#168a55",
        "orange": "#d97706",
        "purple": "#6d43d9",
        "red": "#d43131",
    }

    draw.rectangle((0, 0, width, 118), fill="#10233f")
    draw.text((56, 26), "Proposed Google Cloud Hybrid Connectivity Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "Azure ExpressRoute + VPN Gateway migration pattern using Interconnect, Cloud Router, HA VPN, and Shared VPC",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    _rounded_rect(draw, (56, 150, width - 56, 1230), radius=20, fill="#eaf4ff", outline="#b8d2ea", width=3)
    draw.text((86, 178), "Google Cloud target environment", fill=colors["ink"], font=section_font)

    columns = _gcp_hybrid_columns(target_architecture)
    col_y = 290
    col_h = 790
    onprem_box = (80, col_y, 470, col_y + col_h)
    paths_box = (505, col_y, 1325, col_y + col_h)
    routing_box = (1360, col_y, 1755, col_y + col_h)
    vpc_box = (1790, col_y, 2185, col_y + col_h)
    controls_box = (2220, col_y, 2615, col_y + col_h)

    column_specs = [
        (onprem_box, "On-premises", "Existing network and HA edge", colors["entry"], colors["blue"]),
        (routing_box, "Routing", "Cloud Router is shared by both paths", colors["routing"], colors["purple"]),
        (vpc_box, "VPC network", "Regional private workloads", colors["vpc"], colors["green"]),
        (controls_box, "Controls", "Private access, security, ops", colors["controls"], colors["red"]),
    ]

    for box, title, subtitle, fill, accent in column_specs:
        _rounded_rect(draw, box, radius=18, fill=fill, outline="#c3cfdd", width=2)
        draw.text((box[0] + 24, col_y + 22), title, fill=colors["ink"], font=section_font)
        draw.text((box[0] + 24, col_y + 54), subtitle, fill=colors["muted"], font=body_font)
        if title == "Controls":
            _draw_gcp_control_groups(
                draw,
                (box[0] + 26, col_y + 105, box[2] - 26, col_y + col_h - 28),
                accent,
                node_font,
                body_font,
            )
        else:
            _draw_gcp_component_stack(
                draw=draw,
                components=columns[_gcp_hybrid_column_for_title(title)],
                box=(box[0] + 26, col_y + 105, box[2] - 26, col_y + col_h - 28),
                accent=accent,
                node_font=node_font,
                body_font=body_font,
                placeholder="No dedicated service detected",
            )

    _rounded_rect(draw, paths_box, radius=18, fill="#ffffff", outline="#c3cfdd", width=2)
    draw.text((paths_box[0] + 24, col_y + 22), "Parallel connectivity paths", fill=colors["ink"], font=section_font)
    draw.text((paths_box[0] + 24, col_y + 54), "Primary Interconnect and backup HA VPN feed Cloud Router separately", fill=colors["muted"], font=body_font)
    primary_lane = (paths_box[0] + 26, col_y + 112, paths_box[2] - 26, col_y + 375)
    backup_lane = (paths_box[0] + 26, col_y + 455, paths_box[2] - 26, col_y + 718)
    _draw_gcp_connectivity_lane(
        draw,
        primary_lane,
        "Primary preferred route",
        "Dedicated or Partner Interconnect",
        columns["primary"],
        colors["primary"],
        colors["green"],
        node_font,
        body_font,
    )
    _draw_gcp_connectivity_lane(
        draw,
        backup_lane,
        "Backup lower-priority route",
        "HA VPN failover with BGP",
        columns["backup"],
        colors["backup"],
        colors["orange"],
        node_font,
        body_font,
    )

    primary_y = (primary_lane[1] + primary_lane[3]) // 2
    backup_y = (backup_lane[1] + backup_lane[3]) // 2
    _arrow(draw, (onprem_box[2] - 10, primary_y), (paths_box[0] + 10, primary_y), colors["line"])
    _arrow(draw, (paths_box[2] - 10, primary_y), (routing_box[0] + 10, primary_y), colors["line"])
    _arrow(draw, (onprem_box[2] - 10, backup_y), (paths_box[0] + 10, backup_y), colors["line"], dashed=True)
    _arrow(draw, (paths_box[2] - 10, backup_y), (routing_box[0] + 10, backup_y), colors["line"], dashed=True)
    _arrow(draw, (routing_box[2] - 10, primary_y), (vpc_box[0] + 10, primary_y), colors["line"], label="dynamic routes", font=label_font)
    _arrow(draw, (vpc_box[2] - 10, primary_y), (controls_box[0] + 10, primary_y), colors["line"], label="private access / controls", font=label_font)

    _rounded_rect(draw, (110, 1160, width - 110, 1390), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.text((140, 1188), "Production guardrails", fill=colors["ink"], font=section_font)
    guardrails = [
        ("Routing", "Cloud Router exchanges BGP routes for both Interconnect and HA VPN; route priorities prefer Interconnect."),
        ("GCP subnet model", "Subnets are regional IP ranges; public/private behavior is controlled by external IPs, NAT, routes, firewalls, and load balancers."),
        ("Private services", "Private Service Connect, Private Google Access, and VPC Service Controls protect managed-service access and data boundaries."),
    ]
    card_w = 780
    for index, (title, body) in enumerate(guardrails):
        x = 145 + index * (card_w + 55)
        _node(
            draw,
            (x, 1245, x + card_w, 1368),
            title,
            body,
            "#ffffff",
            [colors["purple"], colors["green"], colors["red"]][index],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _gcp_hybrid_columns(target_architecture: TargetArchitecture) -> dict[str, list[ArchitectureComponent]]:
    columns: dict[str, list[ArchitectureComponent]] = {
        "onprem": [],
        "primary": [],
        "backup": [],
        "routing": [],
        "vpc": [],
        "controls": [],
    }
    for component in target_architecture.components:
        columns[_gcp_hybrid_column_for(component)].append(component)

    priority = {
        "onprem": ["on_premises_network", "customer_edge_routers", "colo_or_service_provider", "google_edge"],
        "primary": ["dedicated_interconnect", "partner_interconnect"],
        "backup": ["ha_vpn_tunnels", "ha_vpn_gateway"],
        "routing": ["vlan_attachments", "cloud_router"],
        "vpc": ["shared_vpc", "regional_private_subnets", "public_lb_tier", "cloud_nat"],
        "controls": [
            "private_service_connect",
            "private_google_access",
            "firewall_policies",
            "vpc_service_controls",
            "cloud_dns",
            "cloud_iam",
            "cloud_kms",
            "secret_manager",
            "cloud_monitoring_logging",
        ],
    }
    limits = {"onprem": 4, "primary": 3, "backup": 3, "routing": 3, "vpc": 5, "controls": 9}
    for key, ordered_ids in priority.items():
        order = {component_id: index for index, component_id in enumerate(ordered_ids)}
        columns[key].sort(key=lambda component: (order.get(component.id, 99), component.name))
        columns[key] = columns[key][: limits[key]]
    return columns


def _gcp_hybrid_column_for(component: ArchitectureComponent) -> str:
    if component.id in {"on_premises_network", "customer_edge_routers", "colo_or_service_provider", "google_edge"}:
        return "onprem"
    if component.id in {"dedicated_interconnect", "partner_interconnect"}:
        return "primary"
    if component.id in {"ha_vpn_tunnels", "ha_vpn_gateway"}:
        return "backup"
    if component.id in {"vlan_attachments", "cloud_router"}:
        return "routing"
    if component.id in {"shared_vpc", "regional_private_subnets", "public_lb_tier", "cloud_nat"}:
        return "vpc"
    return "controls"


def _gcp_hybrid_column_for_title(title: str) -> str:
    return {
        "On-premises": "onprem",
        "Routing": "routing",
        "VPC network": "vpc",
    }.get(title, "controls")


def _draw_gcp_connectivity_lane(
    draw: Any,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    components: list[ArchitectureComponent],
    fill: str,
    accent: str,
    node_font: Any,
    body_font: Any,
) -> None:
    _rounded_rect(draw, box, radius=16, fill=fill, outline="#c3cfdd", width=2)
    draw.text((box[0] + 22, box[1] + 18), title, fill="#102033", font=node_font)
    draw.text((box[0] + 22, box[1] + 50), subtitle, fill="#52657a", font=body_font)

    content_y = box[1] + 92
    node_h = box[3] - content_y - 26
    shown = components[:2]
    if not shown:
        _node(draw, (box[0] + 24, content_y, box[2] - 24, content_y + node_h), "Not shown", "No connectivity service detected", "#ffffff", accent, node_font, body_font)
        return

    gap = 26
    content_w = box[2] - box[0] - 48
    node_w = (content_w - gap * (len(shown) - 1)) // len(shown)
    nodes: list[tuple[int, int, int, int]] = []
    for index, component in enumerate(shown):
        x = box[0] + 24 + index * (node_w + gap)
        nodes.append(
            _node(
                draw,
                (x, content_y, x + node_w, content_y + node_h),
                _clean_component_title(component.name),
                _gcp_component_subtitle(component),
                "#ffffff",
                accent,
                node_font,
                body_font,
            )
        )

    if len(nodes) == 2 and shown[0].id == "ha_vpn_tunnels":
        _arrow(draw, _right(nodes[0]), _left(nodes[1]), "#50677f")
    elif len(nodes) == 2:
        mid_x = (nodes[0][2] + nodes[1][0]) // 2
        mid_y = (nodes[0][1] + nodes[0][3]) // 2 - 12
        draw.text((mid_x - 10, mid_y), "or", fill="#52657a", font=body_font)


def _draw_gcp_component_stack(
    draw: Any,
    components: list[ArchitectureComponent],
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
    placeholder: str,
) -> None:
    if not components:
        _node(draw, (box[0], box[1], box[2], box[1] + 110), "Not shown", placeholder, "#ffffff", accent, node_font, body_font)
        return

    card_h = min(128, max(105, (box[3] - box[1] - 18 * (len(components) - 1)) // max(1, len(components))))
    y = box[1]
    for component in components:
        _node(
            draw,
            (box[0], y, box[2], y + card_h),
            _clean_component_title(component.name),
            _gcp_component_subtitle(component),
            "#ffffff",
            accent,
            node_font,
            body_font,
        )
        y += card_h + 18


def _gcp_component_subtitle(component: ArchitectureComponent) -> str:
    subtitles = {
        "on_premises_network": "Source network",
        "customer_edge_routers": "HA edge routers + BGP",
        "colo_or_service_provider": "Direct or partner handoff",
        "google_edge": "Google network edge",
        "dedicated_interconnect": "Primary private circuit",
        "partner_interconnect": "Provider option",
        "vlan_attachments": "Interconnect attachment",
        "cloud_router": "BGP for Interconnect and HA VPN",
        "ha_vpn_tunnels": "2 IPsec tunnels + BGP",
        "ha_vpn_gateway": "Backup VPN failover",
        "shared_vpc": "Landing zone network",
        "regional_private_subnets": "Regional private IP ranges",
        "public_lb_tier": "Managed ingress only",
        "cloud_nat": "Private egress",
    }
    return subtitles.get(component.id, f"{component.category or 'service'} | {component.confidence:.0%}")


def _draw_gcp_control_groups(
    draw: Any,
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
) -> None:
    groups = [
        ("Private access", "Private Service Connect, Private Google Access"),
        ("Security perimeter", "Firewall policies, VPC Service Controls, Cloud IAM"),
        ("Operations", "Cloud DNS, Cloud KMS, Secret Manager, Monitoring, Logging"),
    ]
    card_h = 172
    y = box[1]
    for title, subtitle in groups:
        _node(draw, (box[0], y, box[2], y + card_h), title, subtitle, "#ffffff", accent, node_font, body_font)
        y += card_h + 26


def _generate_azure_graphrag_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2800
    height = 1500
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(21, bold=True)
    body_font = _font(16)
    label_font = _font(16, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "data": "#eef4ff",
        "extract": "#fff7ed",
        "graph": "#f4f0ff",
        "rag": "#eef8f0",
        "apps": "#eaf7ef",
        "ops": "#eef2f7",
        "blue": "#1677b8",
        "orange": "#d97706",
        "purple": "#6d43d9",
        "green": "#168a55",
        "red": "#d43131",
    }

    draw.rectangle((0, 0, width, 118), fill="#10233f")
    draw.text((56, 26), "Proposed Azure GraphRAG Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "AWS Neo4j knowledge graph and GraphRAG migration preserving graph database, retrieval, AI, and app layers",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    _rounded_rect(draw, (56, 150, width - 56, 1270), radius=20, fill="#eaf4ff", outline="#b8d2ea", width=3)
    draw.text((86, 178), "Azure target environment", fill=colors["ink"], font=section_font)

    columns = _azure_graphrag_columns(target_architecture)
    column_specs = [
        ("Data sources", "Warehouse, object, streaming, ETL", colors["data"], colors["blue"], columns["data"]),
        ("Parsing / enrichment", "Graph ingestion, chunking, extraction", colors["extract"], colors["orange"], columns["extract"]),
        ("Knowledge graph", "Neo4j remains central", colors["graph"], colors["purple"], columns["graph"]),
        ("GraphRAG", "Graph retrieval and LLM grounding", colors["rag"], colors["green"], columns["rag"]),
        ("Applications", "APIs, jobs, containers, VMs", colors["apps"], colors["blue"], columns["apps"]),
        ("Platform controls", "Network, identity, secrets, ops", colors["ops"], colors["red"], columns["controls"]),
    ]

    col_w = 395
    col_h = 855
    col_gap = 28
    start_x = 80
    col_y = 300
    column_boxes: list[tuple[int, int, int, int]] = []

    for index, (title, subtitle, fill, accent, components) in enumerate(column_specs):
        x = start_x + index * (col_w + col_gap)
        box = (x, col_y, x + col_w, col_y + col_h)
        column_boxes.append(box)
        _rounded_rect(draw, box, radius=18, fill=fill, outline="#c3cfdd", width=2)
        draw.text((x + 24, col_y + 22), title, fill=colors["ink"], font=section_font)
        draw.text((x + 24, col_y + 54), subtitle, fill=colors["muted"], font=body_font)
        content_box = (x + 26, col_y + 105, x + col_w - 26, col_y + col_h - 28)
        if title == "Platform controls":
            _draw_azure_graphrag_control_groups(draw, content_box, accent, node_font, body_font)
        else:
            _draw_azure_graphrag_component_stack(
                draw=draw,
                components=components,
                box=content_box,
                accent=accent,
                node_font=node_font,
                body_font=body_font,
                placeholder="No dedicated service detected",
            )

    flow_labels = ["prepare", "write graph", "retrieve", "serve", "govern"]
    for index, (left_box, right_box) in enumerate(zip(column_boxes, column_boxes[1:])):
        y = col_y + 92
        _arrow(
            draw,
            (left_box[2] - 10, y),
            (right_box[0] + 10, y),
            colors["line"],
            label=flow_labels[index],
            font=label_font,
        )

    _rounded_rect(draw, (110, 1195, width - 110, 1430), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.text((140, 1223), "Production guardrails", fill=colors["ink"], font=section_font)
    guardrails = [
        ("Neo4j", "Keep Neo4j AuraDB or Neo4j on AKS/VMs unless the project explicitly redesigns away from Cypher and Neo4j GDS."),
        ("GraphRAG", "Use Azure OpenAI / Azure AI Foundry with Neo4j retrievers; Azure AI Search is optional for hybrid or vector search."),
        ("Kafka migration", "Validate Kafka client compatibility, retention, partitions, consumer groups, and unsupported broker-level features."),
    ]
    card_w = 780
    for index, (title, body) in enumerate(guardrails):
        x = 145 + index * (card_w + 55)
        _node(
            draw,
            (x, 1280, x + card_w, 1405),
            title,
            body,
            "#ffffff",
            [colors["purple"], colors["green"], colors["red"]][index],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _azure_graphrag_columns(target_architecture: TargetArchitecture) -> dict[str, list[ArchitectureComponent]]:
    columns: dict[str, list[ArchitectureComponent]] = {
        "data": [],
        "extract": [],
        "graph": [],
        "rag": [],
        "apps": [],
        "controls": [],
    }
    for component in target_architecture.components:
        columns[_azure_graphrag_column_for(component)].append(component)

    priority = {
        "data": ["data_sources", "adls_gen2", "azure_event_hubs_kafka", "azure_data_factory", "azure_synapse_fabric"],
        "extract": ["extraction_jobs", "azure_machine_learning", "azure_openai_ai_foundry", "neo4j_cypher_ingestion"],
        "graph": ["neo4j_auradb", "neo4j_bloom", "neo4j_graph_data_science"],
        "rag": ["neo4j_graphrag_retriever", "azure_ai_search_optional", "graphrag_api"],
        "apps": ["azure_functions", "azure_app_hosting", "azure_kubernetes_service", "azure_virtual_machines"],
        "controls": [
            "azure_virtual_network",
            "private_endpoints",
            "managed_identity",
            "azure_key_vault",
            "azure_monitor",
            "azure_policy_defender",
        ],
    }
    limits = {"data": 5, "extract": 4, "graph": 4, "rag": 4, "apps": 4, "controls": 6}
    for key, ordered_ids in priority.items():
        order = {component_id: index for index, component_id in enumerate(ordered_ids)}
        columns[key].sort(key=lambda component: (order.get(component.id, 99), component.name))
        columns[key] = columns[key][: limits[key]]
    return columns


def _azure_graphrag_column_for(component: ArchitectureComponent) -> str:
    if component.id in {"data_sources", "adls_gen2", "azure_event_hubs_kafka", "azure_data_factory", "azure_synapse_fabric"}:
        return "data"
    if component.id in {"extraction_jobs", "azure_machine_learning", "azure_openai_ai_foundry", "neo4j_cypher_ingestion"}:
        return "extract"
    if component.id in {"neo4j_auradb", "neo4j_bloom", "neo4j_graph_data_science"}:
        return "graph"
    if component.id in {"neo4j_graphrag_retriever", "azure_ai_search_optional", "graphrag_api"}:
        return "rag"
    if component.id in {"azure_functions", "azure_app_hosting", "azure_kubernetes_service", "azure_virtual_machines"}:
        return "apps"
    return "controls"


def _draw_azure_graphrag_component_stack(
    draw: Any,
    components: list[ArchitectureComponent],
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
    placeholder: str,
) -> None:
    if not components:
        _node(draw, (box[0], box[1], box[2], box[1] + 110), "Not shown", placeholder, "#ffffff", accent, node_font, body_font)
        return

    card_h = min(128, max(95, (box[3] - box[1] - 18 * (len(components) - 1)) // max(1, len(components))))
    y = box[1]
    for component in components:
        _node(
            draw,
            (box[0], y, box[2], y + card_h),
            _clean_component_title(component.name),
            _azure_graphrag_subtitle(component),
            "#ffffff",
            accent,
            node_font,
            body_font,
        )
        y += card_h + 18


def _azure_graphrag_subtitle(component: ArchitectureComponent) -> str:
    subtitles = {
        "data_sources": "Existing AWS data sources",
        "adls_gen2": "S3 document landing zone",
        "azure_event_hubs_kafka": "MSK-style Kafka streams",
        "azure_data_factory": "Glue-style ETL orchestration",
        "azure_synapse_fabric": "Redshift-style warehouse",
        "extraction_jobs": "Parse, chunk, extract entities",
        "azure_machine_learning": "SageMaker-style ML pipelines",
        "azure_openai_ai_foundry": "Bedrock-style foundation models",
        "neo4j_cypher_ingestion": "Cypher writes to graph",
        "neo4j_auradb": "Knowledge graph store",
        "neo4j_bloom": "Graph exploration",
        "neo4j_graph_data_science": "Algorithms and embeddings",
        "neo4j_graphrag_retriever": "Cypher and graph context",
        "azure_ai_search_optional": "Optional hybrid/vector search",
        "graphrag_api": "Retrieval + Azure OpenAI",
        "azure_functions": "Lambda-style serverless",
        "azure_app_hosting": "Managed GraphRAG APIs",
        "azure_kubernetes_service": "EKS-style containers",
        "azure_virtual_machines": "EC2-style lift-and-shift",
    }
    return subtitles.get(component.id, f"{component.category or 'service'} | {component.confidence:.0%}")


def _draw_azure_graphrag_control_groups(
    draw: Any,
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
) -> None:
    groups = [
        ("Network", "VNet, Private Endpoints, Private Link"),
        ("Identity & secrets", "Managed Identity, Entra ID / RBAC, Key Vault"),
        ("Operations & security", "Monitor, Log Analytics, App Insights, Policy, Defender"),
    ]
    card_h = 190
    y = box[1]
    for title, subtitle in groups:
        _node(draw, (box[0], y, box[2], y + card_h), title, subtitle, "#ffffff", accent, node_font, body_font)
        y += card_h + 26


def _generate_gcp_graphrag_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2800
    height = 1500
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(21, bold=True)
    body_font = _font(16)
    label_font = _font(16, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "data": "#eef4ff",
        "extract": "#fff7ed",
        "graph": "#f4f0ff",
        "rag": "#eef8f0",
        "apps": "#eaf7ef",
        "ops": "#eef2f7",
        "blue": "#1677b8",
        "orange": "#d97706",
        "purple": "#6d43d9",
        "green": "#168a55",
        "red": "#d43131",
    }

    draw.rectangle((0, 0, width, 118), fill="#10233f")
    draw.text((56, 26), "Proposed Google Cloud GraphRAG Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "AWS Neo4j knowledge graph and GraphRAG migration preserving graph database, retrieval, AI, and app layers",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    _rounded_rect(draw, (56, 150, width - 56, 1270), radius=20, fill="#eaf4ff", outline="#b8d2ea", width=3)
    draw.text((86, 178), "Google Cloud target environment", fill=colors["ink"], font=section_font)

    columns = _gcp_graphrag_columns(target_architecture)
    column_specs = [
        ("Data sources", "Warehouse, object, streaming, ETL", colors["data"], colors["blue"], columns["data"]),
        ("Parsing / enrichment", "Graph ingestion, chunking, extraction", colors["extract"], colors["orange"], columns["extract"]),
        ("Knowledge graph", "Neo4j remains central", colors["graph"], colors["purple"], columns["graph"]),
        ("GraphRAG", "Graph retrieval and LLM grounding", colors["rag"], colors["green"], columns["rag"]),
        ("Applications", "APIs, jobs, containers, VMs", colors["apps"], colors["blue"], columns["apps"]),
        ("Platform controls", "Network, identity, secrets, ops", colors["ops"], colors["red"], columns["controls"]),
    ]

    col_w = 395
    col_h = 855
    col_gap = 28
    start_x = 80
    col_y = 300
    column_boxes: list[tuple[int, int, int, int]] = []

    for index, (title, subtitle, fill, accent, components) in enumerate(column_specs):
        x = start_x + index * (col_w + col_gap)
        box = (x, col_y, x + col_w, col_y + col_h)
        column_boxes.append(box)
        _rounded_rect(draw, box, radius=18, fill=fill, outline="#c3cfdd", width=2)
        draw.text((x + 24, col_y + 22), title, fill=colors["ink"], font=section_font)
        draw.text((x + 24, col_y + 54), subtitle, fill=colors["muted"], font=body_font)
        content_box = (x + 26, col_y + 105, x + col_w - 26, col_y + col_h - 28)
        if title == "Platform controls":
            _draw_gcp_graphrag_control_groups(draw, content_box, accent, node_font, body_font)
        else:
            _draw_gcp_graphrag_component_stack(
                draw=draw,
                components=components,
                box=content_box,
                accent=accent,
                node_font=node_font,
                body_font=body_font,
                placeholder="No dedicated service detected",
            )

    flow_labels = ["prepare", "write graph", "retrieve", "serve", "govern"]
    for index, (left_box, right_box) in enumerate(zip(column_boxes, column_boxes[1:])):
        y = col_y + 92
        _arrow(
            draw,
            (left_box[2] - 10, y),
            (right_box[0] + 10, y),
            colors["line"],
            label=flow_labels[index],
            font=label_font,
        )

    _rounded_rect(draw, (110, 1195, width - 110, 1430), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.text((140, 1223), "Production guardrails", fill=colors["ink"], font=section_font)
    guardrails = [
        ("Neo4j", "Keep Neo4j AuraDB on Google Cloud unless the project redesigns away from Cypher, Bloom, and GDS."),
        ("GraphRAG", "Use Vertex AI / Gemini with Neo4j retrievers; Vertex AI Vector Search is optional for hybrid retrieval."),
        ("Kafka migration", "Validate Kafka clients, retention, partitions, consumer groups, and unsupported broker-level features."),
    ]
    card_w = 780
    for index, (title, body) in enumerate(guardrails):
        x = 145 + index * (card_w + 55)
        _node(
            draw,
            (x, 1280, x + card_w, 1405),
            title,
            body,
            "#ffffff",
            [colors["purple"], colors["green"], colors["red"]][index],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _gcp_graphrag_columns(target_architecture: TargetArchitecture) -> dict[str, list[ArchitectureComponent]]:
    columns: dict[str, list[ArchitectureComponent]] = {
        "data": [],
        "extract": [],
        "graph": [],
        "rag": [],
        "apps": [],
        "controls": [],
    }
    for component in target_architecture.components:
        columns[_gcp_graphrag_column_for(component)].append(component)

    priority = {
        "data": ["data_sources", "bigquery", "cloud_storage", "managed_kafka", "cloud_data_fusion_dataflow"],
        "extract": ["parsing_jobs", "vertex_ai", "vertex_ai_gemini", "neo4j_cypher_ingestion"],
        "graph": ["neo4j_auradb_gcp", "neo4j_bloom", "neo4j_graph_data_science"],
        "rag": ["neo4j_graphrag_retriever", "vertex_ai_vector_search_optional", "graphrag_api"],
        "apps": ["cloud_run_functions", "cloud_run_services", "google_kubernetes_engine", "compute_engine"],
        "controls": [
            "vpc_network",
            "private_service_connect",
            "cloud_iam",
            "secret_manager",
            "cloud_kms",
            "cloud_monitoring_logging",
            "cloud_armor_firewall",
            "vpc_service_controls",
        ],
    }
    limits = {"data": 5, "extract": 4, "graph": 4, "rag": 4, "apps": 4, "controls": 8}
    for key, ordered_ids in priority.items():
        order = {component_id: index for index, component_id in enumerate(ordered_ids)}
        columns[key].sort(key=lambda component: (order.get(component.id, 99), component.name))
        columns[key] = columns[key][: limits[key]]
    return columns


def _gcp_graphrag_column_for(component: ArchitectureComponent) -> str:
    if component.id in {"data_sources", "bigquery", "cloud_storage", "managed_kafka", "cloud_data_fusion_dataflow"}:
        return "data"
    if component.id in {"parsing_jobs", "vertex_ai", "vertex_ai_gemini", "neo4j_cypher_ingestion"}:
        return "extract"
    if component.id in {"neo4j_auradb_gcp", "neo4j_bloom", "neo4j_graph_data_science"}:
        return "graph"
    if component.id in {"neo4j_graphrag_retriever", "vertex_ai_vector_search_optional", "graphrag_api"}:
        return "rag"
    if component.id in {"cloud_run_functions", "cloud_run_services", "google_kubernetes_engine", "compute_engine"}:
        return "apps"
    return "controls"


def _draw_gcp_graphrag_component_stack(
    draw: Any,
    components: list[ArchitectureComponent],
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
    placeholder: str,
) -> None:
    if not components:
        _node(draw, (box[0], box[1], box[2], box[1] + 110), "Not shown", placeholder, "#ffffff", accent, node_font, body_font)
        return

    card_h = min(128, max(95, (box[3] - box[1] - 18 * (len(components) - 1)) // max(1, len(components))))
    y = box[1]
    for component in components:
        _node(
            draw,
            (box[0], y, box[2], y + card_h),
            _clean_component_title(component.name),
            _gcp_graphrag_subtitle(component),
            "#ffffff",
            accent,
            node_font,
            body_font,
        )
        y += card_h + 18


def _gcp_graphrag_subtitle(component: ArchitectureComponent) -> str:
    subtitles = {
        "data_sources": "Existing AWS data sources",
        "bigquery": "Redshift-style warehouse",
        "cloud_storage": "S3 object landing zone",
        "managed_kafka": "MSK-compatible Kafka",
        "cloud_data_fusion_dataflow": "Glue-style ETL / pipelines",
        "parsing_jobs": "Parse, chunk, extract entities",
        "vertex_ai": "SageMaker-style ML pipelines",
        "vertex_ai_gemini": "Bedrock-style Gemini models",
        "neo4j_cypher_ingestion": "Cypher writes to graph",
        "neo4j_auradb_gcp": "Knowledge graph store",
        "neo4j_bloom": "Graph exploration",
        "neo4j_graph_data_science": "Algorithms and embeddings",
        "neo4j_graphrag_retriever": "Cypher and graph context",
        "vertex_ai_vector_search_optional": "Optional hybrid/vector search",
        "graphrag_api": "Retrieval + Vertex AI",
        "cloud_run_functions": "Lambda-style serverless",
        "cloud_run_services": "Managed GraphRAG APIs",
        "google_kubernetes_engine": "EKS-style containers",
        "compute_engine": "EC2-style lift-and-shift",
    }
    return subtitles.get(component.id, f"{component.category or 'service'} | {component.confidence:.0%}")


def _draw_gcp_graphrag_control_groups(
    draw: Any,
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
) -> None:
    groups = [
        ("Network", "VPC, Private Service Connect, firewall policies"),
        ("Identity & secrets", "Cloud IAM, Secret Manager, Cloud KMS"),
        ("Operations & security", "Cloud Monitoring, Cloud Logging, Cloud Armor, VPC Service Controls"),
    ]
    card_h = 190
    y = box[1]
    for title, subtitle in groups:
        _node(draw, (box[0], y, box[2], y + card_h), title, subtitle, "#ffffff", accent, node_font, body_font)
        y += card_h + 26


def _generate_azure_data_platform_png(target_architecture: TargetArchitecture) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw

    width = 2600
    height = 1500
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)

    title_font = _font(42, bold=True)
    subtitle_font = _font(22)
    section_font = _font(22, bold=True)
    node_font = _font(22, bold=True)
    body_font = _font(16)
    label_font = _font(16, bold=True)

    colors = {
        "ink": "#102033",
        "muted": "#52657a",
        "line": "#50677f",
        "entry": "#eef4ff",
        "ingest": "#fff7ed",
        "process": "#eef8f0",
        "data": "#f4f0ff",
        "ops": "#eef2f7",
        "node": "#ffffff",
        "blue": "#1677b8",
        "orange": "#d97706",
        "green": "#168a55",
        "purple": "#6d43d9",
        "red": "#d43131",
    }

    draw.rectangle((0, 0, width, 118), fill="#10233f")
    draw.text((56, 26), "Proposed Azure Data Platform Architecture", fill="#ffffff", font=title_font)
    draw.text(
        (56, 78),
        "GCP data platform migration preserving device ingestion, processing, analytics, serving, and controls",
        fill="#d7e0ea",
        font=subtitle_font,
    )

    _rounded_rect(draw, (56, 150, 2544, 1270), radius=20, fill="#eaf4ff", outline="#b8d2ea", width=3)
    draw.text((86, 178), "Azure target environment", fill=colors["ink"], font=section_font)

    columns = _azure_data_platform_columns(target_architecture)
    column_specs = [
        ("Entry", "IoT devices, users, and edge clients", colors["entry"], colors["blue"], columns["entry"]),
        ("Ingestion", "Device and telemetry event intake", colors["ingest"], colors["orange"], columns["ingestion"]),
        ("Processing", "Stream, batch, events, and ML", colors["process"], colors["green"], columns["processing"]),
        ("Data lake / warehouse", "Raw, curated, Spark, and analytics", colors["data"], colors["purple"], columns["lake"]),
        ("Serving / consumers", "Operational apps, APIs, BI", "#f0fdf4", colors["blue"], columns["serving"]),
        ("Platform controls", "Cross-cutting guardrails", colors["ops"], colors["red"], columns["controls"]),
    ]

    col_w = 395
    col_h = 855
    col_gap = 28
    start_x = 80
    col_y = 300
    column_boxes: list[tuple[int, int, int, int]] = []

    for index, (title, subtitle, fill, accent, components) in enumerate(column_specs):
        x = start_x + index * (col_w + col_gap)
        box = (x, col_y, x + col_w, col_y + col_h)
        column_boxes.append(box)
        _rounded_rect(draw, box, radius=18, fill=fill, outline="#c3cfdd", width=2)
        draw.text((x + 24, col_y + 22), title, fill=colors["ink"], font=section_font)
        draw.text((x + 24, col_y + 54), subtitle, fill=colors["muted"], font=body_font)
        content_box = (x + 26, col_y + 105, x + col_w - 26, col_y + col_h - 28)
        if title == "Platform controls":
            _draw_azure_control_groups(draw, content_box, accent, node_font, body_font)
        else:
            _draw_component_stack(
                draw=draw,
                components=components,
                box=content_box,
                accent=accent,
                node_font=node_font,
                body_font=body_font,
                placeholder="No dedicated service detected",
                subtitle_source="description",
            )

    flow_labels = ["secure ingress", "events", "curate", "serve", "govern"]
    for index, (left_box, right_box) in enumerate(zip(column_boxes, column_boxes[1:])):
        y = col_y + 92
        _arrow(
            draw,
            (left_box[2] - 10, y),
            (right_box[0] + 10, y),
            colors["line"],
            label=flow_labels[index],
            font=label_font,
        )

    controls_box = column_boxes[-1]
    first_box = column_boxes[0]
    cross_y = col_y + col_h + 38
    _dashed_line(draw, (first_box[0] + 10, cross_y), (controls_box[0] - 10, cross_y), fill=colors["line"], width=4)
    _draw_arrow_head(draw, (controls_box[0] - 70, cross_y), (first_box[0] + 10, cross_y), color=colors["line"])
    draw.text(
        (first_box[0] + 10, cross_y + 12),
        "network, identity, secrets, observability, governance, and recovery apply across all layers",
        fill=colors["muted"],
        font=label_font,
    )

    _rounded_rect(draw, (110, 1195, width - 110, 1430), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.text((140, 1223), "Production guardrails", fill=colors["ink"], font=section_font)
    guardrails = [
        ("Ingestion", "IoT Hub handles device identity and secure device ingress; Event Hubs handles high-throughput telemetry."),
        ("Data platform", "ADLS Gen2 stores raw and curated zones; Synapse/Fabric and Databricks serve analytics workloads."),
        ("Security", "Private Link, Managed Identity, Entra ID/RBAC, Key Vault, Policy, Monitor, and Backup are shared controls."),
    ]
    card_w = 780
    for index, (title, body) in enumerate(guardrails):
        x = 145 + index * (card_w + 55)
        _node(
            draw,
            (x, 1280, x + card_w, 1405),
            title,
            body,
            colors["node"],
            [colors["orange"], colors["purple"], colors["red"]][index],
            node_font,
            body_font,
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _azure_data_platform_columns(target_architecture: TargetArchitecture) -> dict[str, list[ArchitectureComponent]]:
    columns: dict[str, list[ArchitectureComponent]] = {
        "entry": [],
        "ingestion": [],
        "processing": [],
        "lake": [],
        "serving": [],
        "controls": [],
    }
    for component in target_architecture.components:
        key = _azure_data_platform_column_for(component)
        columns[key].append(component)

    priority = {
        "entry": ["iot_devices", "standard_devices"],
        "ingestion": ["azure_iot_hub", "azure_event_hubs"],
        "processing": [
            "azure_stream_analytics",
            "azure_functions",
            "azure_data_factory",
            "azure_machine_learning",
        ],
        "lake": ["adls_gen2", "azure_databricks", "azure_synapse"],
        "serving": ["azure_cosmos_db", "azure_app_hosting", "consumers_bi_apis"],
        "controls": [
            "azure_virtual_network",
            "private_endpoints",
            "managed_identity",
            "azure_key_vault",
            "azure_monitor",
            "nsg_firewall_waf",
            "azure_policy",
            "azure_backup",
        ],
    }
    limits = {
        "entry": 3,
        "ingestion": 4,
        "processing": 4,
        "lake": 4,
        "serving": 4,
        "controls": 8,
    }
    for key, ordered_ids in priority.items():
        order = {component_id: index for index, component_id in enumerate(ordered_ids)}
        columns[key].sort(key=lambda component: (order.get(component.id, 99), component.name))
        columns[key] = columns[key][: limits[key]]
    return columns


def _azure_data_platform_column_for(component: ArchitectureComponent) -> str:
    text = f"{component.id} {component.name} {component.category or ''}".lower()
    if component.id in {"iot_devices", "standard_devices"} or component.category in {"client", "external"}:
        return "entry"
    if component.id in {"azure_iot_hub", "azure_event_hubs"} or any(
        token in text for token in ["iot hub", "event hubs", "service bus", "event grid"]
    ):
        return "ingestion"
    if component.id in {"adls_gen2", "azure_synapse", "azure_databricks"}:
        return "lake"
    if component.id in {"azure_cosmos_db", "azure_app_hosting", "consumers_bi_apis"}:
        return "serving"
    if component.category in {"storage"} or any(
        token in text for token in ["adls", "blob", "synapse", "fabric", "databricks"]
    ):
        return "lake"
    if component.category in {"database"} or any(
        token in text for token in ["cosmos", "app service", "container apps", "consumers", "power bi", "apis"]
    ):
        return "serving"
    if component.category in {"security", "observability", "resilience", "networking"} or any(
        token in text for token in ["monitor", "key vault", "identity", "entra", "private", "firewall", "policy", "backup", "vnet"]
    ):
        return "controls"
    if component.category in {"compute", "analytics", "ml", "application"} or any(
        token in text for token in ["stream analytics", "functions", "data factory", "databricks", "machine learning"]
    ):
        return "processing"
    return "processing"


def _draw_azure_control_groups(
    draw: Any,
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
) -> None:
    groups = [
        (
            "Network security",
            "VNet, Private Link, NSGs, Azure Firewall / WAF",
        ),
        (
            "Identity & secrets",
            "Managed Identity, Entra ID / RBAC, Azure Key Vault",
        ),
        (
            "Operations & governance",
            "Azure Monitor, Log Analytics, App Insights, Policy, Tags, Backup",
        ),
    ]
    card_h = 190
    y = box[1]
    for title, subtitle in groups:
        _node(draw, (box[0], y, box[2], y + card_h), title, subtitle, "#ffffff", accent, node_font, body_font)
        y += card_h + 26


def _data_platform_columns(target_architecture: TargetArchitecture) -> dict[str, list[ArchitectureComponent]]:
    columns: dict[str, list[ArchitectureComponent]] = {
        "entry": [],
        "ingestion": [],
        "processing": [],
        "data": [],
        "ops": [],
    }
    for component in target_architecture.components:
        if component.id in {"vpc", "public_subnets", "private_subnets"}:
            continue
        key = _data_platform_column_for(component)
        columns[key].append(component)

    priority = {
        "entry": ["users", "route53", "application_load_balancer", "elastic_load_balancing", "aws_waf"],
        "ingestion": ["aws_iot_core", "amazon_kinesis", "amazon_sns_sqs", "amazon_sns", "amazon_sqs", "amazon_eventbridge"],
        "processing": [
            "aws_application_hosting_options",
            "amazon_ec2",
            "aws_glue",
            "amazon_managed_flink",
            "amazon_emr",
            "amazon_sagemaker_studio",
        ],
        "data": [
            "amazon_s3",
            "amazon_dynamodb",
            "amazon_redshift",
            "amazon_athena_glue_catalog",
            "amazon_rds",
            "amazon_aurora",
        ],
        "ops": ["aws_observability_stack", "iam", "aws_kms", "aws_secrets_manager", "aws_backup", "amazon_cloudwatch"],
    }
    limits = {
        "entry": 5,
        "ingestion": 5,
        "processing": 6,
        "data": 5,
        "ops": 5,
    }
    for key, ordered_ids in priority.items():
        order = {component_id: index for index, component_id in enumerate(ordered_ids)}
        columns[key].sort(key=lambda component: (order.get(component.id, 99), component.name))
        columns[key] = columns[key][: limits[key]]
    return columns


def _data_platform_column_for(component: ArchitectureComponent) -> str:
    text = f"{component.id} {component.name} {component.category or ''}".lower()
    if component.id in {"users", "route53", "application_load_balancer", "elastic_load_balancing", "aws_waf"}:
        return "entry"
    if component.id in {"amazon_athena_glue_catalog"}:
        return "data"
    if component.category in {"security", "observability", "resilience"} or any(
        token in text for token in ["iam", "kms", "secret", "cloudwatch", "backup", "logging", "monitoring"]
    ):
        return "ops"
    if component.category in {"storage", "database"} or any(
        token in text for token in ["s3", "dynamodb", "redshift", "rds", "aurora", "documentdb"]
    ):
        return "data"
    if component.category in {"messaging", "iot"} or any(
        token in text for token in ["iot", "sns", "sqs", "eventbridge", "kinesis", "pub/sub"]
    ):
        return "ingestion"
    if component.category in {"compute", "application", "analytics", "ml"} or any(
        token in text for token in ["ec2", "ecs", "lambda", "beanstalk", "app runner", "glue", "emr", "sagemaker"]
    ):
        return "processing"
    return "entry" if component.category in {"client", "external"} else "processing"


def _draw_component_stack(
    draw: Any,
    components: list[ArchitectureComponent],
    box: tuple[int, int, int, int],
    accent: str,
    node_font: Any,
    body_font: Any,
    placeholder: str,
    subtitle_source: str = "meta",
) -> None:
    if not components:
        _node(draw, (box[0], box[1], box[2], box[1] + 110), "Not shown", placeholder, "#ffffff", accent, node_font, body_font)
        return

    card_h = min(125, max(92, (box[3] - box[1] - 18 * (len(components) - 1)) // max(1, len(components))))
    y = box[1]
    for component in components:
        title = _clean_component_title(component.name)
        subtitle = (
            _compact_subtitle(component.description or "")
            if subtitle_source == "description" and component.description
            else f"{component.category or 'service'} | {component.confidence:.0%}"
        )
        _node(draw, (box[0], y, box[2], y + card_h), title, subtitle, "#ffffff", accent, node_font, body_font)
        y += card_h + 18


def _compact_subtitle(value: str) -> str:
    text = " ".join(value.split())
    if len(text) > 82:
        return text[:79].rstrip() + "..."
    return text


def _clean_component_title(name: str) -> str:
    aliases = {
        "Amazon SNS + Amazon SQS": "SNS + SQS",
        "EventBridge / SNS + SQS": "EventBridge / SNS + SQS",
        "Amazon Kinesis Data Streams / Firehose": "Kinesis Streams / Firehose",
        "Amazon Managed Service for Apache Flink": "Managed Flink",
        "Amazon Athena + AWS Glue Data Catalog": "Athena + Glue Catalog",
        "AWS Application Hosting Options": "Application hosting options",
        "Application hosting options": "Application hosting options",
        "CloudWatch / CloudTrail / OpenSearch": "CloudWatch\nCloudTrail\nOpenSearch",
        "Azure Data Lake Storage Gen2": "Azure Data Lake\nStorage Gen2",
        "Synapse Analytics or Microsoft Fabric": "Synapse Analytics\nor Microsoft Fabric",
        "Azure Synapse Analytics / Microsoft Fabric": "Synapse Analytics\nor Microsoft Fabric",
        "App Service / Container Apps / AKS": "App Service\nContainer Apps / AKS",
        "Consumers / BI / APIs": "Consumers\nBI / APIs",
        "Azure Monitor + Log Analytics + Application Insights": "Azure Monitor\nLog Analytics\nApp Insights",
        "Managed Identity + Entra ID / RBAC": "Managed Identity\nEntra ID / RBAC",
        "Private Endpoints / Private Link": "Private Endpoints\nPrivate Link",
        "NSGs + Azure Firewall / WAF": "NSGs\nFirewall / WAF",
        "Azure Backup / Recovery Services": "Azure Backup\nRecovery Services",
        "Customer edge routers (HA)": "Customer edge\nrouters (HA)",
        "Colocation / service provider edge": "Colocation /\nprovider edge",
        "Dedicated Interconnect": "Dedicated\nInterconnect",
        "Partner Interconnect option": "Partner\nInterconnect option",
        "VLAN attachments": "VLAN\nattachments",
        "Cloud Router with BGP": "Cloud Router\nwith BGP",
        "HA VPN tunnels (2) with BGP": "HA VPN tunnels\n(2) with BGP",
        "HA VPN gateway": "HA VPN\ngateway",
        "Shared VPC / VPC Network": "Shared VPC\nVPC Network",
        "Regional private workload subnets": "Regional private\nworkload subnets",
        "Public-facing load balancer tier": "Public-facing\nload balancer tier",
        "Cloud NAT for private egress": "Cloud NAT\nprivate egress",
        "Private Service Connect": "Private Service\nConnect",
        "Private Google Access": "Private Google\nAccess",
        "VPC Service Controls": "VPC Service\nControls",
        "Cloud Monitoring + Cloud Logging": "Cloud Monitoring\nCloud Logging",
        "Azure Event Hubs with Kafka support": "Event Hubs\nKafka support",
        "Azure Data Factory / Fabric Data Factory": "Data Factory\nFabric Data Factory",
        "Synapse Analytics or Microsoft Fabric Warehouse": "Synapse / Fabric\nWarehouse",
        "Azure Functions / Databricks extraction jobs": "Functions / Databricks\nextraction jobs",
        "Azure OpenAI / Azure AI Foundry": "Azure OpenAI\nAI Foundry",
        "Neo4j driver / Cypher ingestion service": "Neo4j driver\nCypher ingestion",
        "Neo4j AuraDB on Azure / Neo4j on AKS or VMs": "Neo4j AuraDB\nor Neo4j on AKS/VMs",
        "Neo4j Graph Data Science": "Neo4j Graph\nData Science",
        "Neo4j GraphRAG retriever / Neo4j driver": "Neo4j GraphRAG\nretriever",
        "Optional Azure AI Search": "Optional\nAzure AI Search",
        "GraphRAG API / orchestration service": "GraphRAG API\norchestration",
        "GraphRAG API + Azure OpenAI orchestration": "GraphRAG API\n+ Azure OpenAI",
        "Azure Policy + Defender for Cloud": "Azure Policy\nDefender for Cloud",
        "Redshift / S3 / MSK / Glue inputs": "Redshift / S3\nMSK / Glue inputs",
        "BigQuery - Redshift replacement": "BigQuery\nRedshift replacement",
        "Cloud Storage - S3 landing zone": "Cloud Storage\nS3 landing zone",
        "Managed Service for Apache Kafka": "Managed Kafka\nservice",
        "Cloud Data Fusion / Dataflow / Dataproc": "Data Fusion\nDataflow / Dataproc",
        "Cloud Run jobs / Dataflow parsing": "Cloud Run jobs\nDataflow parsing",
        "Vertex AI / Gemini": "Vertex AI\nGemini",
        "Neo4j AuraDB on Google Cloud": "Neo4j AuraDB\non Google Cloud",
        "Neo4j Graph Data Science / AuraDS": "Neo4j GDS\nAuraDS",
        "Neo4j GraphRAG retriever / Cypher retrieval": "Neo4j GraphRAG\nCypher retrieval",
        "Optional Vertex AI Vector Search": "Optional Vertex AI\nVector Search",
        "GraphRAG API + Vertex AI orchestration": "GraphRAG API\n+ Vertex AI",
        "Cloud Run functions / Cloud Functions": "Cloud Run functions\nCloud Functions",
        "Cloud Run services": "Cloud Run\nservices",
        "Google Kubernetes Engine": "Google Kubernetes\nEngine",
        "Cloud Armor + firewall policies": "Cloud Armor\nfirewall policies",
    }
    if name in aliases:
        return aliases[name]

    replacements = {
        "Amazon ": "",
        "AWS ": "",
        "Application ": "",
        "Elastic ": "",
    }
    cleaned = name
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    if len(cleaned) > 34:
        cleaned = cleaned[:31].rstrip() + "..."
    return cleaned


def _rounded_rect(
    draw: Any,
    box: tuple[int, int, int, int],
    *,
    radius: int,
    fill: str,
    outline: str,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _node(
    draw: Any,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    fill: str,
    accent: str,
    title_font: Any,
    body_font: Any,
) -> tuple[int, int, int, int]:
    _rounded_rect(draw, box, radius=18, fill=fill, outline="#9db2c8", width=3)
    draw.rounded_rectangle((box[0], box[1], box[0] + 14, box[3]), radius=18, fill=accent)
    draw.rectangle((box[0] + 8, box[1], box[0] + 18, box[3]), fill=accent)

    title_lines = title.split("\n")
    title_height = sum(_text_size(draw, line, title_font)[1] for line in title_lines) + 6 * (len(title_lines) - 1)
    title_y = box[1] + 28
    if title_height > (box[3] - box[1]) * 0.5:
        title_y = box[1] + 18
    _draw_centered_lines(draw, title_lines, (box[0] + 24, title_y, box[2] - 18, title_y + title_height), title_font, "#102033")

    subtitle_lines = _wrap_text(draw, subtitle, body_font, max_width=box[2] - box[0] - 52)
    subtitle_y = max(title_y + title_height + 18, box[3] - 58)
    _draw_centered_lines(draw, subtitle_lines[:2], (box[0] + 24, subtitle_y, box[2] - 18, box[3] - 18), body_font, "#52657a")
    return box


def _draw_centered_lines(
    draw: Any,
    lines: list[str],
    box: tuple[int, int, int, int],
    font: Any,
    fill: str,
) -> None:
    heights = [_text_size(draw, line, font)[1] for line in lines]
    total_height = sum(heights) + 6 * max(0, len(lines) - 1)
    y = box[1] + max(0, (box[3] - box[1] - total_height) // 2)
    for line, line_height in zip(lines, heights):
        line_width = _text_size(draw, line, font)[0]
        x = box[0] + max(0, (box[2] - box[0] - line_width) // 2)
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height + 6


def _wrap_text(draw: Any, text: str, font: Any, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and _text_size(draw, candidate, font)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [text]


def _text_size(draw: Any, text: str, font: Any) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _left(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return box[0], (box[1] + box[3]) // 2


def _right(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return box[2], (box[1] + box[3]) // 2


def _top(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return (box[0] + box[2]) // 2, box[1]


def _bottom(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return (box[0] + box[2]) // 2, box[3]


def _arrow(
    draw: Any,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    *,
    label: str = "",
    font: Any | None = None,
    dashed: bool = False,
    elbow_y: int | None = None,
) -> None:
    points = [start, end]
    if elbow_y is not None:
        mid_x = (start[0] + end[0]) // 2
        points = [start, (mid_x, elbow_y), end]

    for point_a, point_b in zip(points, points[1:]):
        if dashed:
            _dashed_line(draw, point_a, point_b, fill=color, width=4)
        else:
            draw.line((*point_a, *point_b), fill=color, width=4)
    _draw_arrow_head(draw, points[-2], points[-1], color=color)

    if label and font:
        label_point_a, label_point_b = _best_label_segment(points)
        x = (label_point_a[0] + label_point_b[0]) // 2
        y = (label_point_a[1] + label_point_b[1]) // 2 - 30
        text_width, text_height = _text_size(draw, label, font)
        pad_x = 10
        pad_y = 5
        draw.rounded_rectangle(
            (x - text_width // 2 - pad_x, y - pad_y, x + text_width // 2 + pad_x, y + text_height + pad_y),
            radius=8,
            fill="#f8fafc",
            outline="#d7dee8",
            width=1,
        )
        draw.text((x - text_width // 2, y), label, fill="#102033", font=font)


def _best_label_segment(points: list[tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    return max(zip(points, points[1:]), key=lambda segment: _distance(segment[0], segment[1]))


def _distance(point_a: tuple[int, int], point_b: tuple[int, int]) -> float:
    return math.hypot(point_b[0] - point_a[0], point_b[1] - point_a[1])


def _dashed_line(
    draw: Any,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    width: int,
    dash: int = 16,
    gap: int = 12,
) -> None:
    total = _distance(start, end)
    if total == 0:
        return
    dx = (end[0] - start[0]) / total
    dy = (end[1] - start[1]) / total
    current = 0.0
    while current < total:
        segment_end = min(total, current + dash)
        p1 = (int(start[0] + dx * current), int(start[1] + dy * current))
        p2 = (int(start[0] + dx * segment_end), int(start[1] + dy * segment_end))
        draw.line((*p1, *p2), fill=fill, width=width)
        current += dash + gap


def _draw_arrow_head(
    draw: Any,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    color: str,
    size: int = 18,
) -> None:
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (
        end[0] - size * math.cos(angle - math.pi / 6),
        end[1] - size * math.sin(angle - math.pi / 6),
    )
    right = (
        end[0] - size * math.cos(angle + math.pi / 6),
        end[1] - size * math.sin(angle + math.pi / 6),
    )
    draw.polygon([end, (int(left[0]), int(left[1])), (int(right[0]), int(right[1]))], fill=color)


def _callout(
    draw: Any,
    box: tuple[int, int, int, int],
    text: str,
    accent: str,
    font: Any,
) -> None:
    _rounded_rect(draw, box, radius=10, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.rounded_rectangle((box[0], box[1], box[0] + 10, box[3]), radius=10, fill=accent)
    draw.text((box[0] + 22, box[1] + 10), text, fill="#334155", font=font)


def _render_curated_diagram(
    target_architecture: TargetArchitecture,
    node_classes: dict[str, Any],
    blank_class: Any,
    cluster_class: Any,
    edge_class: Any,
    users_class: Any,
    onprem_router_class: Any,
    customer_gateway_class: Any,
    vpc_class: Any,
    public_subnet_class: Any,
    private_subnet_class: Any,
) -> None:
    components = {component.id: component for component in target_architecture.components}
    nodes: dict[str, Any] = {}

    compute_components = _components_in_categories(components, {"compute", "application"})
    data_components = _components_in_categories(components, {"database"})
    storage_components = _components_in_categories(components, {"storage"})
    messaging_components = _components_in_categories(components, {"messaging"})
    has_hybrid = _has_any(
        components,
        [
            "on_premises_network",
            "customer_gateway",
            "aws_direct_connect",
            "aws_direct_connect_gateway",
            "ipsec_vpn_tunnels",
            "transit_vif",
            "aws_site_to_site_vpn",
            "aws_transit_gateway",
            "tgw_route_table",
            "tgw_vpc_attachment",
            "private_route_tables",
        ],
    )
    has_public_entry = _has_any(
        components,
        ["users", "route53", "application_load_balancer", "elastic_load_balancing", "aws_waf"],
    )

    if has_public_entry:
        with cluster_class("Client entry"):
            if "users" in components:
                nodes["users"] = users_class("Users")
            if "route53" in components:
                nodes["route53"] = node_classes["route 53"]("Amazon Route 53")

    if has_hybrid:
        with cluster_class("On-premises"):
            nodes["on_premises_network"] = onprem_router_class("On-premises network")

    with cluster_class("AWS network"):
        if has_hybrid:
            with cluster_class("Hybrid connectivity"):
                if "customer_gateway" in components:
                    nodes["customer_gateway"] = customer_gateway_class("Customer routers\nHA")
                if "aws_direct_connect" in components:
                    nodes["aws_direct_connect"] = node_classes["direct connect"](
                        "Redundant\nDirect Connect\nconnections"
                    )
                if "transit_vif" in components:
                    nodes["transit_vif"] = blank_class("Transit VIFs\nBGP")
                if "ipsec_vpn_tunnels" in components:
                    nodes["ipsec_vpn_tunnels"] = blank_class("2 IPsec tunnels\nBGP")
                if "aws_direct_connect_gateway" in components:
                    nodes["aws_direct_connect_gateway"] = node_classes["direct connect"]("DX Gateway")
                if "aws_site_to_site_vpn" in components:
                    nodes["aws_site_to_site_vpn"] = node_classes["site-to-site vpn"](
                        "AWS Site-to-Site\nVPN attachment"
                    )
                if "aws_transit_gateway" in components:
                    nodes["aws_transit_gateway"] = node_classes["transit gateway"]("Transit Gateway")
                if "tgw_route_table" in components:
                    nodes["tgw_route_table"] = blank_class("Transit Gateway\nroute table")

        with cluster_class("Amazon VPC"):
            nodes["vpc"] = vpc_class("VPC")
            if has_public_entry:
                with cluster_class("Public subnets"):
                    nodes["public_subnets"] = public_subnet_class("Public subnets")
                    if "application_load_balancer" in components:
                        nodes["application_load_balancer"] = node_classes["application load balancer"]("ALB")
                    if "elastic_load_balancing" in components:
                        nodes["elastic_load_balancing"] = node_classes["elastic load balancing"]("ELB")
                    if "aws_waf" in components:
                        nodes["aws_waf"] = node_classes["waf"]("AWS WAF")

            with cluster_class("Private subnets"):
                if "tgw_vpc_attachment" in components:
                    nodes["tgw_vpc_attachment"] = node_classes["transit gateway attachment"](
                        "Transit Gateway\nVPC attachment"
                    )
                if "private_route_tables" in components:
                    nodes["private_route_tables"] = blank_class(
                        "Private subnet\nroute tables"
                    )
                nodes["private_subnets"] = private_subnet_class("Private subnets")
                for component in compute_components:
                    nodes[component.id] = _node_class_for(component.name, node_classes, blank_class)(
                        _short_name(component.name)
                    )
                for component in data_components:
                    nodes[component.id] = _node_class_for(component.name, node_classes, blank_class)(
                        _short_name(component.name)
                    )
                for component in storage_components:
                    nodes[component.id] = _node_class_for(component.name, node_classes, blank_class)(
                        _short_name(component.name)
                    )
                for component in messaging_components:
                    nodes[component.id] = _node_class_for(component.name, node_classes, blank_class)(
                        _short_name(component.name)
                    )

    with cluster_class("Security and operations"):
        for component_id in ("iam", "aws_secrets_manager", "aws_kms", "amazon_cloudwatch", "aws_backup"):
            component = components.get(component_id)
            if component:
                nodes[component_id] = _node_class_for(component.name, node_classes, blank_class)(
                    _short_name(component.name)
                )

    _connect_primary_paths(
        nodes=nodes,
        compute_components=compute_components,
        data_components=data_components,
        storage_components=storage_components,
        messaging_components=messaging_components,
        edge_class=edge_class,
    )


def _connect_primary_paths(
    nodes: dict[str, Any],
    compute_components: list[ArchitectureComponent],
    data_components: list[ArchitectureComponent],
    storage_components: list[ArchitectureComponent],
    messaging_components: list[ArchitectureComponent],
    edge_class: Any,
) -> None:
    _connect(nodes, edge_class, "users", "route53", "DNS")
    ingress_id = _first_present(nodes, ["aws_waf", "application_load_balancer", "elastic_load_balancing"])
    if ingress_id:
        _connect(nodes, edge_class, "route53", ingress_id, "HTTPS")
        for compute in compute_components:
            _connect(nodes, edge_class, ingress_id, compute.id)

    _connect(nodes, edge_class, "on_premises_network", "customer_gateway")
    _connect(nodes, edge_class, "customer_gateway", "aws_direct_connect", "redundant DX")
    _connect(nodes, edge_class, "aws_direct_connect", "transit_vif")
    _connect(nodes, edge_class, "transit_vif", "aws_direct_connect_gateway", "BGP over Transit VIF")
    _connect(nodes, edge_class, "aws_direct_connect_gateway", "aws_transit_gateway", "Associated with Transit Gateway")
    _connect(nodes, edge_class, "customer_gateway", "ipsec_vpn_tunnels")
    _connect(nodes, edge_class, "ipsec_vpn_tunnels", "aws_site_to_site_vpn", "BGP over IPsec VPN")
    _connect(nodes, edge_class, "aws_site_to_site_vpn", "aws_transit_gateway", "VPN attachment")
    _connect(nodes, edge_class, "aws_transit_gateway", "tgw_route_table", "association / propagation")
    _connect(nodes, edge_class, "tgw_route_table", "tgw_vpc_attachment", "VPC attachment")
    _connect(nodes, edge_class, "tgw_vpc_attachment", "private_route_tables")
    _connect(nodes, edge_class, "private_route_tables", "private_subnets", "routes")

    for compute in compute_components:
        _connect(nodes, edge_class, compute.id, "private_subnets", style="dashed")
        for data in data_components:
            _connect(nodes, edge_class, compute.id, data.id)
        for storage in storage_components:
            _connect(nodes, edge_class, compute.id, storage.id)
        for messaging in messaging_components:
            _connect(nodes, edge_class, compute.id, messaging.id)
        _connect(nodes, edge_class, compute.id, "aws_secrets_manager", style="dashed")
        _connect(nodes, edge_class, compute.id, "amazon_cloudwatch", style="dashed")

    for data in data_components:
        _connect(nodes, edge_class, data.id, "aws_kms", style="dashed")
        _connect(nodes, edge_class, data.id, "aws_backup", style="dashed")
    for storage in storage_components:
        _connect(nodes, edge_class, storage.id, "aws_kms", style="dashed")
        _connect(nodes, edge_class, storage.id, "aws_backup", style="dashed")

    _connect(nodes, edge_class, "aws_transit_gateway", "amazon_cloudwatch", style="dashed")


def _connect(
    nodes: dict[str, Any],
    edge_class: Any,
    source_id: str,
    target_id: str,
    label: str = "",
    style: str = "solid",
) -> None:
    source = nodes.get(source_id)
    target = nodes.get(target_id)
    if not source or not target:
        return
    if label or style != "solid":
        source >> edge_class(label=label, style=style) >> target
    else:
        source >> target


def _first_present(nodes: dict[str, Any], component_ids: list[str]) -> str | None:
    for component_id in component_ids:
        if component_id in nodes:
            return component_id
    return None


def _node_class_for(name: str, node_classes: dict[str, Any], fallback: Any) -> Any:
    normalized = name.lower()
    for token, node_class in node_classes.items():
        if token in normalized:
            return node_class
    return fallback


def _components_in_categories(
    components: dict[str, ArchitectureComponent],
    categories: set[str],
) -> list[ArchitectureComponent]:
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
        "aws_direct_connect_gateway",
        "ipsec_vpn_tunnels",
        "transit_vif",
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
        component
        for component_id, component in components.items()
        if component_id not in excluded and component.category in categories
    ]


def _has_any(components: dict[str, ArchitectureComponent], component_ids: list[str]) -> bool:
    return any(component_id in components for component_id in component_ids)


def _short_name(name: str) -> str:
    replacements = {
        "Amazon ": "",
        "AWS ": "",
        "Application ": "",
    }
    shortened = name
    for old, new in replacements.items():
        shortened = shortened.replace(old, new)
    return shortened


def _configure_graphviz_executable() -> None:
    settings = get_settings()
    if not settings.graphviz_dot:
        return

    dot_path = Path(settings.graphviz_dot)
    if not dot_path.exists():
        return

    import os
    import graphviz.backend.dot_command as dot_command

    bin_dir = str(dot_path.parent)
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    if bin_dir not in path_parts:
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    dot_command.DOT_BINARY = dot_path


def _generate_fallback_png(
    target_architecture: TargetArchitecture,
    renderer_note: str,
) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    components = target_architecture.components[:16]
    width = 1400
    row_height = 92
    height = max(720, 190 + row_height * max(1, len(components)))
    image = Image.new("RGB", (width, height), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    title_font = _font(size=32, bold=True)
    subtitle_font = _font(size=17)
    node_font = _font(size=18, bold=True)
    body_font = _font(size=14)

    draw.rectangle((0, 0, width, 110), fill="#10233f")
    draw.text(
        (42, 28),
        f"Proposed {_provider_label(target_architecture.provider)} Architecture",
        fill="#ffffff",
        font=title_font,
    )
    draw.text((42, 70), renderer_note, fill="#c9d7ea", font=subtitle_font)

    category_colors = {
        "external": "#e8eef8",
        "networking": "#dbeafe",
        "compute": "#dcfce7",
        "application": "#dcfce7",
        "database": "#fef3c7",
        "storage": "#ede9fe",
        "security": "#fee2e2",
        "observability": "#e0f2fe",
        "messaging": "#fae8ff",
        "resilience": "#ecfccb",
    }

    left_x = 70
    right_x = 760
    y = 150
    for index, component in enumerate(components):
        column_x = left_x if index % 2 == 0 else right_x
        if index > 0 and index % 2 == 0:
            y += row_height
        box = (column_x, y, column_x + 560, y + 64)
        color = category_colors.get(component.category or "", "#ffffff")
        draw.rounded_rectangle(box, radius=8, fill=color, outline="#9fb1c7", width=2)
        draw.text((box[0] + 16, box[1] + 10), component.name, fill="#10233f", font=node_font)
        meta = f"{component.category or 'component'} | {component.confidence:.0%}"
        draw.text((box[0] + 16, box[1] + 38), meta, fill="#475569", font=body_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _provider_key(provider: str | None) -> str:
    normalized = (provider or "").lower()
    if "aws" in normalized or "amazon" in normalized:
        return "aws"
    if "azure" in normalized:
        return "azure"
    if "gcp" in normalized or "google" in normalized:
        return "gcp"
    return normalized or "target"


def _provider_label(provider: str | None) -> str:
    key = _provider_key(provider)
    if key == "aws":
        return "AWS"
    if key == "azure":
        return "Azure"
    if key == "gcp":
        return "Google Cloud"
    return provider or "Target Cloud"


def _font(size: int, bold: bool = False) -> Any:
    from PIL import ImageFont

    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()
