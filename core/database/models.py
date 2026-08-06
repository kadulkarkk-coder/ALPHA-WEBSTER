"""
Database Models
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Table:
    """
    Database table.
    """

    name: str

    schema: str