"""Nebius Token Factory client (OpenAI-compatible)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from openai import OpenAI

from apprentice.config import Settings, load_settings


class TokenFactoryClient:
    """Live inference for Nemotron (think) and Cosmos Reasoner (see)."""

    def __init__(self, settings: Settings | None = None, client: OpenAI | None = None) -> None:
        self.settings = settings or load_settings()
        if client is not None:
            self._client = client
        else:
            if not self.settings.nebius_api_key:
                raise RuntimeError(
                    "NEBIUS_API_KEY is empty. Copy .env.example to .env and add a Token Factory key."
                )
            self._client = OpenAI(
                base_url=self.settings.nebius_base_url,
                api_key=self.settings.nebius_api_key,
                timeout=self.settings.request_timeout_s,
            )

    def chat(
        self,
        model: str,
        messages: Sequence[dict[str, Any]],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> Any:
        return self._client.chat.completions.create(
            model=model,
            messages=list(messages),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def text(self, model: str, messages: Sequence[dict[str, Any]], **kwargs: Any) -> str:
        response = self.chat(model, messages, **kwargs)
        content = response.choices[0].message.content
        return content or ""
