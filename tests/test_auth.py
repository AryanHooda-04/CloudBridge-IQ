import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings
from app.schemas import AuthLoginRequest
from app.services.auth import authenticate_user, create_session_token, user_from_session_token


def test_admin_gets_admin_and_architect_roles():
    settings = Settings(
        auth_secret_key="test-secret",
        auth_admin_identities="admin",
        auth_architect_identities="admin",
        auth_admin_password="admin",
    )

    user = authenticate_user(
        AuthLoginRequest(display_name="admin", requested_role="viewer", admin_password="admin"),
        settings=settings,
    )

    assert user.primary_role == "admin"
    assert "architect" in user.roles
    assert user.permissions["can_admin"] is True
    assert user.permissions["can_approve"] is True


def test_non_admin_reviewer_cannot_approve():
    settings = Settings(auth_secret_key="test-secret")

    user = authenticate_user(
        AuthLoginRequest(display_name="Reviewer One", requested_role="reviewer"),
        settings=settings,
    )

    assert user.primary_role == "reviewer"
    assert user.permissions["can_assess"] is True
    assert user.permissions["can_review"] is True
    assert user.permissions["can_approve"] is False


def test_demo_admin_requires_admin_password():
    settings = Settings(
        auth_secret_key="test-secret",
        auth_admin_identities="aryan",
        auth_architect_identities="aryan",
        auth_admin_password="old-render-password",
    )

    with pytest.raises(HTTPException):
        authenticate_user(
            AuthLoginRequest(display_name="admin", requested_role="reviewer", admin_password="wrong"),
            settings=settings,
        )

    user = authenticate_user(
        AuthLoginRequest(display_name="admin", requested_role="reviewer", admin_password="admin"),
        settings=settings,
    )

    assert user.primary_role == "admin"
    assert user.permissions["can_admin"] is True


def test_viewer_is_read_only():
    settings = Settings(auth_secret_key="test-secret")

    user = authenticate_user(
        AuthLoginRequest(display_name="Viewer One", requested_role="viewer"),
        settings=settings,
    )

    assert user.primary_role == "viewer"
    assert user.permissions["can_view"] is True
    assert user.permissions["can_assess"] is False
    assert user.permissions["can_review"] is False


def test_session_token_round_trip():
    settings = Settings(
        auth_secret_key="test-secret",
        auth_admin_identities="admin",
        auth_architect_identities="admin",
        auth_admin_password="admin",
    )
    user = authenticate_user(
        AuthLoginRequest(display_name="admin", email="admin@example.com", admin_password="admin"),
        settings=settings,
    )

    token = create_session_token(user, settings=settings)
    restored = user_from_session_token(token, settings=settings)

    assert restored.display_name == "admin"
    assert restored.primary_role == "admin"
    assert restored.permissions["can_architect_review"] is True


def test_session_token_rejects_tampering():
    settings = Settings(auth_secret_key="test-secret")
    user = authenticate_user(AuthLoginRequest(display_name="Reviewer"), settings=settings)
    token = create_session_token(user, settings=settings)

    with pytest.raises(HTTPException):
        user_from_session_token(f"{token}tampered", settings=settings)


def test_api_session_alias_supports_render_safe_login_path():
    client = TestClient(app)

    response = client.post(
        "/api/session",
        json={"display_name": "Renu", "requested_role": "reviewer"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["primary_role"] == "reviewer"
    assert "cloudbridge_iq_session" in response.cookies

    me_response = client.get("/api/session")

    assert me_response.status_code == 200
    assert me_response.json()["user"]["display_name"] == "Renu"
