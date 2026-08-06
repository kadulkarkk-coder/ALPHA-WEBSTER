"""core.planning.analyzer

Rule-based GoalAnalyzer and GoalAnalysis result model.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

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
    """
    Rule-based analyzer that inspects a Goal and returns a GoalAnalysis.
    """

    def analyze(self, goal: Goal) -> GoalAnalysis:
        goal.validate()

        text = goal.objective.lower()

        rules = [
            (
                ["create project", "setup project", "initialize project"],
                "development",
                ("create_folder", "write_file", "open_folder", "open_url"),
                "medium",
                4,
                "staged",
            ),
            (
                ["create folder", "make folder", "mkdir"],
                "filesystem",
                ("create_folder",),
                "low",
                1,
                "sequential",
            ),
            (
                ["create file", "new file", "write file", "save file"],
                "filesystem",
                ("create_folder", "write_file"),
                "low",
                1,
                "sequential",
            ),
            (
                ["read file", "open file", "view file"],
                "filesystem",
                ("read_file",),
                "low",
                1,
                "sequential",
            ),
            (
                ["rename file", "move file", "relocate file"],
                "filesystem",
                ("rename", "move"),
                "low",
                1,
                "sequential",
            ),
            (
                ["delete file", "remove file", "delete folder", "remove folder"],
                "filesystem",
                ("delete",),
                "low",
                1,
                "sequential",
            ),
            (
                ["list directory", "list files", "show files", "list folder"],
                "filesystem",
                ("list_directory",),
                "low",
                1,
                "sequential",
            ),
            (
                ["search files", "find files", "search folder"],
                "filesystem",
                ("search",),
                "low",
                1,
                "sequential",
            ),
            (
                ["open url", "go to", "visit", "open website", "open chatgpt"],
                "internet",
                ("open_url",),
                "low",
                1,
                "sequential",
            ),
            (
                ["search for", "google", "search web", "web search"],
                "internet",
                ("web_search",),
                "low",
                1,
                "sequential",
            ),
            (
                ["refresh", "reload"],
                "internet",
                ("refresh",),
                "low",
                1,
                "sequential",
            ),
            (
                ["back", "forward", "close tab"],
                "internet",
                ("back", "forward", "close_tab"),
                "low",
                1,
                "sequential",
            ),
            (
                ["shutdown", "restart", "sleep", "hibernate", "lock", "logout"],
                "system",
                ("power",),
                "low",
                1,
                "sequential",
            ),
            (
                ["launch application", "open application", "start application", "launch app"],
                "system",
                ("launch_application",),
                "low",
                1,
                "sequential",
            ),
            (
                ["kill process", "terminate application", "close process"],
                "system",
                ("kill_process",),
                "low",
                1,
                "sequential",
            ),
        ]

        for patterns, category, caps, complexity, est, strategy in rules:
            if any(pattern in text for pattern in patterns):
                return GoalAnalysis(
                    category=category,
                    required_capabilities=caps,
                    complexity=complexity,
                    estimated_tasks=est,
                    priority=goal.priority,
                    execution_strategy=strategy,
                )

        if "file" in text or "folder" in text or "directory" in text:
            caps = ("create_folder", "write_file", "read_file", "list_directory")
            category = "filesystem"
            complexity = "low"
            est = 2
            strategy = "sequential"
        elif "browser" in text or "web" in text or "search" in text:
            caps = ("open_url", "web_search")
            category = "internet"
            complexity = "low"
            est = 2
            strategy = "sequential"
        elif any(word in text for word in ("shutdown", "restart", "sleep", "lock", "logout")):
            caps = ("power",)
            category = "system"
            complexity = "low"
            est = 1
            strategy = "sequential"
        else:
            caps = ("open_url",)
            category = "general"
            complexity = "low"
            est = 1
            strategy = "sequential"

        return GoalAnalysis(
            category=category,
            required_capabilities=caps,
            complexity=complexity,
            estimated_tasks=est,
            priority=goal.priority,
            execution_strategy=strategy,
        )
