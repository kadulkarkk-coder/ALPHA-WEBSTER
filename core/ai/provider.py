"""
Webster Alpha

AI Provider

Abstract interface implemented by
all AI providers.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.ai.request import AIRequest
from core.ai.response import AIResponse
from core.ai.types import AIProvider
from core.ai.types import AIStatus


class Provider(ABC):
    """
    Base class for every AI provider.
    """

    def __init__(
        self,
        provider: AIProvider
    ) -> None:

        self._provider = provider

        self._status = AIStatus.OFFLINE

    #
    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------
    #

    @abstractmethod
    def initialize(
        self
    ) -> None:
        """
        Initialize the provider.
        """

    @abstractmethod
    def shutdown(
        self
    ) -> None:
        """
        Shutdown the provider.
        """

    #
    # ---------------------------------------------------------
    # Requests
    # ---------------------------------------------------------
    #

    @abstractmethod
    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:
        """
        Generate an AI response.
        """

    #
    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------
    #

    @abstractmethod
    def healthy(
        self
    ) -> bool:
        """
        Check provider health.
        """

    #
    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------
    #

    @property
    def provider(
        self
    ) -> AIProvider:

        return self._provider

    @property
    def status(
        self
    ) -> AIStatus:

        return self._status

    @status.setter
    def status(
        self,
        value: AIStatus
    ) -> None:

        self._status = value

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    @property
    def ready(
        self
    ) -> bool:

        return self._status == AIStatus.READY

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"provider={self.provider.name}, "

            f"status={self.status.name}"

            ")"

        )