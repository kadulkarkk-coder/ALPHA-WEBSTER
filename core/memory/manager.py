"""
Webster Alpha

Memory Manager

High-level interface for the
Webster Memory Engine.
"""

from __future__ import annotations

from core.memory.memory import Memory
from core.memory.query import MemoryQuery
from core.memory.record import MemoryRecord
from core.memory.store import MemoryStore
from core.memory.types import MemoryType
from core.events.event_bus import EventBus
from core.events.event import Event
from core.events.event_types import EventType


class MemoryManager:
    """
    Webster Memory Manager.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
    ) -> None:

        self._store = MemoryStore()

        self._event_bus = event_bus

    #
    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------
    #

    def remember(
        self,
        memory_type: MemoryType,
        topic: str,
        value: str,
        source: str = "system",
        confidence: float = 1.0,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> MemoryRecord:

        record = MemoryRecord(

            memory_type=memory_type,

            topic=topic,

            value=value,

            source=source,

            confidence=confidence,

            tags=tags or [],

            metadata=metadata or {}

        )

        self._store.add(
            record
        )

        if self._event_bus is not None:
            self._event_bus.publish(
                Event(
                    name=EventType.MEMORY_CREATED.name,
                    source="memory_manager",
                    data={
                        "id": record.id,
                        "topic": record.topic,
                        "type": record.memory_type.name,
                    },
                )
            )

        return record

    #
    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------
    #

    def search(
        self,
        query: MemoryQuery
    ) -> list[MemoryRecord]:

        results = self._store.search(
            query
        )

        if self._event_bus is not None:
            self._event_bus.publish(
                Event(
                    name=EventType.MEMORY_SEARCHED.name,
                    source="memory_manager",
                    data={
                        "query": query.topic,
                        "results": len(results),
                    },
                )
            )

        return results

    def find(
        self,
        topic: str
    ) -> list[MemoryRecord]:

        return self.search(

            MemoryQuery(

                topic=topic

            )

        )

    def get(
        self,
        identifier: str
    ) -> MemoryRecord | None:

        return self._store.get(
            identifier
        )

    #
    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------
    #

    def update(
        self,
        identifier: str,
        value: str
    ) -> bool:

        record = self.get(
            identifier
        )

        if record is None:

            return False

        record.update(
            value
        )

        if self._event_bus is not None:
            self._event_bus.publish(
                Event(
                    name=EventType.MEMORY_UPDATED.name,
                    source="memory_manager",
                    data={
                        "id": record.id,
                        "topic": record.topic,
                        "value": record.value,
                    },
                )
            )

        return True

    #
    # ---------------------------------------------------------
    # Archive
    # ---------------------------------------------------------
    #

    def archive(
        self,
        identifier: str
    ) -> bool:

        record = self.get(
            identifier
        )

        if record is None:

            return False

        record.archive()

        return True

    def restore(
        self,
        identifier: str
    ) -> bool:

        record = self.get(
            identifier
        )

        if record is None:

            return False

        record.restore()

        return True

    #
    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------
    #

    def forget(
        self,
        identifier: str
    ) -> bool:

        return (

            self._store.remove(

                identifier

            )

            is not None

        )

    #
    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    #

    @property
    def count(
        self
    ) -> int:

        return self._store.count

    @property
    def active(
        self
    ) -> int:

        return self._store.active

    @property
    def archived(
        self
    ) -> int:

        return self._store.archived

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def store(
        self
    ) -> MemoryStore:

        return self._store

    #
    # ---------------------------------------------------------
    # Future API
    # ---------------------------------------------------------
    #

    def build_memory(
        self,
        record: MemoryRecord
    ) -> Memory:

        """
        Placeholder for the future
        Memory object.

        Sprint 24.6 will implement this.
        """

        return Memory(
            record
        )

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "MemoryManager("

            f"records={self.count}"

            ")"

        )