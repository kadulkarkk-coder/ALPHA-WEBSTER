"""
Webster Alpha

Decision
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from uuid import uuid4

from core.decision.types import (
    DecisionPriority,
    DecisionReason,
    DecisionSource,
    DecisionStatus,
    DecisionType,
)


@dataclass(slots=True, frozen=True)
class Decision:
    """
    Represents a single decision
    made by Webster.
    """

    #
    # Identity
    #

    identifier: str = field(
        default_factory=lambda: str(uuid4())
    )

    created: datetime = field(
        default_factory=datetime.now
    )

    #
    # Decision
    #

    decision_type: DecisionType = DecisionType.NONE

    priority: DecisionPriority = (
        DecisionPriority.NORMAL
    )

    source: DecisionSource = (
        DecisionSource.USER
    )

    reason: DecisionReason = (
        DecisionReason.UNKNOWN
    )

    status: DecisionStatus = (
        DecisionStatus.CREATED
    )

    #
    # Description
    #

    description: str = ""

    confidence: float = 1.0

    #
    # Future Planning
    #

    follow_up: tuple[
        DecisionType,
        ...
    ] = ()

    #
    # Extra information
    #

    metadata: dict = field(
        default_factory=dict
    )

    #
    # -----------------------------------------
    # Validation
    # -----------------------------------------
    #

    def __post_init__(
        self
    ) -> None:

        if not 0.0 <= self.confidence <= 1.0:

            raise ValueError(

                "Confidence must be between "
                "0.0 and 1.0."

            )

    #
    # -----------------------------------------
    # Utilities
    # -----------------------------------------
    #

    @property
    def has_follow_up(
        self
    ) -> bool:

        return len(
            self.follow_up
        ) > 0

    #
    # -----------------------------------------
    # Representation
    # -----------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "Decision("

            f"type={self.decision_type.name}, "

            f"status={self.status.name}, "

            f"confidence={self.confidence:.2f}"

            ")"

        )