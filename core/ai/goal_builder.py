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

    This class does NOT perform planning.

    It only converts natural language
    into a structured Goal object.
    """

    def build(
        self,
        message: str,
        intent: Intent,
    ) -> Goal:
        """
        Build a Goal from the user message.
        """

        return Goal(

            title=self._title(message),

            description=message.strip(),

            category=self._category(intent),

            metadata={

                "intent": intent.intent.name,

                "confidence": intent.confidence,

                "source": "ai",

            }

        )

    # -----------------------------------------------------

    def _title(
        self,
        message: str,
    ) -> str:

        text = message.strip()

        if not text:

            return "Untitled Goal"

        if len(text) <= 60:

            return text

        return text[:57] + "..."

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