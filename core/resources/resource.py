"""
Resource
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Resource:
    """
    Represents a Webster resource.
    """

    name: str

    value: Any

    category: str = "general"

    loaded: bool = False

    created_at: datetime = field(
        default_factory=datetime.now
    )

    last_used: datetime = field(
        default_factory=datetime.now
    )