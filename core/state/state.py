"""
State
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class State:
    """
    Represents a single state object.
    """

    name: str

    value: Any

    mutable: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )