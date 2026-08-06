"""
Resource Manager
"""

from core.resources.cache import ResourceCache
from core.resources.monitor import ResourceMonitor
from core.resources.resource import Resource


class ResourceManager:
    """
    Controls Webster resources.
    """

    def __init__(
        self
    ) -> None:

        self._cache = ResourceCache()

        self._monitor = ResourceMonitor()

    @property
    def count(
        self
    ) -> int:

        return self._cache.count

    def add(
        self,
        resource: Resource
    ) -> None:

        resource.loaded = True

        self._cache.add(
            resource
        )

    def get(
        self,
        name: str
    ) -> Resource:

        resource = self._cache.get(
            name
        )

        self._monitor.touch(
            resource
        )

        return resource

    def remove(
        self,
        name: str
    ) -> None:

        resource = self._cache.get(
            name
        )

        resource.loaded = False

        self._cache.remove(
            name
        )

    def usage(
        self,
        name: str
    ) -> int:

        return self._monitor.usage(
            name
        )

    def clear(
        self
    ) -> None:

        self._cache.clear()

        self._monitor.reset()