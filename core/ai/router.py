"""
Webster Alpha

Intent Router
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class IntentType(Enum):
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
    """Rule-based intent router with explicit filesystem awareness."""

    def __init__(self) -> None:
        self._patterns: list[tuple[IntentType, str, str]] = [
            (
                IntentType.FILE,
                r"\b(create|make|delete|remove|rename|move|copy|read|write|save|list|show|find|search|open)\b.*\b(file|files|folder|folders|directory|directories|document|documents|python files|pdfs)\b",
                "filesystem",
            ),
            (
                IntentType.FILE,
                r"\b(file|files|folder|folders|directory|directories)\b.*\b(create|make|delete|remove|rename|move|copy|read|write|save|list|show|find|search|open)\b",
                "filesystem",
            ),
            (
                IntentType.BROWSER,
                r"\b(open|browse|visit|go to)\b",
                "browser",
            ),
            (
                IntentType.SYSTEM,
                r"\b(shutdown|restart|sleep|hibernate|lock|logout)\b",
                "system",
            ),
            (
                IntentType.SEARCH,
                r"\b(search|look up)\b",
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

    def route(self, message: str) -> Intent:
        text = message.strip().lower()
        if not text:
            return Intent(intent=IntentType.UNKNOWN, confidence=0.0)

        for intent_type, pattern, category in self._patterns:
            if re.search(pattern, text):
                if intent_type == IntentType.FILE:
                    action = self._file_action(text)
                elif intent_type == IntentType.BROWSER:
                    action = self._browser_action(text)
                else:
                    action = None
                return Intent(
                    intent=intent_type,
                    confidence=0.95,
                    action=action,
                    category=category,
                    metadata={"file_action": action} if action else None,
                )

        if text.endswith("?"):
            return Intent(intent=IntentType.QUESTION, confidence=0.90, category="question")

        if len(text.split()) <= 3:
            return Intent(intent=IntentType.CHAT, confidence=0.75, category="conversation")

        # Unknown natural-language requests should remain conversational until
        # a concrete capability is identified. This prevents empty plans from
        # reaching the strict plan validator.
        return Intent(intent=IntentType.ACTION, confidence=0.60, category="general")

    def _file_action(self, text: str) -> str | None:
        for action, words in (
            ("create_folder", ("create folder", "make folder", "mkdir")),
            ("create_file", ("create file", "new file", "make file")),
            ("write_file", ("write file", "save to file", "save file")),
            ("read_file", ("read file", "open file", "view file")),
            ("rename_file", ("rename file",)),
            ("move_file", ("move file", "relocate file")),
            ("copy_file", ("copy file",)),
            ("delete_file", ("delete file", "remove file", "delete folder", "remove folder")),
            ("list_directory", ("list directory", "list files", "show files", "list folder", "show folder", "open folder", "open directory")),
            ("search_files", ("search files", "find files", "find all", "search folder")),
        ):
            if any(word in text for word in words):
                return action
        return None

    def _browser_action(self, text: str) -> str | None:
        if re.search(r"\b(refresh|reload)\b", text):
            return "refresh"
        if re.search(r"\b(back|go back)\b", text):
            return "back"
        return "open_url"

    def classify(self, message: str) -> Intent:
        return self.route(message)

    def health(self) -> dict:
        return {"healthy": True, "patterns": len(self._patterns)}

    def __repr__(self) -> str:
        return f"IntentRouter(patterns={len(self._patterns)})"
