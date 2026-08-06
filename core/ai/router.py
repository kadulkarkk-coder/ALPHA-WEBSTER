"""
Webster Alpha

Intent Router
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class IntentType(Enum):
    """
    Supported user intent types.
    """

    CHAT = auto()

    ACTION = auto()

    QUESTION = auto()

    FILE = auto()

    BROWSER = auto()

    SYSTEM = auto()

    SEARCH = auto()

    WORKFLOW = auto()

    UNKNOWN = auto()


@dataclass(slots=True, frozen=True)
class Intent:
    """
    Represents the detected intent.
    """

    intent: IntentType

    confidence: float

    action: str | None = None

    category: str | None = None

    metadata: dict[str, object] | None = None

    @property
    def is_action(self) -> bool:

        return self.intent in {

            IntentType.ACTION,

            IntentType.FILE,

            IntentType.BROWSER,

            IntentType.SYSTEM,

            IntentType.WORKFLOW,

        }

    @property
    def is_chat(self) -> bool:

        return self.intent == IntentType.CHAT

    @property
    def is_question(self) -> bool:

        return self.intent == IntentType.QUESTION


class IntentRouter:
    """
    Detects the user's intent.

    This is currently rule-based and can later
    be replaced by an LLM-powered classifier.
    """

    def __init__(self) -> None:

        self._patterns: list[tuple[IntentType, str, str]] = [

            (
                IntentType.FILE,
                r"\b(create|make|delete|remove|rename|move|copy|read|write|open)\b.*\b(file|folder|directory)\b",
                "file",
            ),

            (
                IntentType.BROWSER,
                r"\b(open|search|browse|visit|go to)\b",
                "browser",
            ),

            (
                IntentType.SYSTEM,
                r"\b(shutdown|restart|sleep|hibernate|lock|logout)\b",
                "system",
            ),

            (
                IntentType.SEARCH,
                r"\b(search|find|look up)\b",
                "search",
            ),

            (
                IntentType.WORKFLOW,
                r"\b(start workflow|run workflow|execute workflow)\b",
                "workflow",
            ),

            (
                IntentType.QUESTION,
                r"^(what|why|when|where|who|how)\b",
                "question",
            ),

        ]

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def route(
        self,
        message: str,
    ) -> Intent:
        """
        Determine the intent of the message.
        """

        text = message.strip().lower()

        if not text:

            return Intent(

                intent=IntentType.UNKNOWN,

                confidence=0.0,

            )

        for intent_type, pattern, category in self._patterns:

            if re.search(pattern, text):

                return Intent(

                    intent=intent_type,

                    confidence=0.95,

                    category=category,

                )

        if text.endswith("?"):

            return Intent(

                intent=IntentType.QUESTION,

                confidence=0.90,

                category="question",

            )

        if len(text.split()) <= 3:

            return Intent(

                intent=IntentType.CHAT,

                confidence=0.75,

                category="conversation",

            )

        return Intent(

            intent=IntentType.ACTION,

            confidence=0.60,

            category="general",

        )

    # ---------------------------------------------------------

    def classify(
        self,
        message: str,
    ) -> Intent:

        return self.route(message)

    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {

            "healthy": True,

            "patterns": len(self._patterns),

        }

    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            "IntentRouter("

            f"patterns={len(self._patterns)}"

            ")"

        )