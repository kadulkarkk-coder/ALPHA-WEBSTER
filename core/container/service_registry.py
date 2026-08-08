"""
Webster Alpha

Service Registry
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ServiceEntry:
    """
    Represents one registered Webster service.
    """

    name: str

    service: Any

    description: str = ""


class ServiceRegistry:
    """
    Central registry for Webster services.

    Responsibilities
    ----------------

    • Register services
    • Unregister services
    • Retrieve services
    • Check service availability
    • Track lifecycle state
    • Provide registry health information
    """

    # =====================================================
    # Construction
    # =====================================================

    def __init__(
        self,
    ) -> None:
        """
        Create an empty service registry.

        Services are registered later during
        Webster initialization.
        """

        self._services: dict[
            str,
            ServiceEntry,
        ] = {}

        self._initialized = False

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the service registry.

        The registry itself does not need external
        resources, so initialization establishes its
        operational state and validates the registry.
        """

        if self._initialized:

            return

        #
        # Ensure the internal service container exists.
        #

        if self._services is None:

            self._services = {}

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the service registry.

        Registered services are removed so that a future
        initialization starts from a clean runtime state.
        """

        if not self._initialized:

            return

        self._services.clear()

        self._initialized = False

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    @property
    def ready(
        self,
    ) -> bool:

        return self._initialized

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        name: str,
        service: Any,
        description: str = "",
    ) -> None:
        """
        Register a service.

        Parameters
        ----------
        name:
            Unique service name.

        service:
            Service instance.

        description:
            Optional human-readable description.
        """

        if not self._initialized:

            raise RuntimeError(
                "ServiceRegistry must be initialized "
                "before registering services."
            )

        if not name.strip():

            raise ValueError(
                "Service name cannot be empty."
            )

        key = name.strip().lower()

        self._services[key] = ServiceEntry(

            name=key,

            service=service,

            description=description,

        )

    # -----------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered service.
        """

        key = name.strip().lower()

        self._services.pop(

            key,

            None,

        )

    # =====================================================
    # Lookup
    # =====================================================

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Return a registered service.
        """

        key = name.strip().lower()

        entry = self._services.get(

            key

        )

        if entry is None:

            raise KeyError(

                f"Service '{name}' is not registered."

            )

        return entry.service

    # -----------------------------------------------------

    def find(
        self,
        name: str,
    ) -> Any | None:
        """
        Return a service if it exists.

        Unlike get(), this method does not raise an
        exception when the service is missing.
        """

        key = name.strip().lower()

        entry = self._services.get(

            key

        )

        if entry is None:

            return None

        return entry.service

    # -----------------------------------------------------

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a service is registered.
        """

        key = name.strip().lower()

        return key in self._services

    # =====================================================
    # Enumeration
    # =====================================================

    def names(
        self,
    ) -> list[str]:
        """
        Return the names of all registered services.
        """

        return list(

            self._services.keys()

        )

    # -----------------------------------------------------

    def services(
        self,
    ) -> dict[str, Any]:
        """
        Return a snapshot of registered services.
        """

        return {

            name: entry.service

            for name, entry
            in self._services.items()

        }

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def service_count(
        self,
    ) -> int:

        return len(

            self._services

        )

    @property
    def count(
        self,
    ) -> int:

        return self.service_count

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return service registry health information.
        """

        return {

            "initialized": self._initialized,

            "healthy": self._initialized,

            "services": self.service_count,

        }

    # =====================================================
    # Clear
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all registered services without
        shutting down the registry itself.
        """

        self._services.clear()

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            "ServiceRegistry("

            f"initialized={self._initialized}, "

            f"services={self.service_count}"

            ")"

        )