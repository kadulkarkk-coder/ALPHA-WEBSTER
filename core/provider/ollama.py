"""
Webster Alpha

Ollama Provider
"""

from __future__ import annotations

import json
from typing import Iterator

import requests

from core.provider.provider import Provider
from core.ai.request import AIRequest
from core.ai.response import AIResponse
from core.ai.types import AIProvider


class OllamaProvider(Provider):
    """Local Ollama AI Provider."""

    DEFAULT_HOST = "http://127.0.0.1:11434"

    def __init__(
        self,
        model: str = "qwen3:latest",
        host: str = DEFAULT_HOST,
        timeout: float = 120.0,
    ) -> None:

        super().__init__(
            name="ollama",
            version="1.0",
        )

        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout

    def initialize(
        self,
    ) -> None:
        """Verify Ollama availability."""

        if not self.available():

            raise RuntimeError(
                "Ollama server is not running."
            )

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Generate a complete response."""

        payload = {
            "model": self._model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        response = requests.post(
            f"{self._host}/api/generate",
            json=payload,
            timeout=self._timeout,
        )

        response.raise_for_status()

        data = response.json()

        return AIResponse(
            content=data.get("response", ""),
            provider=AIProvider.OLLAMA,
            model=self._model,
        )

    def stream(
        self,
        request: AIRequest,
    ) -> Iterator[str]:

        payload = {
            "model": self._model,
            "prompt": request.prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature,
            },
        }

        response = requests.post(
            f"{self._host}/api/generate",
            json=payload,
            stream=True,
            timeout=self._timeout,
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:

                continue

            chunk = json.loads(
                line.decode("utf-8")
            )

            if "response" in chunk:

                yield chunk["response"]

    def available(
        self,
    ) -> bool:

        try:

            response = requests.get(
                f"{self._host}/api/tags",
                timeout=3,
            )

            return response.status_code == 200

        except Exception:

            return False

    @property
    def model(
        self,
    ) -> str:

        return self._model

    def set_model(
        self,
        model: str,
    ) -> None:

        self._model = model

    def health(
        self,
    ) -> dict:

        return {
            "healthy": self.available(),
            "provider": self.name,
            "model": self._model,
            "host": self._host,
        }

    def shutdown(
        self,
    ) -> None:

        pass

    def __repr__(
        self,
    ) -> str:

        return (
            "OllamaProvider("
            f"model='{self._model}', "
            f"host='{self._host}'"
            ")"
        )
