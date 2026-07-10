"""PDF export helpers for assessment reports."""

from __future__ import annotations

import html
import re
from io import BytesIO


MAX_PDF_LINES = 1400
MAX_TABLE_ROWS = 36
MAX_TABLE_CELL_CHARS = 420
MAX_PARAGRAPH_CHARS = 1800
MAX_CODE_CHARS = 3600


def markdown_to_pdf_bytes(
    markdown: str,
    *,
    include_mermaid_diagram: bool = False,
    mermaid_diagram_png: bytes | None = None,
    mermaid_diagram_title: str = "Rendered Mermaid Architecture Diagram",
    rendered_diagram_png: bytes | None = None,
    rendered_diagram_title: str = "Generated Architecture Diagram",
    source_provider: str | None = None,
    target_provider: str | None = None,
) -> bytes:
    """Convert the concise Markdown report into a readable PDF document."""

    markdown = _strip_pdf_diagram_sections(markdown)
    include_mermaid_diagram = False
    mermaid_diagram_png = None
    rendered_diagram_png = None

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Image as ReportLabImage,
            Paragraph,
            Preformatted,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError("PDF export requires the reportlab package.") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.62 * inch,
        title="CloudBridge IQ Migration Assessment",
    )
    base_styles = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "AssessmentTitle",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=14,
            textColor=colors.HexColor("#111827"),
        ),
        "section": ParagraphStyle(
            "AssessmentSection",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.HexColor("#1f3b63"),
        ),
        "body": ParagraphStyle(
            "AssessmentBody",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=13,
            spaceAfter=6,
            textColor=colors.HexColor("#263548"),
        ),
        "table": ParagraphStyle(
            "AssessmentTable",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10,
            textColor=colors.HexColor("#263548"),
        ),
        "code": ParagraphStyle(
            "AssessmentCode",
            parent=base_styles["Code"],
            fontName="Courier",
            fontSize=7.4,
            leading=9,
            textColor=colors.HexColor("#111827"),
        ),
        "provider": ParagraphStyle(
            "AssessmentProvider",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.4,
            leading=10,
            alignment=1,
            textColor=colors.HexColor("#111827"),
        ),
    }

    story: list = []
    table_rows: list[str] = []
    code_lines: list[str] = []
    in_code = False
    code_language = ""
    mermaid_diagram_added = False
    rendered_diagram_added = False
    provider_route_added = False

    def provider_key(provider: str | None) -> str:
        value = (provider or "unknown").lower()
        if "azure" in value:
            return "azure"
        if "gcp" in value or "google" in value:
            return "gcp"
        if "aws" in value or "amazon" in value:
            return "aws"
        if value == "auto":
            return "auto"
        return "neutral"

    def provider_label(provider: str | None) -> str:
        key = provider_key(provider)
        if key == "azure":
            return "Azure"
        if key == "gcp":
            return "GCP"
        if key == "aws":
            return "AWS"
        if key == "auto":
            return "Auto"
        return (provider or "Unknown").title()

    def provider_colors(provider: str | None) -> tuple[str, str]:
        key = provider_key(provider)
        if key == "azure":
            return "#e8f3ff", "#0078d4"
        if key == "gcp":
            return "#eef6ff", "#1a73e8"
        if key == "aws":
            return "#fff4df", "#ff9900"
        return "#f2f5f8", "#64748b"

    def provider_cell(provider: str | None) -> Paragraph:
        return Paragraph(provider_label(provider), styles["provider"])

    def add_provider_route() -> None:
        nonlocal provider_route_added
        if provider_route_added or not (source_provider or target_provider):
            return
        source_bg, source_border = provider_colors(source_provider)
        target_bg, target_border = provider_colors(target_provider)
        route = Table(
            [[provider_cell(source_provider), Paragraph("to", styles["provider"]), provider_cell(target_provider)]],
            colWidths=[1.15 * inch, 0.32 * inch, 1.15 * inch],
            hAlign="LEFT",
        )
        route.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(source_bg)),
                    ("BACKGROUND", (2, 0), (2, 0), colors.HexColor(target_bg)),
                    ("BOX", (0, 0), (0, 0), 0.8, colors.HexColor(source_border)),
                    ("BOX", (2, 0), (2, 0), 0.8, colors.HexColor(target_border)),
                    ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#667085")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([route, Spacer(1, 10)])
        provider_route_added = True

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return
        raw_rows: list[list[str]] = []
        for row in table_rows:
            if re.match(r"^\|\s*-+", row):
                continue
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if cells:
                raw_rows.append(cells)
        if raw_rows:
            column_count = max(len(row) for row in raw_rows)
            visible_rows = raw_rows[:MAX_TABLE_ROWS]
            rows = [
                [
                    Paragraph(_inline(_truncate_text(cell, MAX_TABLE_CELL_CHARS)), styles["table"])
                    for cell in row + [""] * (column_count - len(row))
                ]
                for row in visible_rows
            ]
            table = Table(
                rows,
                repeatRows=1,
                hAlign="LEFT",
                colWidths=_column_widths(column_count, doc.width),
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f8")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cfd8e3")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.extend([table, Spacer(1, 8)])
            omitted = max(0, len(raw_rows) - len(visible_rows))
            if omitted:
                story.extend(
                    [
                        Paragraph(
                            _inline(
                                f"{omitted} additional table rows were omitted from the PDF export. "
                                "Use Markdown export for the full machine-readable detail."
                            ),
                            styles["body"],
                        ),
                        Spacer(1, 6),
                    ]
                )
        table_rows = []

    def add_png_section(png_bytes: bytes | None, title: str, max_height: float) -> bool:
        if not png_bytes:
            return False

        image = ReportLabImage(BytesIO(png_bytes))
        scale = min(
            doc.width / image.imageWidth,
            max_height / image.imageHeight,
            1,
        )
        image.drawWidth = image.imageWidth * scale
        image.drawHeight = image.imageHeight * scale
        story.extend(
            [
                Spacer(1, 6),
                Paragraph(_inline(title), styles["section"]),
                image,
                Spacer(1, 10),
            ]
        )
        return True

    def add_mermaid_diagram() -> bool:
        nonlocal mermaid_diagram_added
        if not include_mermaid_diagram:
            return False
        if mermaid_diagram_added:
            return False
        mermaid_diagram_added = add_png_section(
            mermaid_diagram_png,
            mermaid_diagram_title,
            4.5 * inch,
        )
        return mermaid_diagram_added

    def add_mermaid_source_diagram(source: str) -> bool:
        nonlocal mermaid_diagram_added
        if not include_mermaid_diagram:
            return False
        if mermaid_diagram_added:
            return False
        png_bytes = _render_mermaid_source_png(source)
        mermaid_diagram_added = add_png_section(
            png_bytes,
            mermaid_diagram_title,
            4.5 * inch,
        )
        return mermaid_diagram_added

    def add_rendered_diagram() -> None:
        nonlocal rendered_diagram_added
        if rendered_diagram_added:
            return
        rendered_diagram_added = add_png_section(
            rendered_diagram_png,
            rendered_diagram_title,
            5.4 * inch,
        )

    def flush_code(language: str = "") -> None:
        nonlocal code_lines
        if not code_lines:
            return
        if language == "mermaid":
            mermaid_source = "\n".join(code_lines)
            if include_mermaid_diagram and not add_mermaid_diagram() and not add_mermaid_source_diagram(mermaid_source):
                story.extend(
                    [
                        Preformatted(mermaid_source, styles["code"]),
                        Spacer(1, 8),
                    ]
                )
            add_rendered_diagram()
        else:
            code_text = _truncate_text("\n".join(code_lines), MAX_CODE_CHARS)
            story.extend(
                [
                    Preformatted(code_text, styles["code"]),
                    Spacer(1, 8),
                ]
            )
        code_lines = []

    for line in _bounded_lines(markdown):
        if line.startswith("```"):
            flush_table()
            if in_code:
                flush_code(code_language)
                in_code = False
                code_language = ""
            else:
                in_code = True
                code_language = line[3:].strip().lower()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith("|"):
            table_rows.append(line)
            continue

        flush_table()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(_inline(stripped[2:]), styles["title"]))
            add_provider_route()
        elif stripped.startswith("## "):
            story.append(Paragraph(_inline(stripped[3:]), styles["section"]))
        elif stripped.startswith("### "):
            story.append(Paragraph(_inline(stripped[4:]), styles["section"]))
        elif stripped.startswith("- "):
            story.append(
                Paragraph("- " + _inline(_truncate_text(stripped[2:], MAX_PARAGRAPH_CHARS)), styles["body"])
            )
        else:
            story.append(Paragraph(_inline(_truncate_text(stripped, MAX_PARAGRAPH_CHARS)), styles["body"]))

    flush_table()
    flush_code(code_language)
    add_mermaid_diagram()
    add_rendered_diagram()

    def draw_brand_frame(canvas, document) -> None:
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(colors.HexColor("#10233f"))
        canvas.rect(0, height - 0.42 * inch, width, 0.42 * inch, fill=1, stroke=0)
        draw_cloudbridge_mark(canvas, 0.55 * inch, height - 0.34 * inch, 0.24 * inch)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(0.85 * inch, height - 0.2 * inch, "CloudBridge IQ")
        canvas.setFont("Helvetica", 7.4)
        canvas.drawString(0.85 * inch, height - 0.31 * inch, "Cloud Migration Assessment")
        if source_provider or target_provider:
            badge_y = height - 0.32 * inch
            target_x = width - 1.48 * inch
            source_x = target_x - 1.22 * inch
            draw_provider_badge(canvas, source_x, badge_y, source_provider)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawCentredString(target_x - 0.13 * inch, badge_y + 0.06 * inch, "to")
            draw_provider_badge(canvas, target_x, badge_y, target_provider)
        else:
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(width - 0.55 * inch, height - 0.27 * inch, "Enterprise Review Pack")
        canvas.setFillColor(colors.HexColor("#667085"))
        canvas.drawRightString(width - 0.55 * inch, 0.34 * inch, f"Page {document.page}")
        canvas.restoreState()

    def draw_cloudbridge_mark(canvas, x: float, y: float, size: float) -> None:
        canvas.setFillColor(colors.HexColor("#10233f"))
        canvas.setStrokeColor(colors.HexColor("#ffffff"))
        canvas.roundRect(x, y, size, size, 4, stroke=1, fill=1)
        canvas.setLineWidth(1.1)
        canvas.setStrokeColor(colors.white)
        canvas.arc(x + size * 0.18, y + size * 0.28, x + size * 0.82, y + size * 0.84, 20, 140)
        canvas.setFillColor(colors.HexColor("#ff9900"))
        canvas.circle(x + size * 0.24, y + size * 0.36, size * 0.1, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#1a73e8"))
        canvas.circle(x + size * 0.5, y + size * 0.58, size * 0.11, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#34a853"))
        canvas.circle(x + size * 0.76, y + size * 0.36, size * 0.1, stroke=0, fill=1)
        sparkle = canvas.beginPath()
        sparkle.moveTo(x + size * 0.5, y + size * 0.8)
        sparkle.lineTo(x + size * 0.55, y + size * 0.67)
        sparkle.lineTo(x + size * 0.68, y + size * 0.62)
        sparkle.lineTo(x + size * 0.55, y + size * 0.56)
        sparkle.lineTo(x + size * 0.5, y + size * 0.43)
        sparkle.lineTo(x + size * 0.45, y + size * 0.56)
        sparkle.lineTo(x + size * 0.32, y + size * 0.62)
        sparkle.lineTo(x + size * 0.45, y + size * 0.67)
        sparkle.close()
        canvas.setFillColor(colors.white)
        canvas.drawPath(sparkle, stroke=0, fill=1)

    def draw_provider_badge(canvas, x: float, y: float, provider: str | None) -> None:
        key = provider_key(provider)
        bg, border = provider_colors(provider)
        canvas.setFillColor(colors.HexColor(bg))
        canvas.setStrokeColor(colors.HexColor(border))
        canvas.roundRect(x, y, 0.98 * inch, 0.22 * inch, 4, stroke=1, fill=1)
        draw_provider_mark(canvas, x + 0.05 * inch, y + 0.035 * inch, key)
        canvas.setFillColor(colors.HexColor("#111827"))
        canvas.setFont("Helvetica-Bold", 7.6)
        canvas.drawString(x + 0.34 * inch, y + 0.065 * inch, provider_label(provider))

    def draw_provider_mark(canvas, x: float, y: float, key: str) -> None:
        if key == "aws":
            canvas.setFillColor(colors.HexColor("#101828"))
            canvas.roundRect(x, y, 0.24 * inch, 0.15 * inch, 2, stroke=0, fill=1)
            canvas.setStrokeColor(colors.HexColor("#ff9900"))
            canvas.setLineWidth(0.75)
            canvas.arc(x + 0.045 * inch, y + 0.015 * inch, x + 0.205 * inch, y + 0.11 * inch, 205, 120)
            canvas.setStrokeColor(colors.white)
            canvas.line(x + 0.055 * inch, y + 0.095 * inch, x + 0.19 * inch, y + 0.095 * inch)
            canvas.line(x + 0.08 * inch, y + 0.045 * inch, x + 0.17 * inch, y + 0.045 * inch)
            return

        if key == "azure":
            path = canvas.beginPath()
            path.moveTo(x + 0.09 * inch, y + 0.155 * inch)
            path.lineTo(x + 0.17 * inch, y + 0.155 * inch)
            path.lineTo(x + 0.10 * inch, y)
            path.lineTo(x + 0.02 * inch, y)
            path.close()
            canvas.setFillColor(colors.HexColor("#0078d4"))
            canvas.drawPath(path, stroke=0, fill=1)
            path = canvas.beginPath()
            path.moveTo(x + 0.17 * inch, y + 0.155 * inch)
            path.lineTo(x + 0.27 * inch, y)
            path.lineTo(x + 0.16 * inch, y)
            path.lineTo(x + 0.11 * inch, y + 0.055 * inch)
            path.close()
            canvas.setFillColor(colors.HexColor("#50a7f2"))
            canvas.drawPath(path, stroke=0, fill=1)
            return

        if key == "gcp":
            canvas.setLineWidth(1.6)
            canvas.setStrokeColor(colors.HexColor("#1a73e8"))
            canvas.arc(x + 0.04 * inch, y + 0.01 * inch, x + 0.25 * inch, y + 0.16 * inch, 185, 115)
            canvas.setStrokeColor(colors.HexColor("#ea4335"))
            canvas.line(x + 0.07 * inch, y + 0.135 * inch, x + 0.16 * inch, y + 0.16 * inch)
            canvas.setStrokeColor(colors.HexColor("#fbbc04"))
            canvas.arc(x + 0.155 * inch, y + 0.015 * inch, x + 0.29 * inch, y + 0.135 * inch, 300, 100)
            canvas.setStrokeColor(colors.HexColor("#34a853"))
            canvas.arc(x + 0.005 * inch, y + 0.015 * inch, x + 0.13 * inch, y + 0.13 * inch, 125, 135)
            return

        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.circle(x + 0.1 * inch, y + 0.08 * inch, 0.045 * inch, stroke=0, fill=1)
        canvas.setStrokeColor(colors.HexColor("#64748b"))
        canvas.setLineWidth(0.9)
        canvas.line(x + 0.16 * inch, y + 0.11 * inch, x + 0.26 * inch, y + 0.11 * inch)
        canvas.line(x + 0.16 * inch, y + 0.075 * inch, x + 0.26 * inch, y + 0.075 * inch)
        canvas.line(x + 0.16 * inch, y + 0.04 * inch, x + 0.26 * inch, y + 0.04 * inch)

    doc.build(story, onFirstPage=draw_brand_frame, onLaterPages=draw_brand_frame)
    return buffer.getvalue()


def _inline(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escaped)


def _strip_pdf_diagram_sections(markdown: str) -> str:
    """Keep PDF export report-only by removing diagram-heavy markdown sections."""

    without_mermaid_blocks = re.sub(
        r"```mermaid[\s\S]*?```",
        "",
        markdown or "",
        flags=re.IGNORECASE,
    )
    kept: list[str] = []
    skipping_diagram_section = False
    for line in without_mermaid_blocks.splitlines():
        stripped = line.strip()
        if re.match(
            r"^##\s+(?:\d+\.\s*)?(?:AWS|Azure|GCP|Google Cloud|Target|Generated|Rendered)?\s*Architecture Diagram\b",
            stripped,
            flags=re.IGNORECASE,
        ):
            skipping_diagram_section = True
            continue
        if skipping_diagram_section and stripped.startswith("## "):
            skipping_diagram_section = False
        if not skipping_diagram_section:
            kept.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


def _column_widths(column_count: int, available_width: float) -> list[float] | None:
    if column_count <= 0:
        return None
    if column_count == 4:
        ratios = [0.22, 0.24, 0.42, 0.12]
    elif column_count == 5:
        ratios = [0.18, 0.2, 0.32, 0.1, 0.2]
    else:
        return [available_width / column_count] * column_count
    return [available_width * ratio for ratio in ratios]


def _bounded_lines(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    if len(lines) <= MAX_PDF_LINES:
        return lines
    omitted = len(lines) - MAX_PDF_LINES
    return lines[:MAX_PDF_LINES] + [
        "",
        f"_PDF export truncated {omitted} additional lines. Use Markdown export for the complete report._",
    ]


def _render_mermaid_source_png(source: str) -> bytes | None:
    """Render a compact flowchart image directly from Mermaid source.

    This intentionally supports the flowchart subset generated by this app. It
    keeps PDF export independent from browser-side Mermaid/CDN rendering.
    """

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    nodes, edges = _parse_mermaid_flowchart(source)
    if not nodes:
        return None

    max_nodes = 30
    max_edges = 42
    visible_node_ids = list(nodes)[:max_nodes]
    visible_nodes = {node_id: nodes[node_id] for node_id in visible_node_ids}
    visible_edges = [
        edge
        for edge in edges
        if edge[0] in visible_nodes and edge[1] in visible_nodes
    ][:max_edges]

    ranks = _rank_mermaid_nodes(visible_nodes, visible_edges)
    columns: dict[int, list[str]] = {}
    for node_id in visible_node_ids:
        columns.setdefault(ranks.get(node_id, 0), []).append(node_id)

    ordered_ranks = sorted(columns)
    column_count = max(1, len(ordered_ranks))
    max_rows = max((len(items) for items in columns.values()), default=1)
    width = min(2200, max(900, column_count * 245 + 110))
    height = min(1600, max(420, max_rows * 112 + 130))

    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    title_font = _load_image_font(22, bold=True)
    label_font = _load_image_font(17, bold=True)
    meta_font = _load_image_font(12)
    edge_font = _load_image_font(11)

    draw.rectangle((0, 0, width, 58), fill="#10233f")
    draw.text((34, 17), "Rendered Mermaid Architecture Diagram", fill="#ffffff", font=title_font)

    node_width = 178
    node_height = 62
    top = 96
    left = 42
    usable_width = max(1, width - left * 2 - node_width)
    col_gap = usable_width / max(1, column_count - 1)
    positions: dict[str, tuple[float, float, float, float]] = {}

    palette = ["#e8f3ff", "#fff7e8", "#eefaf2", "#f4efff", "#fff4f2", "#eef6ff"]
    borders = ["#8fb7de", "#d39b45", "#77b98a", "#a88be0", "#dc8d84", "#77abc9"]

    for col_index, rank in enumerate(ordered_ranks):
        node_ids = columns[rank]
        row_gap = (height - top - 76 - node_height) / max(1, len(node_ids) - 1)
        x = left + col_index * col_gap
        for row_index, node_id in enumerate(node_ids):
            y = top + row_index * max(88, row_gap)
            x1, y1 = x, y
            x2, y2 = x + node_width, y + node_height
            positions[node_id] = (x1, y1, x2, y2)
            color_index = col_index % len(palette)
            draw.rounded_rectangle(
                (x1, y1, x2, y2),
                radius=10,
                fill=palette[color_index],
                outline=borders[color_index],
                width=2,
            )
            label_lines = _wrap_image_text(visible_nodes[node_id], label_font, node_width - 22, draw)
            text_y = y1 + 13 if len(label_lines) == 1 else y1 + 8
            for line in label_lines[:2]:
                line_width = draw.textlength(line, font=label_font)
                draw.text(
                    (x1 + (node_width - line_width) / 2, text_y),
                    line,
                    fill="#18212f",
                    font=label_font,
                )
                text_y += 20
            draw.text(
                (x1 + 12, y2 - 18),
                _truncate_text(node_id.replace("_", " "), 25),
                fill="#5f6f85",
                font=meta_font,
            )

    for source_id, target_id, label in visible_edges:
        if source_id not in positions or target_id not in positions:
            continue
        sx1, sy1, sx2, sy2 = positions[source_id]
        tx1, ty1, tx2, ty2 = positions[target_id]
        start = (sx2, (sy1 + sy2) / 2)
        end = (tx1, (ty1 + ty2) / 2)
        if start[0] <= end[0]:
            mid_x = start[0] + max(28, (end[0] - start[0]) / 2)
            points = [start, (mid_x, start[1]), (mid_x, end[1]), end]
        else:
            offset = 34
            points = [
                start,
                (start[0] + offset, start[1]),
                (start[0] + offset, end[1] + 22),
                (end[0] - offset, end[1] + 22),
                (end[0] - offset, end[1]),
                end,
            ]
        draw.line(points, fill="#50677f", width=2, joint="curve")
        _draw_arrowhead(draw, points[-2], points[-1], "#50677f")
        if label:
            label_text = _truncate_text(label, 28)
            label_x = (points[0][0] + points[-1][0]) / 2
            label_y = (points[0][1] + points[-1][1]) / 2 - 16
            text_width = draw.textlength(label_text, font=edge_font)
            draw.rectangle(
                (label_x - text_width / 2 - 4, label_y - 2, label_x + text_width / 2 + 4, label_y + 13),
                fill="#ffffff",
            )
            draw.text((label_x - text_width / 2, label_y), label_text, fill="#334155", font=edge_font)

    omitted_nodes = max(0, len(nodes) - len(visible_nodes))
    omitted_edges = max(0, len(edges) - len(visible_edges))
    if omitted_nodes or omitted_edges:
        note = f"Simplified for PDF: {omitted_nodes} nodes and {omitted_edges} relationships not shown."
        draw.text((34, height - 34), note, fill="#667085", font=meta_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _parse_mermaid_flowchart(source: str) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []

    def clean_label(value: str) -> str:
        return value.strip().strip('"').strip("'").replace("<br/>", " ").replace("<br>", " ")

    def register_node(token: str) -> str | None:
        token = token.strip()
        match = re.search(r"\b([A-Za-z][A-Za-z0-9_]*)\b", token)
        if not match:
            return None
        node_id = match.group(1)
        label_match = re.search(r'\[\s*"?([^\]"]+)"?\s*\]', token)
        if not label_match:
            label_match = re.search(r'\(\s*"?([^)\"]+)"?\s*\)', token)
        if not label_match:
            label_match = re.search(r'\{\s*"?([^}\"]+)"?\s*\}', token)
        nodes.setdefault(node_id, clean_label(label_match.group(1)) if label_match else node_id.replace("_", " ").title())
        return node_id

    for raw_line in source.splitlines():
        line = raw_line.strip().rstrip(";")
        if not line or line.startswith("%") or line.lower().startswith("graph "):
            continue
        for node_match in re.finditer(
            r'\b([A-Za-z][A-Za-z0-9_]*)\s*(?:\[\s*"?([^\]"]+)"?\s*\]|\(\s*"?([^)\"]+)"?\s*\)|\{\s*"?([^}\"]+)"?\s*\})',
            line,
        ):
            node_id = node_match.group(1)
            label = next((group for group in node_match.groups()[1:] if group), None)
            if label:
                nodes[node_id] = clean_label(label)

        edge_match = re.search(r"(.+?)\s*[-.]+(?:>|x|o)?(?:\|([^|]+)\|)?\s*(.+)$", line)
        if not edge_match:
            register_node(line)
            continue

        source_id = register_node(edge_match.group(1))
        target_id = register_node(edge_match.group(3))
        if source_id and target_id:
            edges.append((source_id, target_id, clean_label(edge_match.group(2) or "")))

    return nodes, edges


def _rank_mermaid_nodes(
    nodes: dict[str, str],
    edges: list[tuple[str, str, str]],
) -> dict[str, int]:
    ranks = {node_id: 0 for node_id in nodes}
    for _ in range(min(len(nodes), 12)):
        changed = False
        for source_id, target_id, _ in edges:
            next_rank = min(7, ranks.get(source_id, 0) + 1)
            if next_rank > ranks.get(target_id, 0):
                ranks[target_id] = next_rank
                changed = True
        if not changed:
            break
    return ranks


def _load_image_font(size: int, *, bold: bool = False):
    from PIL import ImageFont

    candidates = ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_image_text(text: str, font, max_width: int, draw) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [str(text)]


def _truncate_text(value: str, limit: int) -> str:
    text = str(value)
    return text if len(text) <= limit else f"{text[: limit - 3].rstrip()}..."


def _draw_arrowhead(draw, previous: tuple[float, float], end: tuple[float, float], color: str) -> None:
    import math

    angle = math.atan2(end[1] - previous[1], end[0] - previous[0])
    size = 9
    points = [
        end,
        (
            end[0] - size * math.cos(angle - math.pi / 6),
            end[1] - size * math.sin(angle - math.pi / 6),
        ),
        (
            end[0] - size * math.cos(angle + math.pi / 6),
            end[1] - size * math.sin(angle + math.pi / 6),
        ),
    ]
    draw.polygon(points, fill=color)
