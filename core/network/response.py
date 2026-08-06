"""
Response
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Response:
    """
    Represents a network response.
    """

    status: int

    body: Any = None

    headers: dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    success: bool = True