"""Rule-based goal analysis for Webster planning."""

from __future__ import annotations

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
    """Deterministically maps natural-language goals to real capabilities."""

    _RULES = (
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
        (("back", "go back"), "internet", ("back",)),
        (("shutdown", "restart", "sleep", "hibernate", "lock", "logout"), "system", ("power",)),
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
