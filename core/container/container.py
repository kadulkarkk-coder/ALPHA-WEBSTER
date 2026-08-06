"""
Dependency Injection Container
"""

from typing import Any


class Container:
    """
    Stores and resolves singleton services.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """
        Register a singleton service.
        """

        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered.")

        self._services[name] = service

    def resolve(self, name: str) -> Any:
        """
        Resolve a registered service.
        """

        if name not in self._services:
            raise KeyError(f"Service '{name}' is not registered.")

        return self._services[name]

    def unregister(self, name: str) -> None:
        """
        Remove a registered service.
        """

        if name in self._services:
            del self._services[name]

    def contains(self, name: str) -> bool:
        """
        Check if a service exists.
        """

        return name in self._services

    def clear(self) -> None:
        """
        Remove all registered services.
        """

        self._services.clear()