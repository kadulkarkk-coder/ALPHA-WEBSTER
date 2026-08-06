"""
Trigger
"""

from abc import ABC, abstractmethod


class Trigger(
    ABC
):
    """
    Base trigger.
    """

    @property
    @abstractmethod
    def name(
        self
    ) -> str:

        pass

    @abstractmethod
    def check(
        self
    ) -> bool:

        pass