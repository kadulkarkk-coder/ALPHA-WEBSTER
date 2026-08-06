"""
Webster Alpha

Memory Store

Central storage for all memory records.
"""

from __future__ import annotations

from collections.abc import Iterator

from core.memory.query import MemoryQuery
from core.memory.record import MemoryRecord


class MemoryStore:
    """
    Webster Memory Store.
    """

    def __init__(
        self
    ) -> None:

        self._records: dict[
            str,
            MemoryRecord
        ] = {}

    #
    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------
    #

    def add(
        self,
        record: MemoryRecord
    ) -> None:

        self._records[
            record.identifier
        ] = record

    def remove(
        self,
        identifier: str
    ) -> MemoryRecord | None:

        return self._records.pop(
            identifier,
            None
        )

    def clear(
        self
    ) -> None:

        self._records.clear()

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        identifier: str
    ) -> MemoryRecord | None:

        record = self._records.get(
            identifier
        )

        if record:

            record.touch()

        return record

    def exists(
        self,
        identifier: str
    ) -> bool:

        return identifier in self._records

    #
    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------
    #

    def search(
        self,
        query: MemoryQuery
    ) -> list[MemoryRecord]:

        query.validate()

        results: list[
            MemoryRecord
        ] = []

        for record in self._records.values():

            if not query.include_archived:

                if record.archived:

                    continue

            if query.memory_type:

                if record.memory_type != query.memory_type:

                    continue

            if query.source:

                if record.source != query.source:

                    continue

            if record.confidence < query.minimum_confidence:

                continue

            #
            # Topic
            #

            if query.topic:

                if query.exact_match:

                    if record.topic != query.topic:

                        continue

                else:

                    left = record.topic
                    right = query.topic

                    if not query.case_sensitive:

                        left = left.lower()
                        right = right.lower()

                    if right not in left:

                        continue

            #
            # Text
            #

            if query.text:

                value = record.value
                search = query.text

                if not query.case_sensitive:

                    value = value.lower()
                    search = search.lower()

                if query.exact_match:

                    if value != search:

                        continue

                else:

                    if search not in value:

                        continue

            #
            # Tags
            #

            if query.tags:

                if not all(

                    tag in record.tags

                    for tag

                    in query.tags

                ):

                    continue

            record.touch()

            results.append(
                record
            )

            if len(results) >= query.limit:

                break

        return results

    #
    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    #

    @property
    def count(
        self
    ) -> int:

        return len(
            self._records
        )

    @property
    def archived(
        self
    ) -> int:

        return sum(

            record.archived

            for record

            in self._records.values()

        )

    @property
    def active(
        self
    ) -> int:

        return self.count - self.archived

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def records(
        self
    ) -> list[MemoryRecord]:

        return list(
            self._records.values()
        )

    #
    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------
    #

    def __len__(
        self
    ) -> int:

        return self.count

    def __contains__(
        self,
        identifier: str
    ) -> bool:

        return self.exists(
            identifier
        )

    def __iter__(
        self
    ) -> Iterator[
        MemoryRecord
    ]:

        return iter(
            self._records.values()
        )

    def __repr__(
        self
    ) -> str:

        return (

            "MemoryStore("

            f"records={self.count}"

            ")"

        )