"""
Process
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class Process:
    """
    Represents a Webster process.
    """

    name: str

    status: str = "created"

    priority: int = 5

    process_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    started_at: datetime | None = None

    finished_at: datetime | None = None