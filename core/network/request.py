"""
Request
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Request:
    """
    Represents a network request.
    """

    method: str

    url: str

    headers: dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    params: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    body: Any = None