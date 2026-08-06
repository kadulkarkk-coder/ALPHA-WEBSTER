"""
Task
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from uuid import uuid4


@dataclass(slots=True)
class Task:
    """
    Represents a scheduled task.
    """

    name: str

    callback: Callable[[], None]

    interval: float = 0.0

    repeat: bool = False

    enabled: bool = True

    task_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )