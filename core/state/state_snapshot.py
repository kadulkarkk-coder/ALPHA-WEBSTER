"""
State Snapshot
"""

from copy import deepcopy
from datetime import datetime
from typing import Any


class StateSnapshot:
    """
    Immutable snapshot of Webster's state.
    """

    def __init__(
        self,
        states: dict[str, Any]
    ) -> None:

        self.timestamp = datetime.now()

        self.states = deepcopy(
            states
        )