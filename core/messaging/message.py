"""
Message
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Any


@dataclass(slots=True)
class Message:
    """
    Represents an internal Webster message.
    """

    sender: str

    receiver: str

    payload: Any

    message_type: str = "general"

    message_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    timestamp: datetime = field(
        default_factory=datetime.now
    )