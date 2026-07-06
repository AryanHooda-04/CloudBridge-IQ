"""Local authentication and RBAC helpers for CloudBridge IQ.

This module intentionally avoids external auth dependencies. It provides a
small signed-cookie session layer that can later be replaced by SSO while the
rest of the app keeps using the same user and permission contract.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.schemas import AuthLoginRequest, AuthUser, UserRole


SESSION_COOKIE_NAME = "cloudbridge_iq_session"

ROLE_PERMISSIONS: dict[UserRole, dict[str, bool]] = {
    "admin": {
        "can_view": True,
        "can_assess": True,
        "can_review": True,
        "can_architect_review": True,
        "can_approve": True,
        "can_admin": True,
    },
    "architect": {
        "can_view": True,
        "can_assess": True,
        "can_review": True,
        "can_architect_review": True,
        "can_approve": True,
        "can_admin": False,
    },
    "reviewer": {
        "can_view": True,
        "can_assess": True,
        "can_review": True,
        "can_architect_review": False,
        "can_approve": False,
        "can_admin": False,
    },
    "viewer": {
        "can_view": True,
        "can_assess": False,
        "can_review": False,
        "can_architect_review": False,
        "can_approve": False,
        "can_admin": False,
    },
}


def authenticate_user(request: AuthLoginRequest, settings: Settings | None = None) -> AuthUser:
    """Resolve local identity to RBAC roles.

    The configured demo admin identity is promoted to admin + architect through the configured
    identity allowlist. Everyone else is constrained to reviewer or viewer.
    """

    settings = settings or get_settings()
    display_name = request.display_name.strip()
    email = (request.email or "").strip() or None
    identities = _candidate_identities(display_name, email)
    requested_role = request.requested_role

    if "admin" in identities:
        if not hmac.compare_digest(request.admin_password or "", "admin"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Demo admin sign-in requires password admin.",
            )
        return _build_user(
            display_name=display_name,
            email=email,
            primary_role="admin",
            roles=["admin", "architect", "reviewer", "viewer"],
        )

    if identities & settings.admin_identity_set:
        _validate_admin_password(request.admin_password, settings)
        return _build_user(
            display_name=display_name,
            email=email,
            primary_role="admin",
            roles=["admin", "architect", "reviewer", "viewer"],
        )

    if identities & settings.architect_identity_set:
        return _build_user(
            display_name=display_name,
            email=email,
            primary_role="architect",
            roles=["architect", "reviewer", "viewer"],
        )

    role: UserRole = "reviewer" if requested_role not in {"reviewer", "viewer"} else requested_role
    roles: list[UserRole] = ["reviewer", "viewer"] if role == "reviewer" else ["viewer"]
    return _build_user(display_name=display_name, email=email, primary_role=role, roles=roles)


def create_session_token(user: AuthUser, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    issued_at = int(time.time())
    payload: dict[str, Any] = {
        "name": user.display_name,
        "email": user.email,
        "primary_role": user.primary_role,
        "roles": user.roles,
        "iat": issued_at,
        "exp": issued_at + max(settings.auth_session_hours, 1) * 3600,
    }
    encoded_payload = _b64encode_json(payload)
    signature = _sign(encoded_payload, settings.auth_secret_key)
    return f"{encoded_payload}.{signature}"


def user_from_session_token(token: str, settings: Settings | None = None) -> AuthUser:
    settings = settings or get_settings()
    try:
        encoded_payload, supplied_signature = token.split(".", 1)
    except ValueError as exc:
        raise _auth_error() from exc

    expected_signature = _sign(encoded_payload, settings.auth_secret_key)
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise _auth_error()

    try:
        payload = _b64decode_json(encoded_payload)
    except (ValueError, json.JSONDecodeError) as exc:
        raise _auth_error() from exc

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Sign in again.",
        )

    roles = [role for role in payload.get("roles", []) if role in ROLE_PERMISSIONS]
    primary_role = payload.get("primary_role")
    if primary_role not in ROLE_PERMISSIONS or not roles:
        raise _auth_error()

    return _build_user(
        display_name=str(payload.get("name") or "CloudBridge user"),
        email=payload.get("email"),
        primary_role=primary_role,
        roles=roles,
    )


def get_current_user(
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> AuthUser:
    if not session_token:
        raise _auth_error()
    return user_from_session_token(session_token)


def require_permission(permission: str) -> Callable[[AuthUser], AuthUser]:
    def _dependency(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if not user.permissions.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return user

    return _dependency


def session_max_age_seconds(settings: Settings | None = None) -> int:
    settings = settings or get_settings()
    return max(settings.auth_session_hours, 1) * 3600


def _build_user(
    *,
    display_name: str,
    email: str | None,
    primary_role: UserRole,
    roles: list[UserRole],
) -> AuthUser:
    permissions = {key: False for role in ROLE_PERMISSIONS.values() for key in role}
    for role in roles:
        for permission, allowed in ROLE_PERMISSIONS[role].items():
            permissions[permission] = permissions[permission] or allowed
    return AuthUser(
        display_name=display_name,
        email=email,
        primary_role=primary_role,
        roles=roles,
        permissions=permissions,
    )


def _candidate_identities(display_name: str, email: str | None) -> set[str]:
    values = {display_name}
    if email:
        values.add(email)
        values.add(email.split("@", 1)[0])
    return {_normalize_identity(value) for value in values if value.strip()}


def _validate_admin_password(admin_password: str | None, settings: Settings) -> None:
    if not settings.auth_admin_password:
        return
    if not hmac.compare_digest(admin_password or "", settings.auth_admin_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin sign-in requires the configured admin password.",
        )


def _sign(encoded_payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).digest()
    return _b64encode_bytes(digest)


def _b64encode_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64encode_bytes(raw)


def _b64decode_json(value: str) -> dict[str, Any]:
    padded = value + "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("Session payload must be an object.")
    return decoded


def _b64encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _normalize_identity(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )
