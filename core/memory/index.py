"""
Memory Index
"""

from collections import defaultdict


class MemoryIndex:
    """
    Fast category index.
    """

    def __init__(self) -> None:

        self._index: dict[
            str,
            set[str]
        ] = defaultdict(set)

    def add(
        self,
        category: str,
        memory_id: str
    ) -> None:

        self._index[
            category
        ].add(
            memory_id
        )

    def remove(
        self,
        category: str,
        memory_id: str
    ) -> None:

        if category in self._index:

            self._index[
                category
            ].discard(
                memory_id
            )

    def find(
        self,
        category: str
    ) -> list[str]:

        return list(
            self._index.get(
                category,
                set()
            )
        )

    def clear(
        self
    ) -> None:

        self._index.clear()