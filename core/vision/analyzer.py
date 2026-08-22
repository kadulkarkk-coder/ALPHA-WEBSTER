"""Vision analysis contracts and resource-aware orchestration."""
from __future__ import annotations

from typing import Protocol

from core.vision.ocr import OCRService
from core.vision.types import VisionFrame, VisionResult


class VisionProvider(Protocol):
    def analyze(self, frame: VisionFrame, question: str | None = None) -> VisionResult: ...


class VisionAnalyzer:
    def __init__(self, provider: VisionProvider | None = None, ocr: OCRService | None = None) -> None:
        self.provider = provider
        self.ocr = ocr or OCRService()

    def analyze(self, frame: VisionFrame, question: str | None = None) -> VisionResult:
        if self.provider is None:
            return VisionResult(source=frame.source, text=tuple(self.ocr.extract(frame)))
        return self.provider.analyze(frame, question)
