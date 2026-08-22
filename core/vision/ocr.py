"""OCR abstraction for WEBSTER vision."""
from __future__ import annotations

from typing import Protocol

from core.vision.types import OCRText, VisionFrame


class OCRProvider(Protocol):
    def extract(self, frame: VisionFrame) -> list[OCRText]: ...


class OCRService:
    def __init__(self, provider: OCRProvider | None = None) -> None:
        self.provider = provider

    def extract(self, frame: VisionFrame) -> list[OCRText]:
        if self.provider is None:
            return []
        return list(self.provider.extract(frame))
