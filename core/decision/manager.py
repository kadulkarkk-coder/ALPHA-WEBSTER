"""
Webster Alpha

Decision Manager
"""

from __future__ import annotations

from core.ai.request import AIRequest

from core.decision.decision import Decision
from core.decision.evaluator import DecisionEvaluator
from core.decision.policy import (
    PolicyConfiguration,
    PolicyEngine,
)


class DecisionManager:
    """
    Coordinates Webster's
    Decision Engine.
    """

    def __init__(
        self,
        evaluator: DecisionEvaluator | None = None,
        policy: PolicyEngine | None = None,
    ) -> None:

        self._evaluator = (
            evaluator
            or
            DecisionEvaluator()
        )

        self._policy = (
            policy
            or
            PolicyEngine(
                PolicyConfiguration()
            )
        )

    #
    # ---------------------------------------------------------
    # Decision Pipeline
    # ---------------------------------------------------------
    #

    def decide(
        self,
        request: AIRequest
    ) -> Decision:
        """
        Evaluate a request and
        apply policies.
        """

        #
        # Step 1
        #

        decision = self._evaluator.evaluate(
            request
        )

        #
        # Step 2
        #

        decision = self._policy.evaluate(
            decision
        )

        return decision

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def evaluator(
        self
    ) -> DecisionEvaluator:

        return self._evaluator

    @property
    def policy(
        self
    ) -> PolicyEngine:

        return self._policy

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "DecisionManager("

            f"policy={self.policy!r}"

            ")"

        )