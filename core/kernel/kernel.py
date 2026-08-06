"""
Webster Alpha

Kernel

The operating core of Webster Alpha.

Everything in Webster is coordinated
through the Kernel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from core.container.service_registry import ServiceRegistry
from core.kernel.boot import Boot
from core.kernel.capability_registry import CapabilityRegistry
from core.kernel.component import Component
from core.kernel.component_registry import ComponentRegistry
from core.kernel.dependency import ComponentInfo
from core.kernel.dependency_graph import DependencyGraph
from core.kernel.lifecycle import Lifecycle


class Kernel:
    """
    Webster Kernel.
    """

    def __init__(self) -> None:

        #
        # Registries
        #

        self._components = ComponentRegistry()

        self._services = ServiceRegistry()

        self._capabilities = CapabilityRegistry()

        #
        # Managers
        #

        self._lifecycle = Lifecycle(
            self._components
        )

        self._dependencies = DependencyGraph(
            self._components
        )

        self._boot = Boot(
            self._lifecycle
        )

        #
        # Runtime
        #

        self._running = False

        self._started: datetime | None = None

    # =========================================================
    # Properties
    # =========================================================

    @property
    def running(self) -> bool:
        return self._running

    @property
    def components(self) -> ComponentRegistry:
        return self._components

    @property
    def services(self) -> ServiceRegistry:
        return self._services

    @property
    def capabilities(self) -> CapabilityRegistry:
        return self._capabilities

    @property
    def lifecycle(self) -> Lifecycle:
        return self._lifecycle

    @property
    def dependency_graph(self) -> DependencyGraph:
        return self._dependencies

    # =========================================================
    # Component Registration
    # =========================================================

    def register_component(
        self,
        component: Component,
        info: ComponentInfo,
    ) -> None:

        self._components.register(
            component,
            info,
        )

    def unregister_component(
        self,
        name: str,
    ) -> None:

        self._components.unregister(
            name
        )

    # =========================================================
    # Service Registration
    # =========================================================

    def register_service(
        self,
        name: str,
        service: Any,
        **kwargs,
    ) -> None:

        self._services.register(
            name,
            service,
            **kwargs,
        )

    # =========================================================
    # Boot
    # =========================================================

    def start(self) -> None:

        if self._running:
            return

        errors = self._dependencies.validate()

        if errors:

            raise RuntimeError(
                "\n".join(errors)
            )

        ordered = self._dependencies.startup_order()

        self._boot.boot(

            [

                registration.component

                for registration

                in ordered

                if registration.enabled

            ]

        )

        self._running = True

        self._started = datetime.now()

    # =========================================================
    # Shutdown
    # =========================================================

    def shutdown(self) -> None:

        if not self._running:
            return

        ordered = self._dependencies.shutdown_order()

        self._boot.shutdown(

            [

                registration.component

                for registration

                in ordered

                if registration.enabled

            ]

        )

        self._running = False

    # =========================================================
    # Restart
    # =========================================================

    def restart(self) -> None:

        self.shutdown()

        self.start()

    # =========================================================
    # Capability Execution
    # =========================================================

    def execute(
        self,
        capability: str,
        *args,
        **kwargs,
    ):

        return self._capabilities.execute(

            capability,

            *args,

            **kwargs,

        )

    # =========================================================
    # Diagnostics
    # =========================================================

    def diagnostics(self) -> dict:

        return {

            "running": self.running,

            "started": self._started,

            "components":

                self.components.count,

            "services":

                self.services.count,

            "capabilities":

                self.capabilities.capability_count,

            "healthy":

                self.lifecycle.healthy(),

        }

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:

        return (

            "Kernel("

            f"components={self.components.count}, "

            f"services={self.services.count}, "

            f"capabilities={self.capabilities.capability_count}, "

            f"running={self.running}"

            ")"

        )