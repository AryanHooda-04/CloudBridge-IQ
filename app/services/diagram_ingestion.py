"""Input file ingestion for architecture diagrams."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from app.config import get_settings
from app.schemas import DiagramIngestionResult


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


def ingest_diagram(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
) -> DiagramIngestionResult:
    """Extract model-compatible content from an uploaded architecture diagram."""

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    suffix = Path(filename or "").suffix.lower()
    if suffix in SUPPORTED_PDF_EXTENSIONS or content_type == "application/pdf":
        return _ingest_pdf(file_bytes, filename, content_type)

    if suffix in SUPPORTED_IMAGE_EXTENSIONS or (content_type or "").startswith("image/"):
        return _ingest_image(file_bytes, filename, content_type)

    raise ValueError(
        "Unsupported file type. Upload an image file or a PDF architecture diagram."
    )


def _ingest_image(
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
) -> DiagramIngestionResult:
    with Image.open(BytesIO(file_bytes)) as image:
        image.load()
        normalized_bytes, width, height = _normalize_image_for_model(image)

    metadata = {
        "size_bytes": len(file_bytes),
        "image_width": width,
        "image_height": height,
        "model_image_mime_type": "image/png",
        "local_text_extraction": "disabled",
    }

    return DiagramIngestionResult(
        filename=filename,
        content_type=content_type,
        file_kind="image",
        text="",
        image_base64=base64.b64encode(normalized_bytes).decode("utf-8"),
        image_mime_type="image/png",
        metadata=metadata,
    )


def _ingest_pdf(
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
) -> DiagramIngestionResult:
    reader = PdfReader(BytesIO(file_bytes))
    page_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_text.append(text.strip())

    extracted_text = "\n\n".join(page_text)
    metadata = {
        "size_bytes": len(file_bytes),
        "page_count": len(reader.pages),
        "text_character_count": len(extracted_text),
    }

    image_base64: str | None = None
    image_mime_type: str | None = None

    if len(extracted_text.strip()) < 80:
        pdf_image_result = _pdf_to_images(file_bytes)
        metadata.update(pdf_image_result["metadata"])
        image_base64 = pdf_image_result["image_base64"]
        image_mime_type = pdf_image_result["image_mime_type"]

    metadata["final_text_character_count"] = len(extracted_text)
    if len(extracted_text.strip()) < 50 and not image_base64:
        metadata["warning"] = "PDF text extraction was sparse and PDF-to-image conversion was unavailable or failed."

    return DiagramIngestionResult(
        filename=filename,
        content_type=content_type,
        file_kind="pdf",
        text=extracted_text,
        image_base64=image_base64,
        image_mime_type=image_mime_type,
        metadata=metadata,
    )


def _normalize_image_for_model(image: Image.Image) -> tuple[bytes, int, int]:
    normalized = image.convert("RGB")
    normalized.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    normalized.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue(), normalized.width, normalized.height


def _pdf_to_images(file_bytes: bytes) -> dict[str, object]:
    result: dict[str, object] = {
        "image_base64": None,
        "image_mime_type": None,
        "metadata": {
            "pdf_image_conversion_attempted": True,
            "pdf_image_pages_processed": 0,
        },
    }
    try:
        from pdf2image import convert_from_bytes

        settings = get_settings()
        pages = convert_from_bytes(
            file_bytes,
            dpi=180,
            first_page=1,
            last_page=3,
            poppler_path=settings.poppler_path,
        )
        first_page_bytes: bytes | None = None

        for index, page_image in enumerate(pages):
            normalized_bytes, _, _ = _normalize_image_for_model(page_image)
            if index == 0:
                first_page_bytes = normalized_bytes
            result["metadata"]["pdf_image_pages_processed"] = index + 1

        if first_page_bytes:
            result["image_base64"] = base64.b64encode(first_page_bytes).decode("utf-8")
            result["image_mime_type"] = "image/png"
        return result
    except Exception as exc:
        result["metadata"]["pdf_image_conversion_error"] = str(exc)
        return result
