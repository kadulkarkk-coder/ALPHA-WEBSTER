"""Safe, on-demand visual capture abstractions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.vision.types import VisionFrame, VisionSource


class FrameProvider(Protocol):
    def capture(self) -> VisionFrame: ...


@dataclass(slots=True)
class VisionCapture:
    """Coordinates injected screen/camera providers without owning UI code."""

    screen_provider: FrameProvider | None = None
    camera_provider: FrameProvider | None = None

    def capture_screen(self) -> VisionFrame:
        if self.screen_provider is None:
            raise RuntimeError("Screen capture provider is not configured.")
        frame = self.screen_provider.capture()
        if frame.source is not VisionSource.SCREEN:
            raise ValueError("Screen provider returned a non-screen frame.")
        return frame

    def capture_camera(self) -> VisionFrame:
        if self.camera_provider is None:
            raise RuntimeError("Camera capture provider is not configured.")
        frame = self.camera_provider.capture()
        if frame.source is not VisionSource.CAMERA:
            raise ValueError("Camera provider returned a non-camera frame.")
        return frame
