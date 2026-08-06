"""
Diagnostic Report
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class DiagnosticReport:
    """
    Complete Webster diagnostic report.
    """

    generated_at: datetime = field(
        default_factory=datetime.now
    )

    system: dict[str, Any] = field(
        default_factory=dict
    )

    performance: dict[str, Any] = field(
        default_factory=dict
    )

    health: dict[str, Any] = field(
        default_factory=dict
    )