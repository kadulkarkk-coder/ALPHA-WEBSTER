"""Rule-based goal analysis for Webster planning."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .goal import Goal


@dataclass(slots=True)
class GoalAnalysis:
    category: str
    required_capabilities: tuple[str, ...]
    complexity: str
    estimated_tasks: int
    priority: int
    execution_strategy: str


class GoalAnalyzer:
    """Deterministically maps natural-language goals to real capabilities.

    This is intentionally kept in sync with IntentRouter.  The planner is a
    fallback for multi-step requests, not a second unrelated command parser.
    """

    _RULES = (
        (("activate vision", "enable vision", "turn on vision", "start vision"), "vision", ("vision_enable",)),
        (("deactivate vision", "disable vision", "turn off vision", "stop vision"), "vision", ("vision_disable",)),
        (("vision status", "vision state", "vision health", "visual mode status"), "vision", ("vision_status",)),
        (("can you see my screen", "see my screen", "look at my screen", "view my screen", "analyze my screen", "screenshot", "screen capture"), "vision", ("vision_screen",)),
        (("create folder", "make folder", "mkdir"), "filesystem", ("create_folder",)),
        (("create file", "new file", "make file"), "filesystem", ("create_file",)),
        (("write file", "save file"), "filesystem", ("write_file",)),
        (("read file", "open file", "view file"), "filesystem", ("read_file",)),
        (("rename file",), "filesystem", ("rename_file",)),
        (("move file", "relocate file"), "filesystem", ("move_file",)),
        (("copy file",), "filesystem", ("copy_file",)),
        (("delete file", "remove file", "delete folder", "remove folder"), "filesystem", ("delete_file",)),
        (("list directory", "list files", "show files", "list folder", "show folder", "open folder", "open directory"), "filesystem", ("list_directory",)),
        (("search files", "find files", "find all", "search folder"), "filesystem", ("search_files",)),
        (("open url", "open website", "open http", "open https", "go to", "visit", "open chatgpt", "open google"), "internet", ("open_url",)),
        (("refresh", "reload"), "internet", ("refresh",)),
        (("back", "go back"), "internet", ("browser_back",)),
        (("shutdown", "restart", "sleep", "hibernate", "lock", "logout"), "system", ("power",)),
    )

    _FILE_EXTENSION = re.compile(
        r"\b(?:delete|remove|read|view|show|open)\s+(?:the\s+)?(?:file\s+)?[\w .()\-]+\.[a-z0-9]{1,8}\b",
        re.IGNORECASE,
    )

    def analyze(self, goal: Goal) -> GoalAnalysis:
        goal.validate()
        text = goal.objective.lower().strip()

        for patterns, category, capabilities in self._RULES:
            if any(pattern in text for pattern in patterns):
                return GoalAnalysis(
                    category=category,
                    required_capabilities=capabilities,
                    complexity="low" if len(capabilities) == 1 else "medium",
                    estimated_tasks=len(capabilities),
                    priority=goal.priority,
                    execution_strategy="sequential",
                )

        if self._FILE_EXTENSION.search(text):
            capability = "delete_file" if re.search(r"\b(delete|remove)\b", text) else "read_file"
            return GoalAnalysis("filesystem", (capability,), "low", 1, goal.priority, "sequential")

        if any(word in text for word in ("file", "files", "folder", "directory", "document")):
            return GoalAnalysis(
                category="filesystem",
                required_capabilities=("list_directory",),
                complexity="low",
                estimated_tasks=1,
                priority=goal.priority,
                execution_strategy="sequential",
            )

        if any(word in text for word in ("browser", "website", "web", "url")):
            return GoalAnalysis(
                category="internet",
                required_capabilities=("open_url",),
                complexity="low",
                estimated_tasks=1,
                priority=goal.priority,
                execution_strategy="sequential",
            )

        return GoalAnalysis(
            category="general",
            required_capabilities=(),
            complexity="low",
            estimated_tasks=0,
            priority=goal.priority,
            execution_strategy="none",
        )
