"""
Plugin
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    """
    Base class for every Webster plugin.
    """

    def __init__(
        self,
        name: str,
        version: str
    ) -> None:

        self._name = name

        self._version = version

        self._enabled = False

    @property
    def name(
        self
    ) -> str:

        return self._name

    @property
    def version(
        self
    ) -> str:

        return self._version

    @property
    def enabled(
        self
    ) -> bool:

        return self._enabled

    def enable(
        self
    ) -> None:

        self._enabled = True

    def disable(
        self
    ) -> None:

        self._enabled = False

    @abstractmethod
    def start(
        self
    ) -> None:

        pass

    @abstractmethod
    def stop(
        self
    ) -> None:

        pass