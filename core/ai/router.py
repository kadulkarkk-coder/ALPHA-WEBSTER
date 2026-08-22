"""Webster Alpha - deterministic intent routing."""

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
    """Fast deterministic router for commands that should use real tools.

    Routing deliberately happens before the language model.  Natural language
    commands such as ``delete read.txt`` and ``can you see my screen`` must not
    fall through to a text-only provider when Webster has a real capability for
    them.
    """

    _FILE_WORDS = r"file|files|folder|folders|directory|directories|document|documents"

    def __init__(self) -> None:
        self._patterns = [
            # Vision commands must be checked before generic question/action rules.
            (IntentType.SYSTEM, r"\b(activate|enable|turn on|start)\s+(vision|visual mode|screen vision)\b", "vision"),
            (IntentType.SYSTEM, r"\b(deactivate|disable|turn off|stop)\s+(vision|visual mode|screen vision)\b", "vision"),
            (IntentType.SYSTEM, r"\b(vision|visual mode)\s+(status|state|health)\b", "vision"),
            (IntentType.SYSTEM, r"\b(can you|could you|please)\s+(see|look at|view|analyze)\s+(my\s+)?(screen|desktop)\b", "vision"),
            (IntentType.SYSTEM, r"\b(see|look at|view|analyze)\s+(my\s+)?(screen|desktop)\b", "vision"),
            (IntentType.SYSTEM, r"\b(screenshot|screen capture|capture my screen)\b", "vision"),

            (IntentType.FILE, rf"\b(create|make|delete|remove|rename|move|copy|read|write|save|list|show|find|search|open)\b.*\b({ _FILE_WORDS }|python files|pdfs)\b", "filesystem"),
            (IntentType.FILE, rf"\b({ _FILE_WORDS })\b.*\b(create|make|delete|remove|rename|move|copy|read|write|save|list|show|find|search|open)\b", "filesystem"),
            # Natural commands where the object is a filename rather than the word 'file'.
            (IntentType.FILE, r"\b(delete|remove)\s+(?:the\s+)?(?:file\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", "filesystem"),
            (IntentType.FILE, r"\b(read|view|show|open)\s+(?:the\s+)?(?:file\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", "filesystem"),
            (IntentType.FILE, r"\b(create|make)\s+(?:a\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", "filesystem"),

            (IntentType.BROWSER, r"\b(open|browse|visit|go to)\b", "browser"),
            (IntentType.SYSTEM, r"\b(shutdown|restart|sleep|hibernate|lock|logout)\b", "system"),
            (IntentType.SEARCH, r"\b(search|look up)\b", "search"),
            (IntentType.WORKFLOW, r"\b(start workflow|run workflow|execute workflow)\b", "workflow"),
            (IntentType.QUESTION, r"^(what|why|when|where|who|how)\b", "question"),
        ]

    def route(self, message: str) -> Intent:
        text = " ".join(str(message).strip().split()).lower()
        if not text:
            return Intent(IntentType.UNKNOWN, 0.0)

        for intent_type, pattern, category in self._patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if category == "vision":
                    action = self._vision_action(text)
                elif intent_type == IntentType.FILE:
                    action = self._file_action(text)
                elif intent_type == IntentType.BROWSER:
                    action = self._browser_action(text)
                elif intent_type == IntentType.SYSTEM:
                    action = "power"
                elif intent_type == IntentType.SEARCH:
                    action = "search_files" if "file" in text else None
                else:
                    action = None
                return Intent(intent_type, 0.98, action, category, {"action": action} if action else None)

        if text.endswith("?"):
            return Intent(IntentType.QUESTION, 0.90, category="question")
        if len(text.split()) <= 3:
            return Intent(IntentType.CHAT, 0.75, category="conversation")
        return Intent(IntentType.ACTION, 0.60, category="general")

    def _vision_action(self, text: str) -> str:
        if re.search(r"\b(deactivate|disable|turn off|stop)\b", text):
            return "vision_disable"
        if re.search(r"\b(status|state|health)\b", text):
            return "vision_status"
        if re.search(r"\b(see|look at|view|analyze|screenshot|capture)\b", text):
            return "vision_screen"
        return "vision_enable"

    def _file_action(self, text: str) -> str | None:
        rules = (
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
        )
        for action, phrases in rules:
            if any(phrase in text for phrase in phrases):
                return action

        if re.search(r"\b(delete|remove)\s+(?:the\s+)?(?:file\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", text):
            return "delete_file"
        if re.search(r"\b(read|view|show|open)\s+(?:the\s+)?(?:file\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", text):
            return "read_file"
        if re.search(r"\b(create|make)\s+(?:a\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b", text):
            return "create_file"
        return None

    def _browser_action(self, text: str) -> str:
        if re.search(r"\b(refresh|reload)\b", text):
            return "refresh"
        if re.search(r"\b(back|go back)\b", text):
            return "browser_back"
        return "open_url"

    def classify(self, message: str) -> Intent:
        return self.route(message)

    def health(self) -> dict:
        return {"healthy": True, "patterns": len(self._patterns)}

    def __repr__(self) -> str:
        return f"IntentRouter(patterns={len(self._patterns)})"
