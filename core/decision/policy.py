"""
Webster Alpha

Decision Policy Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.decision.decision import Decision
from core.decision.types import (
    DecisionType,
    DecisionReason,
)


@dataclass(slots=True)
class PolicyConfiguration:
    """
    Global policy configuration.
    """

    allow_ai: bool = True

    allow_capabilities: bool = True

    allow_memory: bool = True

    allow_search: bool = True

    offline_mode: bool = False

    developer_mode: bool = False

    metadata: dict = field(
        default_factory=dict
    )


class PolicyEngine:
    """
    Validates decisions against
    Webster's active policies.
    """

    def __init__(
        self,
        configuration: PolicyConfiguration | None = None
    ) -> None:

        self._configuration = (
            configuration
            or
            PolicyConfiguration()
        )

    #
    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------
    #

    def evaluate(
        self,
        decision: Decision
    ) -> Decision:
        """
        Apply policies to a decision.
        """

        #
        # AI disabled
        #

        if (
            decision.decision_type
            == DecisionType.AI
            and
            not self._configuration.allow_ai
        ):

            return self._reject(
                "AI usage is disabled."
            )

        #
        # Memory disabled
        #

        if (
            decision.decision_type
            in (
                DecisionType.REMEMBER,
                DecisionType.RECALL,
            )
            and
            not self._configuration.allow_memory
        ):

            return self._reject(
                "Memory is disabled."
            )

        #
        # Capability execution disabled
        #

        if (
            decision.decision_type
            == DecisionType.EXECUTE
            and
            not self._configuration.allow_capabilities
        ):

            return self._reject(
                "Capabilities are disabled."
            )

        #
        # Search disabled
        #

        if (
            decision.decision_type
            == DecisionType.SEARCH
            and
            not self._configuration.allow_search
        ):

            return self._reject(
                "Search is disabled."
            )

        #
        # Offline mode
        #

        if (
            self._configuration.offline_mode
            and
            decision.decision_type
            == DecisionType.SEARCH
        ):

            return self._reject(
                "Search unavailable in offline mode."
            )

        return decision

    #
    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    #

    def _reject(
        self,
        description: str
    ) -> Decision:

        return Decision(

            decision_type=DecisionType.REJECT,

            reason=DecisionReason.POLICY_RULE,

            description=description,

            confidence=1.0

        )

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def configuration(
        self
    ) -> PolicyConfiguration:

        return self._configuration

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "PolicyEngine("

            f"offline={self.configuration.offline_mode}, "

            f"developer={self.configuration.developer_mode}"

            ")"

        )