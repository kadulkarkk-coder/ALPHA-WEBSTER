"""
Credential Vault
"""

from typing import Any


class Vault:
    """
    Stores sensitive values in memory.
    """

    def __init__(self) -> None:

        self._items: dict[
            str,
            Any
        ] = {}

    @property
    def count(
        self
    ) -> int:

        return len(
            self._items
        )

    def store(
        self,
        key: str,
        value: Any
    ) -> None:

        self._items[
            key
        ] = value

    def get(
        self,
        key: str
    ) -> Any:

        return self._items.get(
            key
        )

    def remove(
        self,
        key: str
    ) -> None:

        self._items.pop(
            key,
            None
        )

    def clear(
        self
    ) -> None:

        self._items.clear()