"""
Webster Alpha

Memory Query

Defines a structured query used to
search the Webster Memory Store.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.memory.types import MemoryType


@dataclass(slots=True)
class MemoryQuery:
    """
    Structured memory search query.
    """

    #
    # Search
    #

    text: str = ""

    topic: str = ""

    memory_type: MemoryType | None = None

    #
    # Filters
    #

    tags: list[str] = field(
        default_factory=list
    )

    source: str | None = None

    minimum_confidence: float = 0.0

    include_archived: bool = False

    #
    # Limits
    #

    limit: int = 25

    exact_match: bool = False

    case_sensitive: bool = False

    #
    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    #

    def validate(
        self
    ) -> None:

        if self.limit <= 0:

            raise ValueError(

                "Limit must be greater than zero."

            )

        if not 0.0 <= self.minimum_confidence <= 1.0:

            raise ValueError(

                "Confidence must be between 0 and 1."

            )

    #
    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    #

    @property
    def empty(
        self
    ) -> bool:

        return not any(

            [

                self.text,

                self.topic,

                self.memory_type,

                self.tags,

                self.source,

            ]

        )

    def copy(
        self
    ) -> "MemoryQuery":

        return MemoryQuery(

            text=self.text,

            topic=self.topic,

            memory_type=self.memory_type,

            tags=self.tags.copy(),

            source=self.source,

            minimum_confidence=self.minimum_confidence,

            include_archived=self.include_archived,

            limit=self.limit,

            exact_match=self.exact_match,

            case_sensitive=self.case_sensitive,

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

            "MemoryQuery("

            f"text='{self.text}', "

            f"type={self.memory_type}"

            ")"

        )