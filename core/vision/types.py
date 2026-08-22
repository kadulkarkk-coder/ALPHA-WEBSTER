"""Core types for WEBSTER vision capabilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VisionSource(str, Enum):
    SCREEN = "screen"
    CAMERA = "camera"
    IMAGE = "image"


@dataclass(frozen=True, slots=True)
class VisionFrame:
    source: VisionSource
    data: bytes
    width: int = 0
    height: int = 0
    format: str = "unknown"
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OCRText:
    text: str
    confidence: float = 0.0
    bounds: tuple[int, int, int, int] | None = None


@dataclass(frozen=True, slots=True)
class VisionResult:
    source: VisionSource
    description: str = ""
    text: tuple[OCRText, ...] = ()
    objects: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)
