"""High-level vision manager for WEBSTER."""
from __future__ import annotations

from dataclasses import dataclass, replace

from core.vision.analyzer import VisionAnalyzer
from core.vision.capture import VisionCapture
from core.vision.types import VisionFrame, VisionResult


@dataclass(slots=True)
class VisionManager:
    capture: VisionCapture
    analyzer: VisionAnalyzer
    enabled: bool = False

    def capture_and_analyze_screen(self, question: str | None = None) -> VisionResult:
        self._ensure_enabled()
        return self._analyze_with_frame(self.capture.capture_screen(), question)

    def capture_and_analyze_camera(self, question: str | None = None) -> VisionResult:
        self._ensure_enabled()
        return self._analyze_with_frame(self.capture.capture_camera(), question)

    def analyze_frame(self, frame: VisionFrame, question: str | None = None) -> VisionResult:
        self._ensure_enabled()
        return self.analyzer.analyze(frame, question)

    def _analyze_with_frame(self, frame: VisionFrame, question: str | None) -> VisionResult:
        result = self.analyzer.analyze(frame, question)
        metadata = dict(result.metadata)
        metadata.update(frame.metadata)
        metadata.update({"width": frame.width, "height": frame.height, "format": frame.format})
        return replace(result, metadata=metadata)

    def _ensure_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Vision processing is disabled. Say 'activate vision' first.")

    def health(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "screen_capture": self.capture.screen_provider is not None,
            "camera_capture": self.capture.camera_provider is not None,
            "vision_provider": self.analyzer.provider is not None,
            "ocr_provider": self.analyzer.ocr.provider is not None,
        }
