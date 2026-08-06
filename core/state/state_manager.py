"""
State Manager
"""

from typing import Any

from core.state.state import State
from core.state.state_snapshot import StateSnapshot


class StateManager:
    """
    Webster state manager.
    """

    def __init__(self) -> None:

        self._states: dict[str, State] = {}

    @property
    def count(self) -> int:

        return len(
            self._states
        )

    def register(
        self,
        state: State
    ) -> None:

        if state.name in self._states:

            raise ValueError(
                f"State '{state.name}' already exists."
            )

        self._states[
            state.name
        ] = state

    def get(
        self,
        name: str
    ) -> Any:

        return self._states[
            name
        ].value

    def update(
        self,
        name: str,
        value: Any
    ) -> None:

        self._states[
            name
        ].value = value

    def snapshot(
        self
    ) -> StateSnapshot:

        values = {}

        for key, state in self._states.items():

            values[key] = state.value

        return StateSnapshot(
            values
        )

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._states

    def remove(
        self,
        name: str
    ) -> None:

        self._states.pop(
            name,
            None
        )

    def clear(
        self
    ) -> None:

        self._states.clear()