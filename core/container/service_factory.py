"""
Service Factory
"""

from typing import Callable, TypeVar

T = TypeVar("T")


class ServiceFactory:
    """
    Creates service instances.
    """

    @staticmethod
    def create(factory: Callable[[], T]) -> T:
        """
        Create and return a service instance.
        """
        return factory()