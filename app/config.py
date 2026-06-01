"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings for model access and request processing."""

    openai_api_key: str | None = Field(default=None)
    model_name: str = Field(default="gpt-4.1")
    vision_model_name: str = Field(default="gpt-4.1")
    ssl_openai: str | None = Field(default=None)
    poppler_path: str | None = Field(default=None)
    graphviz_dot: str | None = Field(default=None)
    max_upload_bytes: int = Field(default=15 * 1024 * 1024)
    auth_secret_key: str = Field(default="cloudbridge-local-dev-secret-change-me")
    auth_admin_identities: str = Field(
        default="aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04",
    )
    auth_architect_identities: str = Field(
        default="aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04",
    )
    auth_admin_password: str | None = Field(default=None)
    auth_default_role: str = Field(default="reviewer")
    auth_session_hours: int = Field(default=8)

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def openai_ssl_insecure(self) -> bool:
        return (self.ssl_openai or "").strip().lower() == "insecure"

    @property
    def admin_identity_set(self) -> set[str]:
        return _split_identity_list(self.auth_admin_identities)

    @property
    def architect_identity_set(self) -> set[str]:
        return _split_identity_list(self.auth_architect_identities)


@lru_cache
def get_settings() -> Settings:
    # Local development should honor the project .env even when the shell has
    # an older OPENAI_API_KEY inherited from another tool or terminal session.
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        model_name=os.getenv("MODEL_NAME", "gpt-4.1"),
        vision_model_name=os.getenv("VISION_MODEL_NAME", "gpt-4.1"),
        ssl_openai=os.getenv("SSL_OPENAI") or None,
        poppler_path=os.getenv("POPPLER_PATH") or None,
        graphviz_dot=os.getenv("GRAPHVIZ_DOT") or None,
        auth_secret_key=os.getenv("AUTH_SECRET_KEY", "cloudbridge-local-dev-secret-change-me"),
        auth_admin_identities=os.getenv(
            "AUTH_ADMIN_IDENTITIES",
            "aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04",
        ),
        auth_architect_identities=os.getenv(
            "AUTH_ARCHITECT_IDENTITIES",
            "aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04",
        ),
        auth_admin_password=os.getenv("AUTH_ADMIN_PASSWORD") or None,
        auth_default_role=os.getenv("AUTH_DEFAULT_ROLE", "reviewer"),
        auth_session_hours=int(os.getenv("AUTH_SESSION_HOURS", "8")),
    )


def _split_identity_list(value: str | None) -> set[str]:
    if not value:
        return set()
    return {_normalize_identity(item) for item in value.split(",") if item.strip()}


def _normalize_identity(value: str) -> str:
    return " ".join(value.strip().lower().split())
