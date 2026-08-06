"""
Webster Alpha

Memory Record

Represents a single memory stored
inside the Webster Memory Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from uuid import uuid4

from core.memory.types import MemoryType


@dataclass(slots=True)
class MemoryRecord:
    """
    A single memory.
    """

    memory_type: MemoryType

    topic: str

    value: str

    source: str

    confidence: float = 1.0

    tags: list[str] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    created: datetime = field(
        default_factory=datetime.now
    )

    updated: datetime = field(
        default_factory=datetime.now
    )

    identifier: str = field(
        default_factory=lambda: str(uuid4())
    )

    access_count: int = 0

    last_accessed: datetime | None = None

    archived: bool = False

    #
    # ---------------------------------------------------------
    # Memory Operations
    # ---------------------------------------------------------
    #

    def touch(self) -> None:
        """
        Mark the memory as accessed.
        """

        self.access_count += 1

        self.last_accessed = datetime.now()

    def update(
        self,
        value: str
    ) -> None:
        """
        Update the stored value.
        """

        self.value = value

        self.updated = datetime.now()

    def add_tag(
        self,
        tag: str
    ) -> None:

        if tag not in self.tags:

            self.tags.append(tag)

    def remove_tag(
        self,
        tag: str
    ) -> None:

        if tag in self.tags:

            self.tags.remove(tag)

    def archive(self) -> None:

        self.archived = True

    def restore(self) -> None:

        self.archived = False

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def searchable(self) -> bool:

        return self.memory_type.searchable

    @property
    def persistent(self) -> bool:

        return self.memory_type.persistent

    @property
    def ai_visible(self) -> bool:

        return self.memory_type.ai_visible

    @property
    def user_visible(self) -> bool:

        return self.memory_type.user_visible

    #
    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------
    #

    def to_dict(
        self
    ) -> dict:

        return {

            "id": self.identifier,

            "type": self.memory_type.name,

            "topic": self.topic,

            "value": self.value,

            "source": self.source,

            "confidence": self.confidence,

            "tags": self.tags,

            "metadata": self.metadata,

            "created": self.created.isoformat(),

            "updated": self.updated.isoformat(),

            "access_count": self.access_count,

            "archived": self.archived,

        }

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "MemoryRecord("

            f"type={self.memory_type.name}, "

            f"topic='{self.topic}'"

            ")"

        )