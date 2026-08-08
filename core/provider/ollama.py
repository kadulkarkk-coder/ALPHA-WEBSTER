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
        model: str = "qwen2.5:3b",
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
        """Initialize without making Ollama availability fatal to startup."""

        return

    def _models(
        self,
    ) -> list[str]:
        """Return locally installed Ollama model names."""

        try:

            response = requests.get(
                f"{self._host}/api/tags",
                timeout=3,
            )

            response.raise_for_status()

            data = response.json()

            return [
                model.get("name", "").strip()
                for model in data.get("models", [])
                if model.get("name")
            ]

        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ):

            return []

    def _select_model(
        self,
    ) -> str | None:
        """Select the configured model or the first installed model."""

        models = self._models()

        if not models:
            return None

        if self._model in models:
            return self._model

        configured_base = self._model.split(":", 1)[0].lower()

        for model in models:

            if model.split(":", 1)[0].lower() == configured_base:

                self._model = model
                return model

        self._model = models[0]
        return self._model

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Generate a response through Ollama."""

        model = self._select_model()

        if model is None:

            return AIResponse.error(
                "No Ollama models are installed. "
                "Run 'ollama list' to check, then install a model "
                "such as 'ollama pull qwen2.5:3b'."
            )

        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        try:

            response = requests.post(
                f"{self._host}/api/generate",
                json=payload,
                timeout=self._timeout,
            )

            response.raise_for_status()

            data = response.json()

            content = data.get(
                "response",
                "",
            )

            if not content:

                return AIResponse.error(
                    "Ollama returned an empty response."
                )

            return AIResponse(
                content=content,
                provider=AIProvider.OLLAMA,
                model=model,
            )

        except requests.RequestException as error:

            return AIResponse.error(
                f"Ollama request failed: {error}"
            )

        except ValueError as error:

            return AIResponse.error(
                f"Ollama returned invalid JSON: {error}"
            )

    def stream(
        self,
        request: AIRequest,
    ) -> Iterator[str]:
        """Stream a response through Ollama."""

        model = self._select_model()

        if model is None:

            raise RuntimeError(
                "No Ollama models are installed. "
                "Run 'ollama pull qwen2.5:3b'."
            )

        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature,
            },
        }

        try:

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

        except requests.RequestException as error:

            raise RuntimeError(
                f"Ollama streaming request failed: {error}"
            ) from error

    def available(
        self,
    ) -> bool:
        """Return True only when Ollama is reachable and has a model."""

        return bool(
            self._models()
        )

    @property
    def model(
        self,
    ) -> str:
        return self._model

    def set_model(
        self,
        model: str,
    ) -> None:

        model = model.strip()

        if not model:

            raise ValueError(
                "Ollama model name cannot be empty."
            )

        self._model = model

    def health(
        self,
    ) -> dict:

        models = self._models()
        available = bool(models)

        return {
            "healthy": available,
            "ready": available,
            "provider": self.name,
            "model": self._model,
            "host": self._host,
            "installed_models": models,
        }

    def shutdown(
        self,
    ) -> None:
        return

    def __repr__(
        self,
    ) -> str:

        return (
            "OllamaProvider("
            f"model='{self._model}', "
            f"host='{self._host}'"
            ")"
        )
