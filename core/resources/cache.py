"""
Resource Cache
"""

from core.resources.resource import Resource


class ResourceCache:
    """
    In-memory cache for Webster resources.
    """

    def __init__(
        self
    ) -> None:

        self._cache: dict[
            str,
            Resource
        ] = {}

    @property
    def count(
        self
    ) -> int:

        return len(
            self._cache
        )

    def add(
        self,
        resource: Resource
    ) -> None:

        self._cache[
            resource.name
        ] = resource

    def get(
        self,
        name: str
    ) -> Resource:

        return self._cache[
            name
        ]

    def remove(
        self,
        name: str
    ) -> None:

        self._cache.pop(
            name,
            None
        )

    def clear(
        self
    ) -> None:

        self._cache.clear()