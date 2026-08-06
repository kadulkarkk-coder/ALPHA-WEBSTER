"""
Webster Alpha

Decision Evaluator
"""

from __future__ import annotations

from core.ai.request import AIRequest

from core.decision.decision import Decision
from core.decision.types import (
    DecisionPriority,
    DecisionReason,
    DecisionType,
)


class DecisionEvaluator:
    """
    Evaluates an AI request and determines
    the most appropriate action.
    """

    def evaluate(
        self,
        request: AIRequest
    ) -> Decision:
        """
        Produce a decision from the request.
        """

        prompt = request.prompt.strip()

        if not prompt:

            return Decision(
                decision_type=DecisionType.REJECT,
                reason=DecisionReason.SYSTEM_EVENT,
                description="Empty request.",
                confidence=1.0
            )

        text = prompt.lower()

        #
        # Memory
        #

        if text.startswith("remember"):

            return Decision(

                decision_type=DecisionType.REMEMBER,

                reason=DecisionReason.USER_REQUEST,

                description="Store information in memory.",

                confidence=1.0

            )

        if text.startswith("what do you remember"):

            return Decision(

                decision_type=DecisionType.RECALL,

                reason=DecisionReason.USER_REQUEST,

                description="Retrieve stored memory.",

                confidence=1.0

            )

        #
        # Search
        #

        if text.startswith("search"):

            return Decision(

                decision_type=DecisionType.SEARCH,

                reason=DecisionReason.USER_REQUEST,

                description="Search for information.",

                confidence=0.95

            )

        #
        # Capability
        #

        capability_keywords = (

            "open",

            "launch",

            "close",

            "shutdown",

            "restart",

            "create folder",

            "delete file"

        )

        if any(

            text.startswith(keyword)

            for keyword in capability_keywords

        ):

            return Decision(

                decision_type=DecisionType.EXECUTE,

                reason=DecisionReason.USER_REQUEST,

                description="Execute system capability.",

                confidence=1.0

            )

        #
        # Clarification
        #

        if len(prompt.split()) <= 1:

            return Decision(

                decision_type=DecisionType.ASK,

                reason=DecisionReason.USER_REQUEST,

                description="More information required.",

                confidence=0.90

            )

        #
        # Default
        #

        return Decision(

            decision_type=DecisionType.AI,

            reason=DecisionReason.USER_REQUEST,

            description="Generate AI response.",

            priority=DecisionPriority.NORMAL,

            confidence=0.95

        )