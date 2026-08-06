"""
Webster Alpha

Application Capability Pack
"""

from __future__ import annotations

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry

from core.capability.application.calculator import (
    CalculatorCapability,
)

from core.capability.application.notepad import (
    NotepadCapability,
)

from core.capability.application.explorer import (
    ExplorerCapability,
)

from core.capability.application.task_manager import (
    TaskManagerCapability,
)


class ApplicationPack(CapabilityPack):
    """
    Registers desktop application
    capabilities.
    """

    @property
    def name(self) -> str:

        return "applications"

    @property
    def version(self) -> str:

        return "1.0.0"

    def register(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        registry.register(
            CalculatorCapability()
        )

        registry.register(
            NotepadCapability()
        )

        registry.register(
            ExplorerCapability()
        )

        registry.register(
            TaskManagerCapability()
        )