from fastapi.testclient import TestClient

from app.main import app


def test_demo_samples_include_metadata_and_image_urls():
    client = TestClient(app)

    response = client.get("/api/demo-samples")

    assert response.status_code == 200
    samples = response.json()
    assert len(samples) == 5
    first = samples[0]
    assert first["id"] == "azure-enterprise-webapp"
    assert first["source_provider"] == "azure"
    assert first["target_provider"] == "aws"
    assert first["architecture_pattern"] == "web-application"
    assert first["migration_intent"]
    assert first["goals"] == ["modernization", "reduce operations", "improve availability"]
    assert first["image_url"] == "/api/demo-samples/azure-enterprise-webapp/image"


def test_demo_sample_image_endpoint_serves_png():
    client = TestClient(app)

    response = client.get("/api/demo-samples/azure-enterprise-webapp/image")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")


def test_unknown_demo_sample_returns_404():
    client = TestClient(app)

    response = client.get("/api/demo-samples/not-a-sample/image")

    assert response.status_code == 404
