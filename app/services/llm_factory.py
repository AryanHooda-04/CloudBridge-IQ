"""LLM client construction helpers."""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings


def build_chat_openai(*, model: str, temperature: float = 0, **kwargs: Any):
    """Create a ChatOpenAI client with local environment SSL options."""

    settings = get_settings()
    client_kwargs: dict[str, Any] = {
        "model": model,
        "api_key": settings.openai_api_key,
        "temperature": temperature,
        **kwargs,
    }

    if settings.openai_ssl_insecure:
        client_kwargs["http_client"] = httpx.Client(verify=False)
        client_kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(**client_kwargs)
