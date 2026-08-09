"""
Webster Alpha

Gemini AI Provider

Primary cloud AI provider for Webster. Uses Google's current
``google-genai`` SDK and keeps the API key in GEMINI_API_KEY.
"""

from __future__ import annotations

import os
import time
from typing import Iterator

from core.provider.provider import Provider
from core.ai.request import AIRequest
from core.ai.response import AIResponse
from core.ai.types import AIProvider


class GeminiProvider(Provider):
    """Google Gemini provider using the official google-genai SDK."""

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(name="gemini", version="1.0")
        self._model = model
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self._timeout = timeout
        self._client = None
        self._import_error: str | None = None

    def initialize(self) -> None:
        if self._client is not None:
            return
        if not self._api_key:
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            self._import_error = None
        except Exception as error:
            self._client = None
            self._import_error = str(error)

    def _contents(self, request: AIRequest) -> str:
        parts: list[str] = []
        context = request.context

        for message in context.messages[-20:]:
            role = getattr(message, "role", "user")
            content = getattr(message, "content", str(message))
            parts.append(f"{role}: {content}")

        if parts:
            return "Conversation so far:\n" + "\n".join(parts) + f"\n\nUser: {request.prompt}"
        return request.prompt

    def _config(self, request: AIRequest):
        from google.genai import types
        kwargs = {"temperature": request.temperature}
        if request.max_tokens is not None:
            kwargs["max_output_tokens"] = request.max_tokens
        return types.GenerateContentConfig(**kwargs)

    def generate(self, request: AIRequest) -> AIResponse:
        if not self.available():
            return AIResponse.error(self._unavailable_message())

        started = time.perf_counter()
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=self._contents(request),
                config=self._config(request),
            )
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                return AIResponse.error("Gemini returned an empty response.")
            return AIResponse(
                content=text,
                provider=AIProvider.GEMINI,
                model=self._model,
                latency=time.perf_counter() - started,
                metadata={"provider": "gemini"},
            )
        except Exception as error:
            return AIResponse.error(f"Gemini request failed: {error}")

    def stream(self, request: AIRequest) -> Iterator[str]:
        if not self.available():
            raise RuntimeError(self._unavailable_message())
        try:
            for chunk in self._client.models.generate_content_stream(
                model=self._model,
                contents=self._contents(request),
                config=self._config(request),
            ):
                text = getattr(chunk, "text", None) or ""
                if text:
                    yield text
        except Exception as error:
            raise RuntimeError(f"Gemini streaming request failed: {error}") from error

    def available(self) -> bool:
        if self._client is None and self._api_key:
            self.initialize()
        return self._client is not None and bool(self._api_key)

    def health(self) -> dict:
        available = self.available()
        return {
            "healthy": available,
            "ready": available,
            "provider": self.name,
            "model": self._model,
            "configured": bool(self._api_key),
            "sdk_error": self._import_error,
        }

    def shutdown(self) -> None:
        self._client = None

    def set_model(self, model: str) -> None:
        model = model.strip()
        if not model:
            raise ValueError("Gemini model name cannot be empty.")
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def _unavailable_message(self) -> str:
        if not self._api_key:
            return "Gemini is not configured. Set GEMINI_API_KEY in your environment."
        if self._import_error:
            return f"Gemini SDK could not initialize: {self._import_error}"
        return "Gemini is currently unavailable."

    def __repr__(self) -> str:
        return f"GeminiProvider(model='{self._model}', configured={bool(self._api_key)})"
