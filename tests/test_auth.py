import pytest
from fastapi import HTTPException

from app.config import Settings
from app.schemas import AuthLoginRequest
from app.services.auth import authenticate_user, create_session_token, user_from_session_token


def test_aryan_gets_admin_and_architect_roles():
    settings = Settings(
        auth_secret_key="test-secret",
        auth_admin_identities="aryan,aryan.a",
        auth_architect_identities="aryan,aryan.a",
    )

    user = authenticate_user(
        AuthLoginRequest(display_name="Aryan", requested_role="viewer"),
        settings=settings,
    )

    assert user.primary_role == "admin"
    assert "architect" in user.roles
    assert user.permissions["can_admin"] is True
    assert user.permissions["can_approve"] is True


def test_non_aryan_reviewer_cannot_approve():
    settings = Settings(auth_secret_key="test-secret")

    user = authenticate_user(
        AuthLoginRequest(display_name="Reviewer One", requested_role="reviewer"),
        settings=settings,
    )

    assert user.primary_role == "reviewer"
    assert user.permissions["can_assess"] is True
    assert user.permissions["can_review"] is True
    assert user.permissions["can_approve"] is False


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
    settings = Settings(auth_secret_key="test-secret")
    user = authenticate_user(
        AuthLoginRequest(display_name="Aryan", email="aryan.a@example.com"),
        settings=settings,
    )

    token = create_session_token(user, settings=settings)
    restored = user_from_session_token(token, settings=settings)

    assert restored.display_name == "Aryan"
    assert restored.primary_role == "admin"
    assert restored.permissions["can_architect_review"] is True


def test_session_token_rejects_tampering():
    settings = Settings(auth_secret_key="test-secret")
    user = authenticate_user(AuthLoginRequest(display_name="Reviewer"), settings=settings)
    token = create_session_token(user, settings=settings)

    with pytest.raises(HTTPException):
        user_from_session_token(f"{token}tampered", settings=settings)
