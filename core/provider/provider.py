"""
Webster Alpha

Base AI Provider
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.ai.request import AIRequest
from core.ai.response import AIResponse


class Provider(ABC):
    """
    Base class for all AI providers.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0",
    ) -> None:

        self._name = name

        self._version = version

        self._enabled = True

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:

        return self._name

    @property
    def version(
        self,
    ) -> str:

        return self._version

    @property
    def enabled(
        self,
    ) -> bool:

        return self._enabled

    # ---------------------------------------------------------

    def enable(
        self,
    ) -> None:

        self._enabled = True

    # ---------------------------------------------------------

    def disable(
        self,
    ) -> None:

        self._enabled = False

    # ---------------------------------------------------------
    # Provider Interface
    # ---------------------------------------------------------

    @abstractmethod
    def initialize(
        self,
    ) -> None:
        """
        Initialize the provider.
        """

    @abstractmethod
    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """
        Generate a response.
        """

    @abstractmethod
    def stream(
        self,
        request: AIRequest,
    ):
        """
        Stream a response.

        Should yield text chunks.
        """

    @abstractmethod
    def available(
        self,
    ) -> bool:
        """
        Returns True if provider
        can currently be used.
        """

    @abstractmethod
    def health(
        self,
    ) -> dict:
        """
        Provider health.
        """

    @abstractmethod
    def shutdown(
        self,
    ) -> None:
        """
        Cleanup resources.
        """

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"name='{self.name}', "

            f"enabled={self.enabled}"

            ")"

        )