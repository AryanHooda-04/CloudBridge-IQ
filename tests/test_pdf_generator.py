from io import BytesIO

from PIL import Image
from pypdf import PdfReader

from app.main import _pdf_report_response
from app.schemas import PdfReportRequest, TargetArchitecture
from app.services.pdf_generator import markdown_to_pdf_bytes


def make_test_png() -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (80, 40), "#f8fafc")
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_markdown_to_pdf_bytes_generates_pdf():
    pdf_bytes = markdown_to_pdf_bytes(
        """# Migration Assessment Snapshot

## Decision

**Conditionally Recommended** (78% confidence)

## Service Moves

| Source | Recommended AWS target | Why | Confidence |
|---|---|---|---|
| Azure App Service | AWS Elastic Beanstalk | Managed app hosting fit. | 86% |
"""
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_markdown_to_pdf_skips_mermaid_diagram_by_default():
    pdf_bytes = markdown_to_pdf_bytes(
        """# Migration Assessment Snapshot

## 7. AWS Architecture Diagram

```mermaid
graph TD
    A --> B
```
""",
        rendered_diagram_png=make_test_png(),
        rendered_diagram_title="Generated AWS Architecture Diagram",
    )

    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf_bytes)).pages)

    assert "Generated AWS Architecture Diagram" in text
    assert "Rendered Mermaid Architecture Diagram" not in text
    assert "graph TD" not in text


def test_pdf_generator_handles_wide_long_tables():
    rows = [
        "# Cloud Migration Assessment Report",
        "",
        "## 1. Executive Summary",
        "This report intentionally contains wide tables and long text for PDF export.",
        "",
        "## 4. Source-to-Target Cloud Service Mapping",
        "| Source Service | Target Service | Reasoning | Confidence | Owner | Decision | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for index in range(70):
        rows.append(
            "| Source "
            + str(index)
            + " | Target "
            + str(index)
            + " | "
            + ("Long rationale with networking, security, cost, and operational details. " * 10)
            + " | 0.82 | Architect | Open | "
            + ("Review note. " * 14)
            + " |"
        )

    pdf = markdown_to_pdf_bytes(
        "\n".join(rows),
        source_provider="aws",
        target_provider="azure",
    )

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_pdf_report_response_skips_optional_diagram_render_failure(monkeypatch):
    async def run_check():
        def fail_renderer(_target_architecture):
            raise RuntimeError("diagram renderer unavailable")

        monkeypatch.setattr("app.main.generate_aws_diagram_png", fail_renderer)
        response = await _pdf_report_response(
            PdfReportRequest(
                filename="fallback.pdf",
                markdown_report="# Migration Assessment\n\nPDF export should still work.",
                target_architecture=TargetArchitecture(
                    provider="aws",
                    summary="Fallback architecture",
                    components=[],
                    relationships=[],
                ),
                include_rendered_diagram=True,
            )
        )

        assert response.media_type == "application/pdf"
        assert response.body.startswith(b"%PDF")

    import asyncio

    asyncio.run(run_check())
