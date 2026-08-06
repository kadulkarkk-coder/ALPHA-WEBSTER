"""
Extension Registry
"""

from core.extensions.extension import Extension


class ExtensionRegistry:
    """
    Stores loaded extensions.
    """

    def __init__(
        self
    ) -> None:

        self._extensions: dict[
            str,
            Extension
        ] = {}

    @property
    def count(
        self
    ) -> int:

        return len(
            self._extensions
        )

    def register(
        self,
        extension: Extension
    ) -> None:

        self._extensions[
            extension.name
        ] = extension

    def unregister(
        self,
        name: str
    ) -> None:

        self._extensions.pop(
            name,
            None
        )

    def get(
        self,
        name: str
    ) -> Extension:

        return self._extensions[
            name
        ]

    def all(
        self
    ) -> list[Extension]:

        return list(
            self._extensions.values()
        )