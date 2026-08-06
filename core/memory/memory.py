"""
Webster Alpha

Memory

Public interface for the Webster
Memory Engine.
"""

from __future__ import annotations

from core.memory.query import MemoryQuery
from core.memory.record import MemoryRecord
from core.memory.types import MemoryType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.memory.manager import MemoryManager


class Memory:
    """
    Webster Memory API.

    Every Webster subsystem should
    communicate with memory through
    this class.
    """

    def __init__(
        self,
        manager: MemoryManager | None = None
    ) -> None:

        # defer import to avoid circular imports
        if manager is None:
            from core.memory.manager import MemoryManager as _MemoryManager

            self._manager = _MemoryManager()
        else:
            self._manager = manager

    #
    # ---------------------------------------------------------
    # Remember
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

        return self._manager.remember(

            memory_type=memory_type,

            topic=topic,

            value=value,

            source=source,

            confidence=confidence,

            tags=tags,

            metadata=metadata,

        )

    #
    # ---------------------------------------------------------
    # Recall
    # ---------------------------------------------------------
    #

    def recall(
        self,
        topic: str
    ) -> list[MemoryRecord]:

        return self._manager.find(
            topic
        )

    def search(
        self,
        query: MemoryQuery
    ) -> list[MemoryRecord]:

        return self._manager.search(
            query
        )

    def get(
        self,
        identifier: str
    ) -> MemoryRecord | None:

        return self._manager.get(
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

        return self._manager.update(

            identifier,

            value

        )

    #
    # ---------------------------------------------------------
    # Archive
    # ---------------------------------------------------------
    #

    def archive(
        self,
        identifier: str
    ) -> bool:

        return self._manager.archive(
            identifier
        )

    def restore(
        self,
        identifier: str
    ) -> bool:

        return self._manager.restore(
            identifier
        )

    #
    # ---------------------------------------------------------
    # Forget
    # ---------------------------------------------------------
    #

    def forget(
        self,
        identifier: str
    ) -> bool:

        return self._manager.forget(
            identifier
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

        return self._manager.count

    @property
    def active(
        self
    ) -> int:

        return self._manager.active

    @property
    def archived(
        self
    ) -> int:

        return self._manager.archived

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def manager(
        self
    ) -> MemoryManager:

        return self._manager

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "Memory("

            f"records={self.count}"

            ")"

        )