"""
Extension
"""

from abc import ABC, abstractmethod


class Extension(ABC):
    """
    Base class for every Webster extension.
    """

    def __init__(
        self,
        name: str,
        version: str
    ) -> None:

        self._name = name

        self._version = version

        self._loaded = False

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
    def loaded(
        self
    ) -> bool:

        return self._loaded

    def load(
        self
    ) -> None:

        self._loaded = True

    def unload(
        self
    ) -> None:

        self._loaded = False

    @abstractmethod
    def initialize(
        self
    ) -> None:

        pass

    @abstractmethod
    def shutdown(
        self
    ) -> None:

        pass