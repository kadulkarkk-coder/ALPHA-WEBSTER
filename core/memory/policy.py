"""Memory retention and privacy policy for WEBSTER."""

from __future__ import annotations

from dataclasses import dataclass

from core.memory.extraction import MemoryCandidate


@dataclass(frozen=True, slots=True)
class MemoryDecision:
    """Decision made before a candidate is persisted."""

    store: bool
    reason: str
    importance: float


class MemoryPolicy:
    """Conservative policy preventing automatic storage of arbitrary text."""

    def evaluate(self, candidate: MemoryCandidate) -> MemoryDecision:
        if not candidate.value.strip():
            return MemoryDecision(False, "empty value", 0.0)
        if candidate.confidence < 0.75:
            return MemoryDecision(False, "confidence below retention threshold", candidate.confidence)
        if candidate.memory_type.name in {"LOG", "CACHE"}:
            return MemoryDecision(False, "non-persistent memory category", 0.0)
        importance = min(1.0, max(0.0, candidate.confidence))
        return MemoryDecision(True, "explicit or high-confidence memory", importance)
