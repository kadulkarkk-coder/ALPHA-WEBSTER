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

    Responsible for managing the high-level memory API
    and controlling the lifecycle of the underlying
    MemoryStore.
    """

    # =====================================================
    # Construction
    # =====================================================

    def __init__(
        self,
        event_bus: EventBus | None = None,
    ) -> None:
        """
        Create the memory manager.

        The MemoryStore is created here, but the memory
        subsystem becomes operational only after
        initialize() is called.
        """

        self._store = MemoryStore()

        self._event_bus = event_bus

        self._initialized = False

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the memory subsystem.

        The current MemoryStore does not require an
        external database connection, so initialization
        verifies that the store is available and marks
        the manager as ready.
        """

        if self._initialized:

            return

        if self._store is None:

            self._store = MemoryStore()

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the memory subsystem.

        The current MemoryStore does not expose a close()
        operation, so we retain the store and simply mark
        the manager as inactive.

        This allows the manager to be initialized again
        later without losing existing in-memory records.
        """

        if not self._initialized:

            return

        self._initialized = False

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    # -----------------------------------------------------

    @property
    def ready(
        self,
    ) -> bool:

        return (

            self._initialized

            and self._store is not None

        )

    # =====================================================
    # Internal Validation
    # =====================================================

    def _ensure_initialized(
        self,
    ) -> None:
        """
        Ensure that the memory manager is initialized.
        """

        if not self._initialized:

            raise RuntimeError(

                "MemoryManager has not been initialized. "
                "Call initialize() before using memory."

            )

    # =====================================================
    # Create
    # =====================================================

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

        self._ensure_initialized()

        record = MemoryRecord(

            memory_type=memory_type,

            topic=topic,

            value=value,

            source=source,

            confidence=confidence,

            tags=tags or [],

            metadata=metadata or {},

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

    # =====================================================
    # Read
    # =====================================================

    def search(
        self,
        query: MemoryQuery,
    ) -> list[MemoryRecord]:

        self._ensure_initialized()

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

    # -----------------------------------------------------

    def find(
        self,
        topic: str,
    ) -> list[MemoryRecord]:

        self._ensure_initialized()

        return self.search(

            MemoryQuery(

                topic=topic

            )

        )

    # -----------------------------------------------------

    def get(
        self,
        identifier: str,
    ) -> MemoryRecord | None:

        self._ensure_initialized()

        return self._store.get(

            identifier

        )

    # =====================================================
    # Update
    # =====================================================

    def update(
        self,
        identifier: str,
        value: str,
    ) -> bool:

        self._ensure_initialized()

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

    # =====================================================
    # Archive
    # =====================================================

    def archive(
        self,
        identifier: str,
    ) -> bool:

        self._ensure_initialized()

        record = self.get(

            identifier

        )

        if record is None:

            return False

        record.archive()

        return True

    # -----------------------------------------------------

    def restore(
        self,
        identifier: str,
    ) -> bool:

        self._ensure_initialized()

        record = self.get(

            identifier

        )

        if record is None:

            return False

        record.restore()

        return True

    # =====================================================
    # Remove
    # =====================================================

    def forget(
        self,
        identifier: str,
    ) -> bool:

        self._ensure_initialized()

        return (

            self._store.remove(

                identifier

            )

            is not None

        )

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def count(
        self,
    ) -> int:

        if self._store is None:

            return 0

        return self._store.count

    # -----------------------------------------------------

    @property
    def active(
        self,
    ) -> int:

        if self._store is None:

            return 0

        return self._store.active

    # -----------------------------------------------------

    @property
    def archived(
        self,
    ) -> int:

        if self._store is None:

            return 0

        return self._store.archived

    # =====================================================
    # Access
    # =====================================================

    @property
    def store(
        self,
    ) -> MemoryStore:

        self._ensure_initialized()

        return self._store

    # =====================================================
    # Memory Object
    # =====================================================

    def build_memory(
        self,
        record: MemoryRecord,
    ) -> Memory:

        self._ensure_initialized()

        return Memory(

            record

        )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return memory subsystem health information.
        """

        return {

            "initialized": self._initialized,

            "healthy": self.ready,

            "ready": self.ready,

            "records": self.count,

            "active": self.active,

            "archived": self.archived,

        }

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            "MemoryManager("

            f"initialized={self._initialized}, "

            f"records={self.count}"

            ")"

        )