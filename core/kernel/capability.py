"""
Webster Alpha
Capability System

Represents a single executable capability inside Webster.

Every feature exposed by Webster inherits from this class.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any


@dataclass(slots=True)
class CapabilityMetadata:
    """
    Metadata describing a capability.
    """

    name: str

    description: str

    category: str

    version: str = "1.0.0"

    author: str = "Webster Alpha"

    tags: list[str] = field(
        default_factory=list
    )

    requires_ai: bool = False

    requires_network: bool = False

    requires_permission: bool = False


class Capability(
    ABC
):
    """
    Base capability.

    Every executable feature inside Webster
    inherits from this class.
    """

    def __init__(
        self,
        metadata: CapabilityMetadata
    ) -> None:

        self._metadata = metadata

        self._enabled = True

        self._registered = False

        self._created = datetime.now()

        self._last_used: datetime | None = None

        self._usage_count = 0

    #
    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------
    #

    @property
    def metadata(
        self
    ) -> CapabilityMetadata:

        return self._metadata

    @property
    def name(
        self
    ) -> str:

        return self._metadata.name

    @property
    def category(
        self
    ) -> str:

        return self._metadata.category

    @property
    def description(
        self
    ) -> str:

        return self._metadata.description

    @property
    def enabled(
        self
    ) -> bool:

        return self._enabled

    @property
    def registered(
        self
    ) -> bool:

        return self._registered

    @property
    def usage_count(
        self
    ) -> int:

        return self._usage_count

    @property
    def created(
        self
    ) -> datetime:

        return self._created

    @property
    def last_used(
        self
    ) -> datetime | None:

        return self._last_used

    #
    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------
    #

    def register(
        self
    ) -> None:

        self._registered = True

    def unregister(
        self
    ) -> None:

        self._registered = False

    def enable(
        self
    ) -> None:

        self._enabled = True

    def disable(
        self
    ) -> None:

        self._enabled = False

    #
    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    #

    def execute(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Executes the capability.
        """

        if not self._enabled:

            raise RuntimeError(

                f"Capability '{self.name}' is disabled."

            )

        self._usage_count += 1

        self._last_used = datetime.now()

        return self.run(
            *args,
            **kwargs
        )

    @abstractmethod
    def run(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Actual implementation.
        """

        raise NotImplementedError

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    def info(
        self
    ) -> dict[str, Any]:

        return {

            "name": self.name,

            "description": self.description,

            "category": self.category,

            "version": self.metadata.version,

            "author": self.metadata.author,

            "enabled": self.enabled,

            "registered": self.registered,

            "usage_count": self.usage_count,

            "requires_ai": self.metadata.requires_ai,

            "requires_network": self.metadata.requires_network,

            "requires_permission":
                self.metadata.requires_permission,

            "tags": self.metadata.tags,

            "created": self.created,

            "last_used": self.last_used

        }

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(name='{self.name}')"

        )