from io import BytesIO

from PIL import Image
from pypdf import PdfReader

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
