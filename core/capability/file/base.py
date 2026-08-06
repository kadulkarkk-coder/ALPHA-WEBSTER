"""
Webster Alpha

Base File System Capability
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest


class FileSystemCapability(Capability, ABC):
    """
    Base class for all filesystem capabilities.

    Provides common helper methods for resolving
    paths and extracting arguments from requests.
    """

    def get_path(
        self,
        request: CapabilityRequest,
        key: str = "path",
    ) -> Path:
        """
        Resolve a filesystem path from the request.

        Raises:
            KeyError: If the key is missing.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        return Path(str(value)).expanduser().resolve()

    def get_text(
        self,
        request: CapabilityRequest,
        key: str = "text",
    ) -> str:
        """
        Retrieve a text argument.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        return str(value)

    def get_string(
        self,
        request: CapabilityRequest,
        key: str,
    ) -> str:
        """
        Retrieve any string argument.
        """

        value = request.arguments.get(key)

        if value is None:
            raise KeyError(
                f"Missing required argument '{key}'."
            )

        return str(value)

    def get_boolean(
        self,
        request: CapabilityRequest,
        key: str,
        default: bool = False,
    ) -> bool:
        """
        Retrieve a boolean argument.
        """

        return bool(
            request.arguments.get(
                key,
                default,
            )
        )

    def ensure_exists(
        self,
        path: Path,
    ) -> None:
        """
        Ensure a path exists.
        """

        if not path.exists():

            raise FileNotFoundError(
                f"'{path}' does not exist."
            )

    def ensure_file(
        self,
        path: Path,
    ) -> None:
        """
        Ensure a path is a file.
        """

        self.ensure_exists(path)

        if not path.is_file():

            raise IsADirectoryError(
                f"'{path}' is not a file."
            )

    def ensure_directory(
        self,
        path: Path,
    ) -> None:
        """
        Ensure a path is a directory.
        """

        self.ensure_exists(path)

        if not path.is_dir():

            raise NotADirectoryError(
                f"'{path}' is not a directory."
            )

    def ensure_parent(
        self,
        path: Path,
    ) -> None:
        """
        Create parent directories if needed.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )