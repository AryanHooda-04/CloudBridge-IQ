from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_docker_image_includes_bundled_demo_samples():
    dockerfile = (ROOT_DIR / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY samples/architecture_diagrams ./samples/architecture_diagrams" in dockerfile


def test_dockerignore_allows_bundled_demo_samples():
    dockerignore = (ROOT_DIR / ".dockerignore").read_text(encoding="utf-8")

    assert "samples/*" in dockerignore
    assert "!samples/architecture_diagrams/" in dockerignore
    assert "!samples/architecture_diagrams/**" in dockerignore
