from io import BytesIO

from PIL import Image, ImageDraw

from app.services.diagram_ingestion import ingest_diagram


def test_image_ingestion_normalizes_image_for_vision():
    image = Image.new("RGB", (420, 160), "white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 60), "Azure App Service", fill="black")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    result = ingest_diagram(buffer.getvalue(), "architecture.png", "image/png")

    assert result.file_kind == "image"
    assert result.image_base64
    assert result.image_mime_type == "image/png"
    assert result.metadata["image_width"] == 420
    assert result.metadata["local_text_extraction"] == "disabled"
