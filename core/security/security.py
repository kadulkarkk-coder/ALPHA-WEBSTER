"""
Security Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class SecurityContext:
    """
    Represents a Webster security session.
    """

    session_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    authenticated: bool = False

    permission_level: str = "user"

    created_at: datetime = field(
        default_factory=datetime.now
    )