"""
Base Event
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Event:
    """
    Base event object.
    """

    name: str

    source: str

    data: dict[str, Any]

    timestamp: datetime = datetime.now()