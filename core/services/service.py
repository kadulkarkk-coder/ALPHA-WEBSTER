"""
Base Service
"""

from abc import ABC, abstractmethod


class Service(ABC):
    """
    Base class for every Webster service.
    """

    def __init__(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        """
        Return the running state.
        """
        return self._running

    @abstractmethod
    def start(self) -> None:
        """
        Start the service.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the service.
        """