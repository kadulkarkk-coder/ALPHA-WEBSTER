"""
Webster Alpha

Goal Builder
"""

from __future__ import annotations

from core.ai.router import Intent
from core.planning.goal import Goal


class GoalBuilder:
    """
    Converts an Intent into a Planning Goal.
    """

    def build(
        self,
        message: str,
        intent: Intent,
    ) -> Goal:
        """Build a Goal using the project's actual Goal model."""

        return Goal(
            objective=message.strip(),
            priority=0,
            metadata={
                "intent": intent.intent.name,
                "confidence": intent.confidence,
                "category": self._category(intent),
                "source": "ai",
            },
        )

    # -----------------------------------------------------

    def _category(
        self,
        intent: Intent,
    ) -> str:

        if intent.category:

            return intent.category

        return intent.intent.name.lower()

    # -----------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {
            "healthy": True,
            "builder": "GoalBuilder",
        }

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return "GoalBuilder()"
