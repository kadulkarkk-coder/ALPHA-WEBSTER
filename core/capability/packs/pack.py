"""
Webster Alpha

Capability Pack
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.capability.registry import CapabilityRegistry


class CapabilityPack(ABC):
    """
    Base class for all capability packs.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Human-readable pack name.
        """
        raise NotImplementedError

    @property
    def version(
        self,
    ) -> str:
        """
        Pack version.
        """

        return "1.0.0"

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Whether this pack should
        be loaded.
        """

        return True

    @abstractmethod
    def register(
        self,
        registry: CapabilityRegistry,
    ) -> None:
        """
        Register this pack's
        capabilities.
        """

        raise NotImplementedError

    def unregister(
        self,
        registry: CapabilityRegistry,
    ) -> None:
        """
        Optional cleanup.
        """

        return None

    def __repr__(
        self,
    ) -> str:

        return (

            "CapabilityPack("

            f"name='{self.name}', "

            f"version='{self.version}'"

            ")"

        )