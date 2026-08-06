"""
Webster Alpha

System Capability Pack
"""

from __future__ import annotations

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry

from core.capability.system.launch_app import LaunchApplicationCapability
from core.capability.system.terminate_app import TerminateApplicationCapability
from core.capability.system.list_processes import ListProcessesCapability
from core.capability.system.kill_process import KillProcessCapability
from core.capability.system.open_folder import OpenFolderCapability
from core.capability.system.execute_command import ExecuteCommandCapability
from core.capability.system.clipboard import ClipboardCapability
from core.capability.system.notification import NotificationCapability
from core.capability.system.system_info import SystemInfoCapability
from core.capability.system.power import PowerCapability


class SystemPack(CapabilityPack):
    """\\\
    Registers all system capabilities.
    """

    @property
    def name(self) -> str:
        return "system"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        registry.register(
            LaunchApplicationCapability()
        )

        registry.register(
            TerminateApplicationCapability()
        )

        registry.register(
            ListProcessesCapability()
        )

        registry.register(
            KillProcessCapability()
        )

        registry.register(
            OpenFolderCapability()
        )

        registry.register(
            ExecuteCommandCapability()
        )

        registry.register(
            ClipboardCapability()
        )

        registry.register(
            NotificationCapability()
        )

        registry.register(
            SystemInfoCapability()
        )

        registry.register(
            PowerCapability()
        )