"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

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

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def openai_ssl_insecure(self) -> bool:
        return (self.ssl_openai or "").strip().lower() == "insecure"


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        model_name=os.getenv("MODEL_NAME", "gpt-4.1"),
        vision_model_name=os.getenv("VISION_MODEL_NAME", "gpt-4.1"),
        ssl_openai=os.getenv("SSL_OPENAI") or None,
        poppler_path=os.getenv("POPPLER_PATH") or None,
        graphviz_dot=os.getenv("GRAPHVIZ_DOT") or None,
    )
