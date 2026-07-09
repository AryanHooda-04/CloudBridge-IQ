from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.validator_bridge import BridgeSettings, _require_token, health, router


def test_validator_routes_are_mounted_on_router() -> None:
    paths = {route.path for route in router.routes}
    assert {"/health", "/probe", "/check", "/validate", "/evaluate"}.issubset(paths)


def test_validator_health_is_available_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VALIDATOR_TOKEN", raising=False)
    payload = health()
    assert payload["ok"] is True
    assert payload["service"] == "cloudbridge-citrix-validator"
    assert payload["auth_required"] is False


def test_validator_probe_requires_token_when_configured() -> None:
    settings = BridgeSettings(
        openai_api_key="test-key",
        validator_token="secret",
        openai_endpoint="https://example.invalid/v1/responses",
        default_model="gpt-4.1-mini",
        timeout_sec=1,
        max_image_bytes=1024,
    )
    with pytest.raises(HTTPException) as exc_info:
        _require_token(settings, None)
    assert exc_info.value.status_code == 401
