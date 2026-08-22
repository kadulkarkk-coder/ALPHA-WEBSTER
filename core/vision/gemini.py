"""Optional Gemini-backed multimodal provider for Webster vision."""

from __future__ import annotations

import os

from core.vision.types import VisionFrame, VisionResult, VisionSource


class GeminiVisionProvider:
    """Analyze captured frames with Gemini when GEMINI_API_KEY is configured."""

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        self._client = None
        self._error: str | None = None
        if self.api_key:
            self._initialize()

    def _initialize(self) -> None:
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._error = None
        except Exception as exc:
            self._client = None
            self._error = str(exc)

    @property
    def available(self) -> bool:
        return self._client is not None

    @property
    def error(self) -> str | None:
        return self._error

    def analyze(self, frame: VisionFrame, question: str | None = None) -> VisionResult:
        if not self.available:
            raise RuntimeError(
                self._error
                or "Gemini vision is not configured. Set GEMINI_API_KEY to enable semantic screen analysis."
            )

        prompt = question.strip() if question and question.strip() else (
            "Describe what is visible on this screen. Focus on useful UI elements, "
            "applications, windows, prominent text, and anything that appears relevant."
        )

        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=frame.data, mime_type="image/png"),
                ],
            )
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                raise RuntimeError("Gemini vision returned an empty response.")
            return VisionResult(
                source=frame.source if frame.source else VisionSource.IMAGE,
                description=text,
                metadata={"provider": "gemini", "model": self.model},
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini vision request failed: {exc}") from exc
