"""Memory importance scoring."""

from __future__ import annotations

from core.memory.record import MemoryRecord


class MemoryImportanceScorer:
    """Scores memories using stable, explainable signals."""

    def score(self, record: MemoryRecord) -> float:
        confidence = min(1.0, max(0.0, record.confidence))
        persistence = 1.0 if record.persistent else 0.4
        access = min(1.0, record.access_count / 10.0)
        return round((confidence * 0.65) + (persistence * 0.25) + (access * 0.10), 3)
