"""Memory context construction for WEBSTER AI requests."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.memory.manager import MemoryManager
from core.memory.query import MemoryQuery
from core.memory.record import MemoryRecord


@dataclass(slots=True)
class MemoryContext:
    """A bounded, AI-safe view of relevant memories."""

    records: list[MemoryRecord] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return not self.records

    def as_text(self) -> str:
        if not self.records:
            return ""
        return "\n".join(
            f"[{record.memory_type.name}] {record.topic}: {record.value}"
            for record in self.records
        )


class MemoryContextBuilder:
    """Retrieves relevant memories without exposing non-AI-visible records."""

    def __init__(self, memory: MemoryManager, limit: int = 8) -> None:
        if memory is None:
            raise ValueError("MemoryContextBuilder requires a MemoryManager.")
        self.memory = memory
        self.limit = max(1, int(limit))

    def build(self, topic: str) -> MemoryContext:
        topic = str(topic).strip()
        if not topic:
            return MemoryContext()
        if not self.memory.initialized:
            self.memory.initialize()
        results = self.memory.search(MemoryQuery(topic=topic))
        visible = [record for record in results if record.ai_visible and not record.archived]
        return MemoryContext(visible[: self.limit])

    def build_from_records(self, records: list[MemoryRecord]) -> MemoryContext:
        visible = [record for record in records if record.ai_visible and not record.archived]
        return MemoryContext(visible[: self.limit])
