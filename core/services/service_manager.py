"""
Service Manager
"""

from core.services.service import Service


class ServiceManager:
    """
    Controls Webster services.
    """

    def __init__(self) -> None:

        self._services: dict[str, Service] = {}

    @property
    def count(self) -> int:
        """
        Number of registered services.
        """

        return len(self._services)

    def register(
        self,
        name: str,
        service: Service
    ) -> None:
        """
        Register a service.
        """

        if name in self._services:

            raise ValueError(
                f"Service '{name}' already exists."
            )

        self._services[name] = service

    def unregister(
        self,
        name: str
    ) -> None:
        """
        Remove a service.
        """

        if name in self._services:

            del self._services[name]

    def get(
        self,
        name: str
    ) -> Service:
        """
        Retrieve a service.
        """

        if name not in self._services:

            raise KeyError(
                f"Service '{name}' not found."
            )

        return self._services[name]

    def contains(
        self,
        name: str
    ) -> bool:
        """
        Check whether a service exists.
        """

        return name in self._services

    def clear(self) -> None:
        """
        Remove every service.
        """

        self._services.clear()