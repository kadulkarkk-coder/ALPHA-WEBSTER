"""
Webster Alpha

Base System Capability
"""

from __future__ import annotations

import platform
from abc import ABC
from pathlib import Path

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest


class SystemCapability(Capability, ABC):
    """
    Base class for all system capabilities.
    """

    def get_path(
        self,
        request: CapabilityRequest,
        key: str = "path",
    ) -> Path:
        """
        Return a filesystem path.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        return Path(value).expanduser()

    def get_existing_path(
        self,
        request: CapabilityRequest,
        key: str = "path",
    ) -> Path:
        """
        Return an existing filesystem path.
        """

        path = self.get_path(
            request,
            key,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"'{path}' does not exist."
            )

        return path

    def get_command(
        self,
        request: CapabilityRequest,
        key: str = "command",
    ) -> str:
        """
        Return a shell command.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        command = str(value).strip()

        if not command:
            raise ValueError(
                "Command cannot be empty."
            )

        return command

    def get_process_name(
        self,
        request: CapabilityRequest,
        key: str = "process",
    ) -> str:
        """
        Return a process name.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        process = str(value).strip()

        if not process:
            raise ValueError(
                "Process name cannot be empty."
            )

        return process

    @property
    def operating_system(self) -> str:
        """
        Return the current operating system.
        """

        return platform.system()

    @property
    def is_windows(self) -> bool:

        return self.operating_system == "Windows"

    @property
    def is_linux(self) -> bool:

        return self.operating_system == "Linux"

    @property
    def is_macos(self) -> bool:

        return self.operating_system == "Darwin"