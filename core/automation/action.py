"""
Action
"""

from abc import ABC, abstractmethod


class Action(
    ABC
):
    """
    Base automation action.
    """

    @property
    @abstractmethod
    def name(
        self
    ) -> str:

        pass

    @abstractmethod
    def execute(
        self
    ) -> None:

        pass