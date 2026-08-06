"""
Service Locator
"""

from typing import Any

from core.container.container import Container


class ServiceLocator:
    """
    Global service accessor.
    """

    def __init__(self, container: Container) -> None:
        self._container = container

    def get(self, name: str) -> Any:
        """
        Resolve a service.
        """

        return self._container.resolve(name)

    def has(self, name: str) -> bool:
        """
        Check if a service exists.
        """

        return self._container.contains(name)